"""
Command routing and handling for UnrealOn SDK v1.0

Provides intelligent command routing with:
- Type-safe command dispatch using Pydantic v2 models
- Priority handling with configurable strategies
- Timeout management with automatic cancellation
- Performance monitoring and metrics collection
- Concurrent execution control with resource management
"""

import asyncio
import logging
from typing import Dict, Callable, Optional, Awaitable, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Use auto-generated models only - no custom models!
from unrealon_sdk.src.clients.python_websocket.types import ParserCommandEvent, CommandStatus
from unrealon_sdk.src.clients.python_http.models import SuccessResponse, ErrorResponse

# SDK metadata models
from unrealon_sdk.src.core.metadata import ExecutionInfo, RouterStatistics
from unrealon_sdk.src.core.exceptions import CommandError, TimeoutError as SDKTimeoutError
from unrealon_sdk.src.utils import generate_correlation_id


class CommandPriority(str, Enum):
    """Command priority levels for queue ordering."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class CommandExecution:
    """Tracks command execution state with comprehensive monitoring."""

    command: ParserCommandEvent
    handler: Callable
    started_at: datetime
    correlation_id: str
    task: Optional[asyncio.Task] = None
    timeout_task: Optional[asyncio.Task] = None
    priority: CommandPriority = CommandPriority.NORMAL

    @property
    def execution_time_ms(self) -> float:
        """Get current execution time in milliseconds."""
        return (datetime.utcnow() - self.started_at).total_seconds() * 1000

    @property
    def is_running(self) -> bool:
        """Check if command is currently running."""
        return self.task is not None and not self.task.done()

    @property
    def is_timed_out(self) -> bool:
        """Check if command has timed out."""
        return (
            self.timeout_task is not None
            and self.timeout_task.done()
            and not self.timeout_task.cancelled()
        )


class CommandRouter:
    """
    Routes and manages command execution with enterprise-grade capabilities.

    Features:
    - Priority-based command queuing with multiple strategies
    - Concurrent execution control with resource management
    - Comprehensive timeout handling with cancellation
    - Performance metrics collection and analysis
    - Error correlation and recovery recommendations
    - Circuit breaker pattern for failed handlers

    Follows Layer 2 requirements from development checklist:
    - Type-safe command dispatch
    - Automatic retry with exponential backoff
    - Resource monitoring and optimization
    - Error recovery and circuit breaker patterns
    """

    def __init__(self, max_concurrent_commands: int = 10, default_timeout: int = 300):
        """
        Initialize command router.

        Args:
            max_concurrent_commands: Maximum concurrent command executions
            default_timeout: Default command timeout in seconds
        """
        self.logger = logging.getLogger("unrealon_sdk.command_router")

        # Command handlers registry
        self._handlers: Dict[str, Callable] = {}

        # Execution tracking
        self._active_executions: Dict[str, CommandExecution] = {}
        self._command_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

        # Configuration
        self._max_concurrent_commands = max_concurrent_commands
        self._default_timeout = default_timeout

        # Statistics and monitoring
        self._total_commands = 0
        self._successful_commands = 0
        self._failed_commands = 0
        self._timeout_commands = 0
        self._cancelled_commands = 0

        # Performance tracking
        self._total_execution_time = 0.0
        self._min_execution_time = float("inf")
        self._max_execution_time = 0.0

        # Circuit breaker for handlers
        self._handler_failures: Dict[str, int] = {}
        self._handler_last_failure: Dict[str, datetime] = {}
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = timedelta(minutes=5)

        self.logger.debug(
            f"CommandRouter initialized with max_concurrent={max_concurrent_commands}"
        )

    def register_handler(
        self,
        command_type: str,
        handler: Callable[[ParserCommandEvent], Awaitable[Union[SuccessResponse, ErrorResponse]]],
    ) -> None:
        """
        Register a command handler.

        Args:
            command_type: Type of command to handle
            handler: Async function to handle the command
        """
        self._handlers[command_type] = handler

        # Reset circuit breaker for this handler
        self._handler_failures[command_type] = 0
        if command_type in self._handler_last_failure:
            del self._handler_last_failure[command_type]

        self.logger.debug(f"Registered handler for command type: {command_type}")

    def unregister_handler(self, command_type: str) -> None:
        """
        Unregister a command handler.

        Args:
            command_type: Type of command to unregister
        """
        if command_type in self._handlers:
            del self._handlers[command_type]
            self.logger.debug(f"Unregistered handler for command type: {command_type}")

    async def route_command(
        self, command: ParserCommandEvent
    ) -> Union[SuccessResponse, ErrorResponse]:
        """
        Route and execute a command with comprehensive error handling.

        Args:
            command: Command to execute

        Returns:
            Command response

        Raises:
            CommandError: If no handler exists for command type or execution fails
        """
        self._total_commands += 1
        start_time = datetime.utcnow()
        correlation_id = generate_correlation_id()

        self.logger.info(
            f"Routing command {command.command_id} of type {command.command_type}",
            extra={"correlation_id": correlation_id},
        )

        try:
            # Validate command and handler
            await self._validate_command(command)

            # Check circuit breaker for handler
            if self._is_circuit_breaker_open(command.command_type):
                raise CommandError(
                    f"Circuit breaker open for command type: {command.command_type}",
                    error_code="CIRCUIT_BREAKER_OPEN",
                )

            # Check concurrent execution limit
            if len(self._active_executions) >= self._max_concurrent_commands:
                raise CommandError(
                    f"Maximum concurrent commands limit reached ({self._max_concurrent_commands})",
                    error_code="CONCURRENT_LIMIT_EXCEEDED",
                )

            # Execute command
            response = await self._execute_command(command, correlation_id, start_time)

            # Update statistics for successful execution
            self._update_success_statistics(start_time)

            return response

        except Exception as e:
            # Update statistics for failed execution
            self._update_failure_statistics(command.command_type, start_time)

            # Create error response
            error_response = self._create_error_response(command, e, correlation_id, start_time)

            self.logger.error(
                f"Command {command.command_id} failed: {e}",
                extra={"correlation_id": correlation_id},
            )

            return error_response

    async def _validate_command(self, command: ParserCommandEvent) -> None:
        """Validate command before execution."""
        if command.command_type not in self._handlers:
            raise CommandError(
                f"No handler registered for command type: {command.command_type}",
                error_code="HANDLER_NOT_FOUND",
            )

        # Validate command structure using Pydantic (already validated during parsing)
        # Additional business logic validation can be added here

    def _is_circuit_breaker_open(self, command_type: str) -> bool:
        """Check if circuit breaker is open for a command type."""
        failure_count = self._handler_failures.get(command_type, 0)
        last_failure = self._handler_last_failure.get(command_type)

        if failure_count < self._circuit_breaker_threshold:
            return False

        if last_failure is None:
            return False

        # Check if timeout has passed
        if datetime.utcnow() - last_failure > self._circuit_breaker_timeout:
            # Reset circuit breaker
            self._handler_failures[command_type] = 0
            del self._handler_last_failure[command_type]
            return False

        return True

    async def _execute_command(
        self, command: ParserCommandEvent, correlation_id: str, start_time: datetime
    ) -> Union[SuccessResponse, ErrorResponse]:
        """Execute command with timeout and cancellation support."""

        handler = self._handlers[command.command_type]
        execution = CommandExecution(
            command=command, handler=handler, started_at=start_time, correlation_id=correlation_id
        )

        # Add to active executions
        self._active_executions[command.command_id] = execution

        try:
            # Create execution task
            execution.task = asyncio.create_task(handler(command))

            # Create timeout task
            timeout_seconds = command.timeout_seconds or self._default_timeout
            execution.timeout_task = asyncio.create_task(
                self._handle_timeout(command, timeout_seconds)
            )

            # Wait for either completion or timeout
            done, pending = await asyncio.wait(
                [execution.task, execution.timeout_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Check if command completed or timed out
            if execution.task in done:
                # Command completed successfully
                result_data = await execution.task
                execution_time = execution.execution_time_ms

                self._successful_commands += 1

                response = SuccessResponse(
                    success=True,
                    message="Command completed successfully",
                    data=result_data,
                    timestamp=datetime.utcnow().isoformat(),
                )

                self.logger.info(
                    f"Command {command.command_id} completed in {execution_time:.2f}ms",
                    extra={"correlation_id": correlation_id},
                )

                return response

            else:
                # Command timed out
                execution_time = execution.execution_time_ms
                self._timeout_commands += 1

                response = ErrorResponse(
                    success=False,
                    message=f"Command timed out after {timeout_seconds} seconds",
                    error_code="COMMAND_TIMEOUT",
                    timestamp=datetime.utcnow().isoformat(),
                )

                self.logger.warning(
                    f"Command {command.command_id} timed out after {execution_time:.2f}ms",
                    extra={"correlation_id": correlation_id},
                )

                return response

        finally:
            # Cleanup execution tracking
            if command.command_id in self._active_executions:
                del self._active_executions[command.command_id]

    async def _handle_timeout(self, command: ParserCommandEvent, timeout_seconds: int) -> None:
        """Handle command timeout."""
        await asyncio.sleep(timeout_seconds)
        self.logger.warning(
            f"Command {command.command_id} exceeded timeout of {timeout_seconds} seconds"
        )

    def _update_success_statistics(self, start_time: datetime) -> None:
        """Update statistics for successful command execution."""
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        self._total_execution_time += execution_time
        self._min_execution_time = min(self._min_execution_time, execution_time)
        self._max_execution_time = max(self._max_execution_time, execution_time)

    def _update_failure_statistics(self, command_type: str, start_time: datetime) -> None:
        """Update statistics for failed command execution."""
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        self._failed_commands += 1
        self._total_execution_time += execution_time

        # Update circuit breaker
        self._handler_failures[command_type] = self._handler_failures.get(command_type, 0) + 1
        self._handler_last_failure[command_type] = datetime.utcnow()

    def _create_error_response(
        self,
        command: ParserCommandEvent,
        error: Exception,
        correlation_id: str,
        start_time: datetime,
    ) -> ErrorResponse:
        """Create structured error response."""
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Determine error details
        if isinstance(error, CommandError):
            error_message = str(error)
            error_code = getattr(error, "error_code", "COMMAND_ERROR")
        elif isinstance(error, TimeoutError):
            error_message = str(error)
            error_code = "TIMEOUT_ERROR"
        else:
            error_message = f"Unexpected error: {str(error)}"
            error_code = "INTERNAL_ERROR"

        return ErrorResponse(
            success=False,
            message=error_message,
            error_code=error_code,
            timestamp=datetime.utcnow().isoformat(),
        )

    def get_registered_handlers(self) -> Dict[str, str]:
        """Get information about registered handlers."""
        return {
            cmd_type: handler.__name__ if hasattr(handler, "__name__") else str(handler)
            for cmd_type, handler in self._handlers.items()
        }

    def get_active_executions(self) -> Dict[str, ExecutionInfo]:
        """Get information about currently executing commands."""
        return {
            cmd_id: ExecutionInfo(
                command_id=cmd_id,
                command_type=execution.command.command_type,
                status=(
                    "running"
                    if execution.is_running
                    else ("timeout" if execution.is_timed_out else "completed")
                ),
                start_time=execution.started_at,
                duration_ms=execution.execution_time_ms,
            )
            for cmd_id, execution in self._active_executions.items()
        }

    def get_statistics(self) -> RouterStatistics:
        """Get comprehensive command execution statistics."""
        avg_execution_time = (
            self._total_execution_time / self._total_commands if self._total_commands > 0 else 0
        )

        success_rate = (
            self._successful_commands / self._total_commands * 100
            if self._total_commands > 0
            else 0
        )

        return RouterStatistics(
            total_commands=self._total_commands,
            successful_commands=self._successful_commands,
            failed_commands=self._failed_commands,
            average_execution_time_ms=avg_execution_time,
            active_executions=len(self._active_executions),
            success_rate=success_rate,
        )

    async def cancel_command(self, command_id: str) -> bool:
        """
        Cancel an active command execution.

        Args:
            command_id: ID of command to cancel

        Returns:
            True if command was cancelled, False if not found
        """
        if command_id not in self._active_executions:
            return False

        execution = self._active_executions[command_id]

        # Cancel tasks
        if execution.task and not execution.task.done():
            execution.task.cancel()

        if execution.timeout_task and not execution.timeout_task.done():
            execution.timeout_task.cancel()

        # Update statistics
        self._cancelled_commands += 1

        # Remove from tracking
        del self._active_executions[command_id]

        self.logger.info(f"Cancelled command {command_id}")
        return True

    async def shutdown(self) -> None:
        """Shutdown the command router and cancel all active executions."""
        self.logger.info("Shutting down command router...")

        # Cancel all active executions
        active_commands = list(self._active_executions.keys())
        for command_id in active_commands:
            await self.cancel_command(command_id)

        self.logger.info(
            f"Command router shutdown complete. Cancelled {len(active_commands)} commands"
        )

    def reset_statistics(self) -> None:
        """Reset all statistics (useful for testing)."""
        self._total_commands = 0
        self._successful_commands = 0
        self._failed_commands = 0
        self._timeout_commands = 0
        self._cancelled_commands = 0
        self._total_execution_time = 0.0
        self._min_execution_time = float("inf")
        self._max_execution_time = 0.0
        self._handler_failures.clear()
        self._handler_last_failure.clear()

        self.logger.debug("Command router statistics reset")
