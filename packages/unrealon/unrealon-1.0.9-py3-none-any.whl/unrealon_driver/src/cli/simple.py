"""
UnrealOn Driver v3.0 Simple CLI

Restored full Click-based CLI functionality from v2.0.
KISS principle - does exactly what you need with new Driver v3.0 architecture.
"""

import asyncio
import signal
import time
from typing import Callable, Optional, Dict, Any
from pathlib import Path

import click

from unrealon_driver.src.core.parser import Parser
from unrealon_driver.src.dto.cli import ParserInstanceConfig, create_parser_config
from unrealon_driver.src.config.auto_config import AutoConfig
from unrealon_driver.src.dto.config import LogLevel
from unrealon_driver.src.utils import TimeFormatter, ScheduleTimer, DaemonTimer


class SimpleParser(Parser):
    """
    Enhanced Parser with Click CLI integration.

    Combines the revolutionary v3.0 Parser with the proven CLI system from v2.0.
    """

    def __init__(self, config: ParserInstanceConfig):
        """
        Initialize SimpleParser with Pydantic configuration.

        Args:
            config: ParserInstanceConfig with validated configuration
        """
        if not isinstance(config, ParserInstanceConfig):
            raise TypeError(f"Expected ParserInstanceConfig, got {type(config)}")

        # Store validated config
        self.cli_config = config
        # Initialize base Parser with converted config
        super().__init__(
            parser_id=config.parser_id,
            parser_name=config.parser_name,
            config=config.to_parser_config(),
        )

        # Override _config after super().__init__() for logger compatibility
        self._config = config

        # Shutdown event for graceful stopping
        self._shutdown_event = asyncio.Event()

        if self.logger:
            self.logger.info(f"🚀 SimpleParser initialized: {self.parser_name}")

    async def setup(self) -> None:
        """Setup parser resources (override in subclass if needed)."""
        if self.logger:
            self.logger.info("Setting up parser resources...")

    async def cleanup(self) -> None:
        """Cleanup parser resources (override in subclass if needed)."""
        if self.logger:
            self.logger.info("Cleaning up parser resources...")
        await super().cleanup()

    async def parse(self) -> dict:
        """
        Main parsing method - override this in your parser.
        Should return parsed data.
        """
        return await self.parse_data()

    async def parse_data(self) -> dict:
        """
        Override this method in your parser.
        Should return parsed data.

        Note: This is an alias for parse() method for CLI compatibility.
        """
        raise NotImplementedError(
            f"Parser '{self.parser_name}' must implement either parse() or parse_data() method."
        )

    def create_click_cli(self, custom_commands: Optional[Dict[str, Callable]] = None):
        """
        Create a Click CLI interface for this parser.

        Args:
            custom_commands: Dict of command_name -> async_function for custom commands
        """

        @click.group(invoke_without_command=True)
        @click.pass_context
        def cli(ctx):
            """Revolutionary parser CLI with zero configuration."""
            if ctx.invoked_subcommand is None:
                click.echo(f"🚀 {self.parser_name}")
                click.echo(
                    f"   {self.cli_config.description or 'Revolutionary web automation'}"
                )
                click.echo("\nAvailable commands:")
                click.echo("  test       - Run test mode")
                click.echo("  daemon     - Run daemon mode (WebSocket service)")
                click.echo("  scheduled  - Run scheduled mode")
                click.echo("  interactive - Run interactive mode")

                if custom_commands:
                    click.echo("\nCustom commands:")
                    for cmd_name in custom_commands.keys():
                        click.echo(f"  {cmd_name}")

        @cli.command()
        @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
        @click.option("--show-browser", is_flag=True, help="Show browser window")
        def test(verbose, show_browser):
            """Run parser in test mode."""

            async def run():
                start_time = time.time()
                try:
                    click.echo(f"🧪 Starting {self.parser_name} test...")
                    click.echo(f"🕐 Started at: {TimeFormatter.format_datetime()}")

                    # Configure test options
                    test_config = {}
                    if verbose:
                        test_config["verbose"] = True
                    if show_browser:
                        test_config["show_browser"] = True

                    result = await self.test(**test_config)
                    
                    duration = time.time() - start_time

                    if result["success"]:
                        click.echo(f"✅ Test completed successfully in {TimeFormatter.format_duration(duration)}!")
                        if result.get("data"):
                            count = (
                                len(result["data"])
                                if isinstance(result["data"], (list, dict))
                                else 1
                            )
                            click.echo(f"📊 Result: {count} items")
                    else:
                        click.echo(f"❌ Test failed after {TimeFormatter.format_duration(duration)}: {result['error']['message']}")

                except Exception as e:
                    duration = time.time() - start_time
                    click.echo(f"❌ Test error after {TimeFormatter.format_duration(duration)}: {e}")
                    raise

            try:
                asyncio.run(run())
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # Already in event loop, run synchronously

                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task for running loop
                        task = loop.create_task(run())
                        # Don't await here as it would block
                    else:
                        asyncio.run(run())
                else:
                    raise

        @cli.command()
        @click.option("--server", "-s", help="WebSocket server URL")
        @click.option("--api-key", "-k", help="API key for authentication")
        def daemon(server, api_key):
            """Run parser in daemon mode (WebSocket service)."""

            async def run():
                daemon_timer = DaemonTimer()

                try:
                    click.echo(f"🔌 Starting {self.parser_name} daemon...")
                    click.echo(f"🕐 Started at: {TimeFormatter.format_datetime()}")
                    if server:
                        click.echo(f"🌐 Server: {server}")
                    if api_key:
                        click.echo("🔑 API key provided")
                    click.echo("Press Ctrl+C to stop\n")

                    kwargs = {}
                    if server:
                        kwargs["server"] = server
                        daemon_timer.connect()
                    if api_key:
                        kwargs["api_key"] = api_key

                    # Start daemon with periodic status updates
                    daemon_task = asyncio.create_task(self.daemon(**kwargs))

                    # Status update task
                    async def status_updates():
                        while not daemon_task.done():
                            await asyncio.sleep(30)  # Every 30 seconds
                            daemon_timer.heartbeat()
                            click.echo(
                                f"💓 Status - Uptime: {daemon_timer.get_uptime()}"
                            )

                    status_task = asyncio.create_task(status_updates())

                    # Wait for completion
                    await daemon_task
                    status_task.cancel()

                except KeyboardInterrupt:
                    click.echo(f"\n⏹️  Daemon stopped (Ctrl+C)")
                    click.echo(f"⏰ Final uptime: {daemon_timer.get_uptime()}")
                except Exception as e:
                    click.echo(f"❌ Daemon error: {e}")
                    raise

            try:
                asyncio.run(run())
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # Already in event loop, run synchronously

                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task for running loop
                        task = loop.create_task(run())
                        # Don't await here as it would block
                    else:
                        asyncio.run(run())
                else:
                    raise

        @cli.command()
        @click.option(
            "--every",
            "-e",
            default="30m",
            help="Execution interval (e.g., '30m', '1h', 'daily')",
        )
        @click.option(
            "--at", "-a", help="Time for daily/weekly schedules (e.g., '09:00')"
        )
        @click.option("--max-runs", type=int, help="Maximum number of runs")
        def scheduled(every, at, max_runs):
            """Run parser in scheduled mode."""

            async def run():
                schedule_timer = ScheduleTimer(every)

                try:
                    click.echo(f"⏰ Starting {self.parser_name} scheduled mode...")
                    click.echo(f"🕐 Started at: {TimeFormatter.format_datetime()}")
                    click.echo(f"📅 Schedule: every {every}")
                    if at:
                        click.echo(f"🕘 At time: {at}")
                    if max_runs:
                        click.echo(f"🔢 Max runs: {max_runs}")
                    click.echo("Press Ctrl+C to stop\n")

                    kwargs = {"every": every}
                    if at:
                        kwargs["at"] = at
                    if max_runs:
                        kwargs["max_runs"] = max_runs

                    # Custom schedule implementation with timing
                    run_count = 0
                    success_count = 0

                    while True:
                        if max_runs and run_count >= max_runs:
                            click.echo(f"🏁 Reached maximum runs ({max_runs})")
                            break

                        # Start run timer
                        schedule_timer.start_run()
                        run_start = time.time()

                        click.echo(
                            f"🚀 Starting run #{run_count + 1} at {TimeFormatter.format_time()}"
                        )

                        try:
                            # Execute parser
                            result = await self.parse()
                            duration = time.time() - run_start

                            if result:
                                success_count += 1
                                click.echo(
                                    f"✅ Run #{run_count + 1} completed in {TimeFormatter.format_duration(duration)}"
                                )
                            else:
                                click.echo(
                                    f"❌ Run #{run_count + 1} failed after {TimeFormatter.format_duration(duration)}"
                                )

                        except Exception as e:
                            duration = time.time() - run_start
                            click.echo(
                                f"❌ Run #{run_count + 1} error after {TimeFormatter.format_duration(duration)}: {e}"
                            )

                        run_count += 1

                        # Show status
                        click.echo(
                            f"📊 Progress: {success_count}/{run_count} successful"
                        )
                        click.echo(
                            f"⏰ Total elapsed: {schedule_timer.get_elapsed_total()}"
                        )

                        if max_runs and run_count >= max_runs:
                            break

                        # Show next run info
                        click.echo(
                            f"🕐 Next run at: {TimeFormatter.format_time(schedule_timer.next_run)}"
                        )
                        click.echo(
                            f"⏳ Waiting: {schedule_timer.get_time_until_next()}"
                        )

                        # Sleep until next run with live countdown
                        sleep_seconds = TimeFormatter.parse_interval(every)
                        
                        def countdown_callback(current_time, remaining_time, remaining_seconds, update_in_place=False):
                            if update_in_place:
                                # Live update on same line
                                import sys
                                sys.stdout.write(f"\r⏳ {current_time} - Time remaining: {remaining_time}")
                                sys.stdout.flush()
                            else:
                                click.echo(f"⏳ {current_time} - Time remaining: {remaining_time}")
                        
                        await TimeFormatter.countdown_sleep(sleep_seconds, countdown_callback)

                except KeyboardInterrupt:
                    click.echo(f"\n⏹️  Scheduled mode stopped (Ctrl+C)")
                    click.echo(
                        f"⏰ Total runtime: {schedule_timer.get_elapsed_total()}"
                    )
                    click.echo(f"🔄 Runs completed: {schedule_timer.run_count}")
                except Exception as e:
                    click.echo(f"❌ Scheduled mode error: {e}")
                    raise

            try:
                asyncio.run(run())
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # Already in event loop, run synchronously

                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task for running loop
                        task = loop.create_task(run())
                        # Don't await here as it would block
                    else:
                        asyncio.run(run())
                else:
                    raise

        @cli.command()
        def interactive():
            """Run parser in interactive mode."""

            async def run():
                start_time = time.time()
                try:
                    click.echo(f"🎮 Starting {self.parser_name} interactive mode...")
                    click.echo(f"🕐 Started at: {TimeFormatter.format_datetime()}")
                    await self.interactive()
                except KeyboardInterrupt:
                    duration = time.time() - start_time
                    click.echo(f"⏹️  Interactive mode stopped (Ctrl+C)")
                    click.echo(f"⏰ Session duration: {TimeFormatter.format_duration(duration)}")
                except Exception as e:
                    duration = time.time() - start_time
                    click.echo(f"❌ Interactive mode error after {TimeFormatter.format_duration(duration)}: {e}")
                    raise

            try:
                asyncio.run(run())
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # Already in event loop, run synchronously

                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task for running loop
                        task = loop.create_task(run())
                        # Don't await here as it would block
                    else:
                        asyncio.run(run())
                else:
                    raise

        # Add custom commands
        if custom_commands:
            for cmd_name, cmd_func in custom_commands.items():

                @cli.command(name=cmd_name)
                @click.pass_context
                def custom_cmd(ctx, _cmd_func=cmd_func):
                    """Custom command."""

                    async def run():
                        try:
                            result = await _cmd_func(self)
                            if result:
                                click.echo("✅ Command completed!")
                        except Exception as e:
                            click.echo(f"❌ Command error: {e}")
                            raise

                    try:
                        asyncio.run(run())
                    except RuntimeError as e:
                        if "cannot be called from a running event loop" in str(e):
                            # Already in event loop, run synchronously
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # Create task for running loop
                                    task = loop.create_task(run())
                                    # Don't await here as it would block
                                else:
                                    asyncio.run(run())
                            except RuntimeError:
                                # No event loop, just skip
                                pass
                        else:
                            raise

        return cli

    # Legacy compatibility methods from v2.0
    async def run_test(self) -> dict:
        """Legacy compatibility: run parser in test mode."""
        result = await self.test()
        if hasattr(result, "data") and result.data is not None:
            return result.data
        elif hasattr(result, "data") and isinstance(result.data, dict):
            return result.data
        elif isinstance(result, dict):
            return result
        else:
            return {}

    async def run_daemon(self) -> None:
        """Legacy compatibility: run parser in daemon mode."""
        await self.daemon()

    async def run_scheduled(self) -> None:
        """Legacy compatibility: run parser in scheduled mode."""
        every = getattr(self, "scheduled_interval", "30m")
        await self.schedule(every=str(every))


# Convenience function for quick Click CLI creation
def create_click_parser_cli(
    parser_class: type,
    parser_id: str,
    parser_name: Optional[str] = None,
    description: Optional[str] = None,
    custom_commands: Optional[Dict[str, Callable]] = None,
    **config_kwargs,
):
    """
    Create a Click CLI for a parser class.

    Args:
        parser_class: Parser class (should inherit from SimpleParser)
        parser_id: Unique parser identifier
        parser_name: Human-readable name
        description: Parser description
        custom_commands: Dict of command_name -> async_function for custom commands
        **config_kwargs: Additional config parameters

    Returns:
        Click CLI group ready to run

    Usage:
        if __name__ == "__main__":
            cli = create_click_parser_cli(
                MyParser,
                "my_parser",
                custom_commands={"custom": my_custom_func}
            )
            cli()
    """
    # Create parser config
    config = create_parser_config(
        parser_id=parser_id,
        parser_name=parser_name,
        description=description,
        **config_kwargs,
    )

    # Create parser instance
    parser = parser_class(config)

    # Create and return CLI
    return parser.create_click_cli(custom_commands)
