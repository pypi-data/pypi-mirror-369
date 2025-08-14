"""OpenAI streaming response formatting.

This module provides Server-Sent Events (SSE) formatting for OpenAI-compatible
streaming responses.
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from typing import Any, Literal

import structlog

from .models import (
    generate_openai_response_id,
)


logger = structlog.get_logger(__name__)


class OpenAISSEFormatter:
    """Formats streaming responses to match OpenAI's SSE format."""

    @staticmethod
    def format_data_event(data: dict[str, Any]) -> str:
        """Format a data event for OpenAI-compatible Server-Sent Events.

        Args:
            data: Event data dictionary

        Returns:
            Formatted SSE string
        """
        json_data = json.dumps(data, separators=(",", ":"))
        return f"data: {json_data}\n\n"

    @staticmethod
    def format_first_chunk(
        message_id: str, model: str, created: int, role: str = "assistant"
    ) -> str:
        """Format the first chunk with role and basic metadata.

        Args:
            message_id: Unique identifier for the completion
            model: Model name being used
            created: Unix timestamp when the completion was created
            role: Role of the assistant

        Returns:
            Formatted SSE string
        """
        data = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": role},
                    "logprobs": None,
                    "finish_reason": None,
                }
            ],
        }
        return OpenAISSEFormatter.format_data_event(data)

    @staticmethod
    def format_content_chunk(
        message_id: str, model: str, created: int, content: str, choice_index: int = 0
    ) -> str:
        """Format a content chunk with text delta.

        Args:
            message_id: Unique identifier for the completion
            model: Model name being used
            created: Unix timestamp when the completion was created
            content: Text content to include in the delta
            choice_index: Index of the choice (usually 0)

        Returns:
            Formatted SSE string
        """
        data = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": choice_index,
                    "delta": {"content": content},
                    "logprobs": None,
                    "finish_reason": None,
                }
            ],
        }
        return OpenAISSEFormatter.format_data_event(data)

    @staticmethod
    def format_tool_call_chunk(
        message_id: str,
        model: str,
        created: int,
        tool_call_id: str,
        function_name: str | None = None,
        function_arguments: str | None = None,
        tool_call_index: int = 0,
        choice_index: int = 0,
    ) -> str:
        """Format a tool call chunk.

        Args:
            message_id: Unique identifier for the completion
            model: Model name being used
            created: Unix timestamp when the completion was created
            tool_call_id: ID of the tool call
            function_name: Name of the function being called
            function_arguments: Arguments for the function
            tool_call_index: Index of the tool call
            choice_index: Index of the choice (usually 0)

        Returns:
            Formatted SSE string
        """
        tool_call: dict[str, Any] = {
            "index": tool_call_index,
            "id": tool_call_id,
            "type": "function",
            "function": {},
        }

        if function_name is not None:
            tool_call["function"]["name"] = function_name

        if function_arguments is not None:
            tool_call["function"]["arguments"] = function_arguments

        data = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": choice_index,
                    "delta": {"tool_calls": [tool_call]},
                    "logprobs": None,
                    "finish_reason": None,
                }
            ],
        }
        return OpenAISSEFormatter.format_data_event(data)

    @staticmethod
    def format_final_chunk(
        message_id: str,
        model: str,
        created: int,
        finish_reason: str = "stop",
        choice_index: int = 0,
        usage: dict[str, int] | None = None,
    ) -> str:
        """Format the final chunk with finish_reason.

        Args:
            message_id: Unique identifier for the completion
            model: Model name being used
            created: Unix timestamp when the completion was created
            finish_reason: Reason for completion (stop, length, tool_calls, etc.)
            choice_index: Index of the choice (usually 0)
            usage: Optional usage information to include

        Returns:
            Formatted SSE string
        """
        data = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": choice_index,
                    "delta": {},
                    "logprobs": None,
                    "finish_reason": finish_reason,
                }
            ],
        }

        # Add usage if provided
        if usage:
            data["usage"] = usage

        return OpenAISSEFormatter.format_data_event(data)

    @staticmethod
    def format_error_chunk(
        message_id: str, model: str, created: int, error_type: str, error_message: str
    ) -> str:
        """Format an error chunk.

        Args:
            message_id: Unique identifier for the completion
            model: Model name being used
            created: Unix timestamp when the completion was created
            error_type: Type of error
            error_message: Error message

        Returns:
            Formatted SSE string
        """
        data = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {"index": 0, "delta": {}, "logprobs": None, "finish_reason": "error"}
            ],
            "error": {"type": error_type, "message": error_message},
        }
        return OpenAISSEFormatter.format_data_event(data)

    @staticmethod
    def format_done() -> str:
        """Format the final DONE event.

        Returns:
            Formatted SSE termination string
        """
        return "data: [DONE]\n\n"


