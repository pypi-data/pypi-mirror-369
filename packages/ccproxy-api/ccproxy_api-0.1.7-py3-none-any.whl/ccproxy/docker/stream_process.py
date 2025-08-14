"""Process execution and streaming output handling.

This module provides tools for running subprocesses and handling their output streams.
It supports custom output processing through middleware components, making it suitable
for real-time output handling in CLI applications.

Example:
    ```python
    from ccproxy.docker.stream_process import run_command, DefaultOutputMiddleware

    # Create custom middleware to add timestamps
    from datetime import datetime
    class TimestampMiddleware(DefaultOutputMiddleware):
        async def process(self, line: str, stream_type: str) -> str:
            timestamp = datetime.now().strftime('%H:%M:%S')
            return f"[{timestamp}] {await super().process(line, stream_type)}"

    # Run a command with custom output handling
    return_code, stdout, stderr = await run_command(
        "ls -la", middleware=TimestampMiddleware()
    )
    ```
"""

import asyncio
import shlex
from typing import Any, Generic, TypeAlias, TypeVar, cast


T = TypeVar("T")  # Type of processed output

# Type alias for the result of run_command
ProcessResult: TypeAlias = tuple[int, list[T], list[T]]  # (return_code, stdout, stderr)


class OutputMiddleware(Generic[T]):
    """Base class for processing command output streams.

    OutputMiddleware provides a way to intercept and process output lines
    from subprocesses. Implementations can format, filter, or transform
    the output as needed.

    Type parameter T represents the return type of the process method,
    allowing middleware to transform strings into other types if needed.
    """

    async def process(self, line: str, stream_type: str) -> T:
        """Process a line of output from a subprocess stream.

        Args:
            line: A line of text from the process output
            stream_type: Either "stdout" or "stderr"

        Returns:
            Processed output of type T

        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError()


class DefaultOutputMiddleware(OutputMiddleware[str]):
    """Simple middleware that prints output with optional prefixes.

    This middleware prints each line to the console with configurable
    prefixes for stdout and stderr streams.
    """

    def __init__(self, stdout_prefix: str = "", stderr_prefix: str = "ERROR: ") -> None:
        """Initialize middleware with custom prefixes.

        Args:
            stdout_prefix: Prefix for stdout lines (default: "")
            stderr_prefix: Prefix for stderr lines (default: "ERROR: ")
        """
        self.stdout_prefix = stdout_prefix
        self.stderr_prefix = stderr_prefix

    async def process(self, line: str, stream_type: str) -> str:
        """Process and print a line with the appropriate prefix.

        Args:
            line: Output line to process
            stream_type: Either "stdout" or "stderr"

        Returns:
            The original line (unmodified)
        """
        prefix = self.stdout_prefix if stream_type == "stdout" else self.stderr_prefix
        print(f"{prefix}{line}")
        return line


class ChainedOutputMiddleware(OutputMiddleware[T]):
    """Middleware that chains multiple middleware components together.

    Processes output through a sequence of middleware components, where each
    middleware processes the output from the previous one. The final output
    type T is determined by the last middleware in the chain.

    Example:
        ```python
        # Chain progress tracking with logging
        progress_middleware = CompilationProgressMiddleware(callback)
        logger_middleware = LoggerOutputMiddleware(logger)

        chained = ChainedOutputMiddleware([progress_middleware, logger_middleware])

        # Process: line -> progress_middleware -> logger_middleware -> final result
        result = docker_adapter.run_container("image", [], {}, middleware=chained)
        ```
    """

    def __init__(self, middleware_chain: list[OutputMiddleware[Any]]) -> None:
        """Initialize chained middleware.

        Args:
            middleware_chain: List of middleware components to chain together.
                             Output flows from first to last middleware.

        Raises:
            ValueError: If middleware_chain is empty
        """
        if not middleware_chain:
            raise ValueError("Middleware chain cannot be empty")

        self.middleware_chain = middleware_chain

    async def process(self, line: str, stream_type: str) -> T:
        """Process line through the middleware chain.

        Args:
            line: Output line to process
            stream_type: Either "stdout" or "stderr"

        Returns:
            Output from the final middleware in the chain
        """
        current_output: Any = line

        # Process through each middleware in sequence
        for middleware in self.middleware_chain:
            current_output = await middleware.process(current_output, stream_type)

        return cast(T, current_output)


def create_chained_middleware(
    middleware_chain: list[OutputMiddleware[Any]],
) -> ChainedOutputMiddleware[Any]:
    """Factory function to create a chained middleware.

    Args:
        middleware_chain: List of middleware components to chain together

    Returns:
        ChainedOutputMiddleware instance

    Raises:
        ValueError: If middleware_chain is empty

    Example:
        ```python
        from ccproxy.docker.stream_process import create_chained_middleware
        from ccproxy.docker.adapter import LoggerOutputMiddleware

        # Create individual middleware components
        logger_middleware = LoggerOutputMiddleware(logger)

        # Chain them together
        chained = create_chained_middleware([logger_middleware])

        # Use with docker adapter
        result = docker_adapter.run_container("image", [], {}, middleware=chained)
        ```
    """
    return ChainedOutputMiddleware(middleware_chain)


async def run_command(
    cmd: str | list[str],
    middleware: OutputMiddleware[T] | None = None,
) -> ProcessResult[T]:
    """Run a command and process its output through middleware.

    This function executes a command as a subprocess and streams its output
    through the provided middleware for real-time processing. The processed
    outputs are collected and returned along with the exit code.

    Args:
        cmd: Command to run, either as a string or list of arguments
        middleware: Optional middleware for processing output (uses DefaultOutputMiddleware if None)

    Returns:
        Tuple containing:
            - Return code from the process (0 for success)
            - List of processed stdout lines
            - List of processed stderr lines

    Example:
        ```python
        # Simple command execution
        rc, stdout, stderr = await run_command("ls -l")

        # With custom middleware
        class CustomMiddleware(OutputMiddleware[str]):
            async def process(self, line: str, stream_type: str) -> str:
                return f"[{stream_type}] {line}"

        rc, stdout, stderr = await run_command("ls -l", CustomMiddleware())
        ```
    """
    if middleware is None:
        # Cast is needed because T is unbound at this point
        middleware = cast(OutputMiddleware[T], DefaultOutputMiddleware())

    # Parse string commands into argument lists
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    # Start the async process with pipes for stdout and stderr
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async def stream_output(stream: asyncio.StreamReader, stream_type: str) -> list[T]:
        """Process output from a stream and capture results.

        Args:
            stream: Async stream to read from (stdout or stderr)
            stream_type: Type of the stream ("stdout" or "stderr")

        Returns:
            List of processed output lines
        """
        captured: list[T] = []
        while True:
            line_bytes = await stream.readline()
            if not line_bytes:
                break
            line = line_bytes.decode().rstrip()
            if line:
                processed = await middleware.process(line, stream_type)
                if processed is not None:
                    captured.append(processed)
        return captured

    # Create async tasks for concurrent output processing
    # Ensure stdout and stderr are available
    if process.stdout is None or process.stderr is None:
        raise RuntimeError("Process stdout or stderr is None")

    stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
    stderr_task = asyncio.create_task(stream_output(process.stderr, "stderr"))

    # Wait for process to complete and collect output
    return_code = await process.wait()
    stdout_lines = await stdout_task
    stderr_lines = await stderr_task

    return return_code, stdout_lines, stderr_lines
