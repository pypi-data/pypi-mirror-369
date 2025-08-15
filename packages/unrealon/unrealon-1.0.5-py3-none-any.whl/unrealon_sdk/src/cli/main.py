"""
UnrealOn SDK CLI - Simplified & Optimal

🚀 Simple and powerful CLI for SDK testing and diagnostics
"""

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

# Import command functions
from .commands.security import run_security_scan
from .commands.benchmark import run_performance_benchmark
from .commands.health import run_health_check
from .commands.tests import run_all_tests
from .commands.servers import start_mock_server, manage_servers
from .commands.reports import generate_report

console = Console()


def print_banner():
    """Print beautiful CLI banner."""
    banner = Text()
    banner.append("🚀 UnrealOn SDK ", style="bold blue")
    banner.append("CLI Tools", style="bold white")
    banner.append(" v1.0", style="dim")

    panel = Panel(
        banner, title="[bold]Testing & Diagnostics[/bold]", box=box.DOUBLE, border_style="blue"
    )
    console.print(panel)


@click.group(invoke_without_command=True)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, verbose):
    """🚀 UnrealOn SDK CLI Tools"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # If no command specified - run interactive mode
    if ctx.invoked_subcommand is None:
        print_banner()
        interactive_menu()


def interactive_menu():
    """Interactive menu."""
    while True:
        console.print("\n[bold blue]Choose an action:[/bold blue]")

        action = questionary.select(
            "",
            choices=[
                "🔒 Security - Vulnerability scanning",
                "⚡ Benchmark - Performance testing",
                "🧪 Tests - Run all tests",
                "🩺 Health - System health check",
                "🖥️ Servers - Start mock servers",
                "📊 Report - Generate report",
                "❌ Exit",
            ],
        ).ask()

        if not action or "Exit" in action:
            console.print("[green]Goodbye! 👋[/green]")
            break

        if "Security" in action:
            run_security_scan()
        elif "Benchmark" in action:
            run_performance_benchmark()
        elif "Tests" in action:
            run_all_tests()
        elif "Health" in action:
            run_health_check()
        elif "Servers" in action:
            manage_servers()
        elif "Report" in action:
            generate_report()


@cli.command()
def security():
    """🔒 Quick security check."""
    run_security_scan()


@cli.command()
def benchmark():
    """⚡ Quick benchmarks."""
    run_performance_benchmark()


@cli.command()
def test():
    """🧪 Run all tests."""
    run_all_tests()


@cli.command()
def health():
    """🩺 System health check."""
    run_health_check()


@cli.command()
@click.option("--port", default=18765, help="WebSocket port")
def server(port):
    """🖥️ Start mock server."""
    start_mock_server(port)


@cli.command()
def report():
    """📊 Generate report."""
    generate_report()


if __name__ == "__main__":
    cli()