class OpenAIStreamProcessor:
    """Processes Anthropic/Claude streaming responses into OpenAI format."""

    def __init__(
        self,
        message_id: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        created: int | None = None,
        enable_usage: bool = True,
        enable_tool_calls: bool = True,
        output_format: Literal["sse", "dict"] = "sse",
    ):
        """Initialize the stream processor.

        Args:
            message_id: Response ID, generated if not provided
            model: Model name for responses
            created: Creation timestamp, current time if not provided
            enable_usage: Whether to include usage information
            enable_tool_calls: Whether to process tool calls
            output_format: Output format - "sse" for Server-Sent Events strings, "dict" for dict objects
        """
        self.message_id = message_id or generate_openai_response_id()
        self.model = model
        self.created = created or int(time.time())
        self.enable_usage = enable_usage
        self.enable_tool_calls = enable_tool_calls
        self.output_format = output_format
        self.formatter = OpenAISSEFormatter()

        # State tracking
        self.role_sent = False
        self.accumulated_content = ""
        self.tool_calls: dict[str, dict[str, Any]] = {}
        self.usage_info: dict[str, int] | None = None
        # Thinking block tracking
        self.current_thinking_text = ""
        self.current_thinking_signature: str | None = None
        self.thinking_block_active = False

    async def process_stream(
        self, claude_stream: AsyncIterator[dict[str, Any]]
    ) -> AsyncIterator[str | dict[str, Any]]:
        """Process a Claude/Anthropic stream into OpenAI format.

        Args:
            claude_stream: Async iterator of Claude response chunks

        Yields:
            OpenAI-formatted SSE strings or dict objects based on output_format
        """
        try:
            chunk_count = 0
            processed_count = 0
            async for chunk in claude_stream:
                chunk_count += 1
                logger.debug(
                    "openai_stream_chunk_received",
                    chunk_count=chunk_count,
                    chunk_type=chunk.get("type"),
                    chunk=chunk,
                )
                async for sse_chunk in self._process_chunk(chunk):
                    processed_count += 1
                    logger.debug(
                        "openai_stream_chunk_processed",
                        processed_count=processed_count,
                        sse_chunk=sse_chunk,
                    )
                    yield sse_chunk

            logger.debug(
                "openai_stream_complete",
                total_chunks=chunk_count,
                processed_chunks=processed_count,
                usage_info=self.usage_info,
            )

            # Send final chunk
            if self.usage_info and self.enable_usage:
                yield self._format_chunk_output(
                    finish_reason="stop",
                    usage=self.usage_info,
                )
            else:
                yield self._format_chunk_output(finish_reason="stop")

            # Send DONE event (only for SSE format)
            if self.output_format == "sse":
                yield self.formatter.format_done()

        except Exception as e:
            # Send error chunk
            if self.output_format == "sse":
                yield self.formatter.format_error_chunk(
                    self.message_id, self.model, self.created, "error", str(e)
                )
                yield self.formatter.format_done()
            else:
                # Dict format error
                yield self._create_chunk_dict(finish_reason="error")

    async def _process_chunk(
        self, chunk: dict[str, Any]
    ) -> AsyncIterator[str | dict[str, Any]]:
        """Process a single chunk from the Claude stream.

        Args:
            chunk: Claude response chunk

        Yields:
            OpenAI-formatted SSE strings or dict objects based on output_format
        """
        # Handle both Claude SDK and standard Anthropic API formats:
        # Claude SDK format: {"event": "...", "data": {"type": "..."}}
        # Anthropic API format: {"type": "...", ...}
        event_type = chunk.get("event")
        if event_type:
            # Claude SDK format
            chunk_data = chunk.get("data", {})
            chunk_type = chunk_data.get("type")
        else:
            # Standard Anthropic API format
            chunk_data = chunk
            chunk_type = chunk.get("type")

        if chunk_type == "message_start":
            # Send initial role chunk
            if not self.role_sent:
                yield self._format_chunk_output(delta={"role": "assistant"})
                self.role_sent = True

        elif chunk_type == "content_block_start":
            block = chunk_data.get("content_block", {})
            if block.get("type") == "thinking":
                # Start of thinking block
                self.thinking_block_active = True
                self.current_thinking_text = ""
                self.current_thinking_signature = None
            elif block.get("type") == "system_message":
                # Handle system message content block
                system_text = block.get("text", "")
                source = block.get("source", "claude_code_sdk")
                # Format as text with clear source attribution
                formatted_text = f"[{source}]: {system_text}"
                yield self._format_chunk_output(delta={"content": formatted_text})
            elif block.get("type") == "tool_use_sdk" and self.enable_tool_calls:
                # Handle custom tool_use_sdk content block
                tool_id = block.get("id", "")
                tool_name = block.get("name", "")
                tool_input = block.get("input", {})
                source = block.get("source", "claude_code_sdk")

                # For dict format, immediately yield the tool call
                if self.output_format == "dict":
                    yield self._format_chunk_output(
                        delta={
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": tool_id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": json.dumps(tool_input),
                                    },
                                }
                            ]
                        }
                    )
                else:
                    # For SSE format, store for later processing
                    self.tool_calls[tool_id] = {
                        "id": tool_id,
                        "name": tool_name,
                        "arguments": tool_input,
                        "source": source,
                    }
            elif block.get("type") == "tool_result_sdk":
                # Handle custom tool_result_sdk content block
                source = block.get("source", "claude_code_sdk")
                tool_use_id = block.get("tool_use_id", "")
                result_content = block.get("content", "")
                is_error = block.get("is_error", False)
                error_indicator = " (ERROR)" if is_error else ""
                formatted_text = f"[{source} tool_result {tool_use_id}{error_indicator}]: {result_content}"
                yield self._format_chunk_output(delta={"content": formatted_text})
            elif block.get("type") == "result_message":
                # Handle custom result_message content block
                source = block.get("source", "claude_code_sdk")
                result_data = block.get("data", {})
                session_id = result_data.get("session_id", "")
                stop_reason = result_data.get("stop_reason", "")
                usage = result_data.get("usage", {})
                cost_usd = result_data.get("total_cost_usd")
                formatted_text = f"[{source} result {session_id}]: stop_reason={stop_reason}, usage={usage}"
                if cost_usd is not None:
                    formatted_text += f", cost_usd={cost_usd}"
                yield self._format_chunk_output(delta={"content": formatted_text})

            elif block.get("type") == "tool_use":
                # Start of tool call
                tool_id = block.get("id", "")
                tool_name = block.get("name", "")
                self.tool_calls[tool_id] = {
                    "id": tool_id,
                    "name": tool_name,
                    "arguments": "",
                }

        elif chunk_type == "content_block_delta":
            delta = chunk_data.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "text_delta":
                # Text content
                text = delta.get("text", "")
                if text:
                    yield self._format_chunk_output(delta={"content": text})

            elif delta_type == "thinking_delta" and self.thinking_block_active:
                # Thinking content
                thinking_text = delta.get("thinking", "")
                if thinking_text:
                    self.current_thinking_text += thinking_text

            elif delta_type == "signature_delta" and self.thinking_block_active:
                # Thinking signature
                signature = delta.get("signature", "")
                if signature:
                    if self.current_thinking_signature is None:
                        self.current_thinking_signature = ""
                    self.current_thinking_signature += signature

            elif delta_type == "input_json_delta":
                # Tool call arguments
                partial_json = delta.get("partial_json", "")
                if partial_json and self.tool_calls:
                    # Find the tool call this belongs to (usually the last one)
                    latest_tool_id = list(self.tool_calls.keys())[-1]
                    self.tool_calls[latest_tool_id]["arguments"] += partial_json

        elif chunk_type == "content_block_stop":
            # End of content block
            if self.thinking_block_active:
                # Format and send the complete thinking block
                self.thinking_block_active = False
                if self.current_thinking_text:
                    # Format thinking block with signature
                    thinking_content = f'<thinking signature="{self.current_thinking_signature}">{self.current_thinking_text}</thinking>'
                    yield self._format_chunk_output(delta={"content": thinking_content})
                # Reset thinking state
                self.current_thinking_text = ""
                self.current_thinking_signature = None

            elif (
                self.tool_calls
                and self.enable_tool_calls
                and self.output_format == "sse"
            ):
                # Send completed tool calls (only for SSE format, dict format sends immediately)
                for tool_call in self.tool_calls.values():
                    yield self._format_chunk_output(
                        delta={
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": tool_call["id"],
                                    "type": "function",
                                    "function": {
                                        "name": tool_call["name"],
                                        "arguments": json.dumps(tool_call["arguments"])
                                        if isinstance(tool_call["arguments"], dict)
                                        else tool_call["arguments"],
                                    },
                                }
                            ]
                        }
                    )

        elif chunk_type == "message_delta":
            # Usage information
            usage = chunk_data.get("usage", {})
            if usage and self.enable_usage:
                self.usage_info = {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0)
                    + usage.get("output_tokens", 0),
                }

        elif chunk_type == "message_stop":
            # End of message - handled in main process_stream method
            pass

    def _create_chunk_dict(
        self,
        delta: dict[str, Any] | None = None,
        finish_reason: str | None = None,
        usage: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Create an OpenAI completion chunk dict.

        Args:
            delta: The delta content for the chunk
            finish_reason: Optional finish reason
            usage: Optional usage information

        Returns:
            OpenAI completion chunk dict
        """
        chunk = {
            "id": self.message_id,
            "object": "chat.completion.chunk",
            "created": self.created,
            "model": self.model,
            "choices": [
                {
                    "index": 0,
                    "delta": delta or {},
                    "logprobs": None,
                    "finish_reason": finish_reason,
                }
            ],
        }

        if usage:
            chunk["usage"] = usage

        return chunk

    def _format_chunk_output(
        self,
        delta: dict[str, Any] | None = None,
        finish_reason: str | None = None,
        usage: dict[str, int] | None = None,
    ) -> str | dict[str, Any]:
        """Format chunk output based on output_format flag.

        Args:
            delta: The delta content for the chunk
            finish_reason: Optional finish reason
            usage: Optional usage information

        Returns:
            Either SSE string or dict based on output_format
        """
        if self.output_format == "dict":
            return self._create_chunk_dict(delta, finish_reason, usage)
        else:
            # SSE format
            if finish_reason:
                if usage:
                    return self.formatter.format_final_chunk(
                        self.message_id,
                        self.model,
                        self.created,
                        finish_reason,
                        usage=usage,
                    )
                else:
                    return self.formatter.format_final_chunk(
                        self.message_id, self.model, self.created, finish_reason
                    )
            elif delta and delta.get("role"):
                return self.formatter.format_first_chunk(
                    self.message_id, self.model, self.created, delta["role"]
                )
            elif delta and delta.get("content"):
                return self.formatter.format_content_chunk(
                    self.message_id, self.model, self.created, delta["content"]
                )
            elif delta and delta.get("tool_calls"):
                # Handle tool calls
                tool_call = delta["tool_calls"][0]  # Assume single tool call for now
                return self.formatter.format_tool_call_chunk(
                    self.message_id,
                    self.model,
                    self.created,
                    tool_call["id"],
                    tool_call.get("function", {}).get("name"),
                    tool_call.get("function", {}).get("arguments"),
                )
            else:
                # Empty delta
                return self.formatter.format_final_chunk(
                    self.message_id, self.model, self.created, "stop"
                )


__all__ = [
    "OpenAISSEFormatter",
    "OpenAIStreamProcessor",
]
