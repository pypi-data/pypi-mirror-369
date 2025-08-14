"""Claude SDK service orchestration for business logic."""

from collections.abc import AsyncIterator
from typing import Any

import structlog
from claude_code_sdk import ClaudeCodeOptions

from ccproxy.auth.manager import AuthManager
from ccproxy.claude_sdk.client import ClaudeSDKClient
from ccproxy.claude_sdk.converter import MessageConverter
from ccproxy.claude_sdk.exceptions import StreamTimeoutError
from ccproxy.claude_sdk.manager import SessionManager
from ccproxy.claude_sdk.options import OptionsHandler
from ccproxy.claude_sdk.streaming import ClaudeStreamProcessor
from ccproxy.config.claude import SDKMessageMode
from ccproxy.config.settings import Settings
from ccproxy.core.errors import (
    ClaudeProxyError,
    ServiceUnavailableError,
)
from ccproxy.models import claude_sdk as sdk_models
from ccproxy.models.claude_sdk import SDKMessage, create_sdk_message
from ccproxy.models.messages import MessageResponse
from ccproxy.observability.context import RequestContext
from ccproxy.observability.metrics import PrometheusMetrics
from ccproxy.utils.model_mapping import map_model_to_claude
from ccproxy.utils.simple_request_logger import write_request_log


logger = structlog.get_logger(__name__)


