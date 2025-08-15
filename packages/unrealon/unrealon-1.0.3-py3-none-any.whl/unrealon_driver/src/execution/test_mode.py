"""
Test Mode implementation for UnrealOn Driver v3.0

Development and debugging execution mode with detailed output and error reporting.
COMPLIANCE: 100% Pydantic v2 compliant, no Dict[str, Any] usage.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Optional

from unrealon_driver.src.core.exceptions import ParserError
from unrealon_driver.src.dto.execution import (
    ParserTestConfig,
    ExecutionResult,
    ErrorInfo,
    PerformanceMetrics,
    ExecutionEnvironment,
)


class TestMode:
    """
    🧪 Test Mode - Development and debugging

    Single execution for development and testing with:
    - Detailed logging and debugging
    - Error reporting with suggestions
    - Performance metrics
    - Results visualization
    """

    def __init__(self, parser: Any, config: ParserTestConfig):
        """Initialize test mode with type-safe configuration."""
        self.parser = parser
        self.config = config
        self.logger = parser.logger
        self.metrics = parser.metrics

    async def execute(self, **kwargs) -> ExecutionResult:
        """Execute parser in test mode with type-safe results."""
        start_time = time.time()
        start_datetime = datetime.now()
        execution_id = f"test_{int(start_time)}"

        if self.config.verbose:
            self._print_test_header()

        try:
            # Initialize parser if needed
            await self._initialize_test_environment()

            # Execute the parse method
            if self.config.verbose:
                print("🚀 Starting parse execution...")

            parse_start = time.time()
            result = await self.parser.parse()
            parse_duration = time.time() - parse_start

            # Process results
            processed_result = await self._process_test_result(
                result, parse_duration, execution_id, start_datetime
            )

            if self.config.verbose:
                self._print_test_success(processed_result, time.time() - start_time)

            return processed_result

        except Exception as e:
            # In test mode, let critical exceptions propagate for debugging
            if isinstance(e, (RuntimeError, NotImplementedError)):
                raise
                
            error_result = await self._handle_test_error(
                e, execution_id, start_datetime, time.time() - start_time
            )

            if self.config.verbose:
                self._print_test_error(error_result)

            return error_result

        finally:
            await self._cleanup_test_environment()

    def _print_test_header(self):
        """Print test mode header."""
        print("\n" + "=" * 60)
        print(f"🧪 UnrealOn Driver v3.0 - Test Mode")
        print(f"📝 Parser: {self.parser.parser_name}")
        print(f"🆔 ID: {self.parser.parser_id}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    async def _initialize_test_environment(self):
        """Initialize test environment."""
        if self.config.show_browser:
            # Override browser config to show browser
            if hasattr(self.parser, "_browser") and self.parser._browser:
                self.parser._browser.config["headless"] = False
            else:
                self.parser._config.browser_config["headless"] = False

        # Ensure system directories exist
        system_dir = self.parser._config._get_system_dir()
        system_dir.mkdir(parents=True, exist_ok=True)

        if self.logger:
            self.logger.info(f"Starting test execution for {self.parser.parser_name}")

    async def _process_test_result(
        self, result: Any, duration: float, execution_id: str, start_time: datetime
    ) -> ExecutionResult:
        """Process and enrich test results with type safety."""
        end_time = datetime.now()

        # Count items processed
        items_count = 0
        if isinstance(result, list):
            items_count = len(result)
        elif isinstance(result, dict) and "data" in result:
            data = result["data"]
            if isinstance(data, list):
                items_count = len(data)
            else:
                items_count = 1
        elif result is not None:
            items_count = 1

        # Create performance metrics
        performance_metrics = PerformanceMetrics(
            execution_time_seconds=duration,
            memory_usage_mb=0.0,  # TODO: Add real memory tracking
            cpu_usage_percent=0.0,  # TODO: Add real CPU tracking
            operations_count=items_count,
            operations_per_second=items_count / duration if duration > 0 else 0.0,
        )

        return ExecutionResult(
            success=True,
            execution_id=execution_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            data=result if isinstance(result, dict) else {"result": result},
            items_processed=items_count,
            error=None,
            parser_id=self.parser.parser_id,
            execution_mode="test",
            environment=self.config.environment,
            performance_metrics=performance_metrics,
        )

    async def _handle_test_error(
        self,
        error: Exception,
        execution_id: str,
        start_time: datetime,
        total_duration: float,
    ) -> ExecutionResult:
        """Handle test execution errors with type safety."""
        end_time = datetime.now()

        # Create error info
        error_info = ErrorInfo(
            message=str(error),
            error_type=type(error).__name__,
            error_code=getattr(
                error, "error_code", None
            ),  # OK for exception attributes
            traceback=None,  # We can add traceback if needed
            context={
                "parser_id": self.parser.parser_id,
                "execution_id": execution_id,
                "test_config": self.config.model_dump(),
            },
        )

        # Log error
        if self.logger:
            self.logger.error(f"Test execution failed: {error}")

        # Create performance metrics for error case
        performance_metrics = PerformanceMetrics(
            execution_time_seconds=total_duration,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            operations_count=0,
            operations_per_second=0.0,
        )

        return ExecutionResult(
            success=False,
            execution_id=execution_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=total_duration,
            data=None,
            items_processed=0,
            error=error_info,
            parser_id=self.parser.parser_id,
            execution_mode="test",
            environment=self.config.environment,
            performance_metrics=performance_metrics,
        )

    async def _cleanup_test_environment(self):
        """Clean up test environment."""
        try:
            # Capture final screenshots if enabled
            if self.config.save_screenshots:
                # Implementation for screenshot capture
                pass

            if self.logger:
                self.logger.info("Test environment cleanup completed")

        except Exception as e:
            # Don't fail on screenshot errors, but log for debugging
            if self.logger:
                self.logger.debug(f"Screenshot capture failed (non-critical): {e}")

    def _print_test_success(self, result: ExecutionResult, total_duration: float):
        """Print successful test results."""
        print("\n✅ Test completed successfully!")
        print(f"⏱️  Total duration: {total_duration:.2f}s")
        print(f"📊 Parse duration: {result.duration_seconds:.2f}s")
        print(f"📈 Items processed: {result.items_processed}")
        print(f"🆔 Execution ID: {result.execution_id}")

        if result.data and self.config.verbose:
            print(f"📄 Result preview: {str(result.data)[:100]}...")

    def _print_test_error(self, result: ExecutionResult):
        """Print test error information."""
        print("\n❌ Test failed!")
        print(f"⏱️  Duration: {result.duration_seconds:.2f}s")
        print(f"🆔 Execution ID: {result.execution_id}")

        if result.error:
            print(f"🚫 Error: {result.error.message}")
            print(f"📝 Type: {result.error.error_type}")
            if result.error.error_code:
                print(f"🔢 Code: {result.error.error_code}")

    def __repr__(self) -> str:
        return f"<TestMode(parser={self.parser.parser_id}, config={self.config.environment})>"