class ClaudeSDKService:
    """
    Service layer for Claude SDK operations orchestration.

    This class handles business logic coordination between the pure SDK client,
    authentication, metrics, and format conversion while maintaining clean
    separation of concerns.
    """

    def __init__(
        self,
        sdk_client: ClaudeSDKClient | None = None,
        auth_manager: AuthManager | None = None,
        metrics: PrometheusMetrics | None = None,
        settings: Settings | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        """
        Initialize Claude SDK service.

        Args:
            sdk_client: Claude SDK client instance
            auth_manager: Authentication manager (optional)
            metrics: Prometheus metrics instance (optional)
            settings: Application settings (optional)
            session_manager: Session manager for dependency injection (optional)
        """
        self.sdk_client = sdk_client or ClaudeSDKClient(
            settings=settings, session_manager=session_manager
        )
        self.auth_manager = auth_manager
        self.metrics = metrics
        self.settings = settings
        self.message_converter = MessageConverter()
        self.options_handler = OptionsHandler(settings=settings)
        self.stream_processor = ClaudeStreamProcessor(
            message_converter=self.message_converter,
            metrics=self.metrics,
        )

    def _convert_messages_to_sdk_message(
        self, messages: list[dict[str, Any]], session_id: str | None = None
    ) -> "SDKMessage":
        """Convert list of Anthropic messages to single SDKMessage.

        Takes the last user message from the list and converts it to SDKMessage format.

        Args:
            messages: List of Anthropic API messages
            session_id: Optional session ID for conversation continuity

        Returns:
            SDKMessage ready to send to Claude SDK
        """
        # Find the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg
                break

        if not last_user_message:
            raise ClaudeProxyError(
                message="No user message found in messages list",
                error_type="invalid_request_error",
                status_code=400,
            )

        # Extract text content from the message
        content = last_user_message.get("content", "")
        if isinstance(content, list):
            # Extract text from content blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)
        elif not isinstance(content, str):
            content = str(content)

        return create_sdk_message(content=content, session_id=session_id)

    async def _capture_session_metadata(
        self,
        ctx: RequestContext,
        session_id: str | None,
        options: "ClaudeCodeOptions",
    ) -> None:
        """Capture session metadata for access logging.

        Args:
            ctx: Request context to add metadata to
            session_id: Optional session ID
            options: Claude Code options
        """
        if (
            session_id
            and hasattr(self.sdk_client, "_session_manager")
            and self.sdk_client._session_manager
        ):
            try:
                session_client = (
                    await self.sdk_client._session_manager.get_session_client(
                        session_id, options
                    )
                )
                if session_client:
                    # Determine if session pool is enabled
                    session_pool_enabled = (
                        hasattr(self.sdk_client._session_manager, "session_pool")
                        and self.sdk_client._session_manager.session_pool is not None
                        and hasattr(
                            self.sdk_client._session_manager.session_pool, "config"
                        )
                        and self.sdk_client._session_manager.session_pool.config.enabled
                    )

                    # Add session metadata to context
                    ctx.add_metadata(
                        session_type="session_pool"
                        if session_pool_enabled
                        else "direct",
                        session_status=session_client.status.value,
                        session_age_seconds=session_client.metrics.age_seconds,
                        session_message_count=session_client.metrics.message_count,
                        session_client_id=session_client.client_id,
                        session_pool_enabled=session_pool_enabled,
                        session_idle_seconds=session_client.metrics.idle_seconds,
                        session_error_count=session_client.metrics.error_count,
                        session_is_new=session_client.is_newly_created,
                    )
            except Exception as e:
                logger.warning(
                    "failed_to_capture_session_metadata",
                    session_id=session_id,
                    error=str(e),
                )
        else:
            # Add basic session metadata for direct connections (no session pool)
            ctx.add_metadata(
                session_type="direct",
                session_pool_enabled=False,
                session_is_new=True,  # Direct connections are always new
            )

    async def create_completion(
        self,
        request_context: RequestContext,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> MessageResponse | AsyncIterator[dict[str, Any]]:
        """
        Create a completion using Claude SDK with business logic orchestration.

        Args:
            messages: List of messages in Anthropic format
            model: The model to use
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            stream: Whether to stream responses
            session_id: Optional session ID for Claude SDK integration
            request_context: Existing request context to use instead of creating new one
            **kwargs: Additional arguments

        Returns:
            Response dict or async iterator of response chunks if streaming

        Raises:
            ClaudeProxyError: If request fails
            ServiceUnavailableError: If service is unavailable
        """

        # Extract system message and create options
        system_message = self.options_handler.extract_system_message(messages)

        # Map model to Claude model
        model = map_model_to_claude(model)

        options = self.options_handler.create_options(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message,
            session_id=session_id,
            **kwargs,
        )

        # Messages will be converted to SDK format in the client layer

        # Use existing context, but update metadata for this service (preserve original service_type)
        ctx = request_context
        metadata = {
            "endpoint": "messages",
            "model": model,
            "streaming": stream,
        }
        if session_id:
            metadata["session_id"] = session_id
        ctx.add_metadata(**metadata)
        # Use existing request ID from context
        request_id = ctx.request_id

        try:
            # Log SDK request parameters
            timestamp = ctx.get_log_timestamp_prefix() if ctx else None
            await self._log_sdk_request(
                request_id, messages, options, model, stream, session_id, timestamp
            )

            if stream:
                # For streaming, return the async iterator directly
                # Access logging will be handled by the stream processor when ResultMessage is received
                return self._stream_completion(
                    ctx, messages, options, model, session_id, timestamp
                )
            else:
                result = await self._complete_non_streaming(
                    ctx, messages, options, model, session_id, timestamp
                )
                return result
        except (ClaudeProxyError, ServiceUnavailableError) as e:
            # Add error info to context for automatic access logging
            ctx.add_metadata(error_message=str(e), error_type=type(e).__name__)
            raise

    async def _complete_non_streaming(
        self,
        ctx: RequestContext,
        messages: list[dict[str, Any]],
        options: "ClaudeCodeOptions",
        model: str,
        session_id: str | None = None,
        timestamp: str | None = None,
    ) -> MessageResponse:
        """
        Complete a non-streaming request with business logic.

        Args:
            prompt: The formatted prompt
            options: Claude SDK options
            model: The model being used

        Returns:
            Response in Anthropic format

        Raises:
            ClaudeProxyError: If completion fails
        """
        request_id = ctx.request_id
        logger.debug("claude_sdk_completion_start", request_id=request_id)

        # Convert messages to single SDKMessage
        sdk_message = self._convert_messages_to_sdk_message(messages, session_id)

        # Get stream handle
        stream_handle = await self.sdk_client.query_completion(
            sdk_message, options, request_id, session_id
        )

        # Capture session metadata for access logging
        await self._capture_session_metadata(ctx, session_id, options)

        # Create a listener and collect all messages
        sdk_messages = []
        async for m in stream_handle.create_listener():
            sdk_messages.append(m)

        result_message = next(
            (m for m in sdk_messages if isinstance(m, sdk_models.ResultMessage)), None
        )
        assistant_message = next(
            (m for m in sdk_messages if isinstance(m, sdk_models.AssistantMessage)),
            None,
        )

        if result_message is None:
            raise ClaudeProxyError(
                message="No result message received from Claude SDK",
                error_type="internal_server_error",
                status_code=500,
            )

        if assistant_message is None:
            raise ClaudeProxyError(
                message="No assistant response received from Claude SDK",
                error_type="internal_server_error",
                status_code=500,
            )

        logger.debug("claude_sdk_completion_received")
        mode = (
            self.settings.claude.sdk_message_mode
            if self.settings
            else SDKMessageMode.FORWARD
        )
        pretty_format = self.settings.claude.pretty_format if self.settings else True

        response = self.message_converter.convert_to_anthropic_response(
            assistant_message, result_message, model, mode, pretty_format
        )

        # Add other message types to the content block
        all_messages = [
            m
            for m in sdk_messages
            if not isinstance(m, sdk_models.AssistantMessage | sdk_models.ResultMessage)
        ]

        if mode != SDKMessageMode.IGNORE and response.content:
            for message in all_messages:
                if isinstance(message, sdk_models.SystemMessage):
                    content_block = self.message_converter._create_sdk_content_block(
                        sdk_object=message,
                        mode=mode,
                        pretty_format=pretty_format,
                        xml_tag="system_message",
                        forward_converter=lambda obj: {
                            "type": "system_message",
                            "text": obj.model_dump_json(),
                        },
                    )
                    if content_block:
                        # Only validate as SDKMessageMode if it's a system_message type
                        if content_block.get("type") == "system_message":
                            response.content.append(
                                sdk_models.SDKMessageMode.model_validate(content_block)
                            )
                        else:
                            # For other types (like text blocks in FORMATTED mode), create appropriate content block
                            if content_block.get("type") == "text":
                                response.content.append(
                                    sdk_models.TextBlock.model_validate(content_block)
                                )
                            else:
                                # Fallback for other content block types
                                logger.warning(
                                    "unknown_content_block_type",
                                    content_block_type=content_block.get("type"),
                                )
                elif isinstance(message, sdk_models.UserMessage):
                    for block in message.content:
                        if isinstance(block, sdk_models.ToolResultBlock):
                            response.content.append(block)

        cost_usd = result_message.total_cost_usd
        usage = result_message.usage_model

        # if cost_usd is not None and response.usage:
        #     response.usage.cost_usd = cost_usd

        logger.debug(
            "claude_sdk_completion_completed",
            model=model,
            tokens_input=usage.input_tokens,
            tokens_output=usage.output_tokens,
            cache_read_tokens=usage.cache_read_input_tokens,
            cache_write_tokens=usage.cache_creation_input_tokens,
            cost_usd=cost_usd,
            request_id=request_id,
        )

        ctx.add_metadata(
            status_code=200,
            tokens_input=usage.input_tokens,
            tokens_output=usage.output_tokens,
            cache_read_tokens=usage.cache_read_input_tokens,
            cache_write_tokens=usage.cache_creation_input_tokens,
            cost_usd=cost_usd,
            session_id=result_message.session_id,
            num_turns=result_message.num_turns,
        )
        # Add success status to context for automatic access logging
        ctx.add_metadata(status_code=200)

        # Log SDK response
        if request_id:
            await self._log_sdk_response(request_id, response, timestamp)

        return response

    async def _stream_completion(
        self,
        ctx: RequestContext,
        messages: list[dict[str, Any]],
        options: "ClaudeCodeOptions",
        model: str,
        session_id: str | None = None,
        timestamp: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Stream completion responses with business logic.

        Args:
            prompt: The formatted prompt
            options: Claude SDK options
            model: The model being used
            ctx: Optional request context for metrics

        Yields:
            Response chunks in Anthropic format
        """
        request_id = ctx.request_id
        sdk_message_mode = (
            self.settings.claude.sdk_message_mode
            if self.settings
            else SDKMessageMode.FORWARD
        )
        pretty_format = self.settings.claude.pretty_format if self.settings else True

        # Convert messages to single SDKMessage
        sdk_message = self._convert_messages_to_sdk_message(messages, session_id)

        # Get stream handle instead of direct iterator
        stream_handle = await self.sdk_client.query_completion(
            sdk_message, options, request_id, session_id
        )

        # Store handle in session client if available for cleanup
        if (
            session_id
            and hasattr(self.sdk_client, "_session_manager")
            and self.sdk_client._session_manager
        ):
            try:
                session_client = (
                    await self.sdk_client._session_manager.get_session_client(
                        session_id, options
                    )
                )
                if session_client:
                    session_client.active_stream_handle = stream_handle
            except Exception as e:
                logger.warning(
                    "failed_to_store_stream_handle",
                    session_id=session_id,
                    error=str(e),
                )

        # Capture session metadata for access logging
        await self._capture_session_metadata(ctx, session_id, options)

        # Create a listener for this stream
        sdk_stream = stream_handle.create_listener()

        try:
            async for chunk in self.stream_processor.process_stream(
                sdk_stream=sdk_stream,
                model=model,
                request_id=request_id,
                ctx=ctx,
                sdk_message_mode=sdk_message_mode,
                pretty_format=pretty_format,
            ):
                # Log streaming chunk
                if request_id:
                    await self._log_sdk_streaming_chunk(request_id, chunk, timestamp)
                yield chunk
        except GeneratorExit:
            # Client disconnected - log and re-raise to propagate to create_listener()
            logger.info(
                "claude_sdk_service_client_disconnected",
                request_id=request_id,
                session_id=session_id,
                message="Client disconnected from SDK service stream, propagating to stream handle",
            )
            # CRITICAL: Re-raise GeneratorExit to trigger interrupt in create_listener()
            raise
        except StreamTimeoutError as e:
            # Send error events to the client
            logger.error(
                "stream_timeout_error",
                message=str(e),
                session_id=e.session_id,
                timeout_seconds=e.timeout_seconds,
                request_id=request_id,
            )

            # Create a unique message ID for the error response
            from uuid import uuid4

            error_message_id = f"msg_error_{uuid4()}"

            # Yield message_start event
            yield {
                "type": "message_start",
                "message": {
                    "id": error_message_id,
                    "type": "message",
                    "role": "assistant",
                    "model": model,
                    "content": [],
                    "stop_reason": "error",
                    "stop_sequence": None,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            }

            # Yield content_block_start for error message
            yield {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "text", "text": ""},
            }

            # Yield error text delta
            error_text = f"Error: {e}"
            yield {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": error_text},
            }

            # Yield content_block_stop
            yield {
                "type": "content_block_stop",
                "index": 0,
            }

            # Yield message_delta with stop reason
            yield {
                "type": "message_delta",
                "delta": {"stop_reason": "error", "stop_sequence": None},
                "usage": {"output_tokens": len(error_text.split())},
            }

            # Yield message_stop
            yield {
                "type": "message_stop",
            }

            # Update context with error status
            ctx.add_metadata(
                status_code=504,  # Gateway Timeout
                error_message=str(e),
                error_type="stream_timeout",
                session_id=e.session_id,
            )

    async def _log_sdk_request(
        self,
        request_id: str,
        messages: list[dict[str, Any]],
        options: "ClaudeCodeOptions",
        model: str,
        stream: bool,
        session_id: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        """Log SDK input parameters as JSON dump.

        Args:
            request_id: Request identifier
            messages: List of Anthropic API messages
            options: Claude SDK options
            model: The model being used
            stream: Whether streaming is enabled
            session_id: Optional session ID for Claude SDK integration
            timestamp: Optional timestamp prefix
        """
        # timestamp is already provided from context, no need for fallback

        # JSON dump of the parameters passed to SDK completion
        sdk_request_data = {
            "messages": messages,
            "options": options,
            "stream": stream,
            "request_id": request_id,
        }
        if session_id:
            sdk_request_data["session_id"] = session_id

        await write_request_log(
            request_id=request_id,
            log_type="sdk_request",
            data=sdk_request_data,
            timestamp=timestamp,
        )

    async def _log_sdk_response(
        self,
        request_id: str,
        result: Any,
        timestamp: str | None = None,
    ) -> None:
        """Log SDK response result as JSON dump.

        Args:
            request_id: Request identifier
            result: The result from _complete_non_streaming
            timestamp: Optional timestamp prefix
        """
        # timestamp is already provided from context, no need for fallback

        # JSON dump of the result from _complete_non_streaming
        sdk_response_data = {
            "result": result.model_dump()
            if hasattr(result, "model_dump")
            else str(result),
        }

        await write_request_log(
            request_id=request_id,
            log_type="sdk_response",
            data=sdk_response_data,
            timestamp=timestamp,
        )

    async def _log_sdk_streaming_chunk(
        self,
        request_id: str,
        chunk: dict[str, Any],
        timestamp: str | None = None,
    ) -> None:
        """Log streaming chunk as JSON dump.

        Args:
            request_id: Request identifier
            chunk: The streaming chunk from process_stream
            timestamp: Optional timestamp prefix
        """
        # timestamp is already provided from context, no need for fallback

        # Append streaming chunk as JSON to raw file
        import json

        from ccproxy.utils.simple_request_logger import append_streaming_log

        chunk_data = json.dumps(chunk, default=str) + "\n"
        await append_streaming_log(
            request_id=request_id,
            log_type="sdk_streaming",
            data=chunk_data.encode("utf-8"),
            timestamp=timestamp,
        )

    async def validate_health(self) -> bool:
        """
        Validate that the service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            return await self.sdk_client.validate_health()
        except Exception as e:
            logger.error(
                "health_check_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            return False

    async def interrupt_session(self, session_id: str) -> bool:
        """Interrupt a Claude session due to client disconnection.

        Args:
            session_id: The session ID to interrupt

        Returns:
            True if session was found and interrupted, False otherwise
        """
        return await self.sdk_client.interrupt_session(session_id)

    async def close(self) -> None:
        """Close the service and cleanup resources."""
        await self.sdk_client.close()

    async def __aenter__(self) -> "ClaudeSDKService":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
