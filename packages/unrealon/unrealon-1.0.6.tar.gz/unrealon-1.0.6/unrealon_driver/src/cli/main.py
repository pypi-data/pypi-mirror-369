"""
Main CLI entry point for UnrealOn Driver v3.0

Global CLI interface for driver operations.
"""

import click
from typing import Optional


@click.group()
@click.version_option(version="3.0.0", prog_name="unrealon-driver")
def main():
    """
    🚀 UnrealOn Driver v3.0 - Revolutionary Web Automation

    Zero-configuration web automation framework with AI-first design.
    """
    pass


@main.command()
@click.argument("parser_name")
@click.option("--test", "-t", is_flag=True, help="Run in test mode")
@click.option("--daemon", "-d", is_flag=True, help="Run in daemon mode")
@click.option("--schedule", "-s", help="Run in scheduled mode (e.g., '30m', '1h')")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
def run(
    parser_name: str,
    test: bool,
    daemon: bool,
    schedule: Optional[str],
    interactive: bool,
):
    """Run a parser by name."""
    click.echo(f"🚀 Running parser: {parser_name}")

    if test:
        click.echo("🧪 Test mode")
    elif daemon:
        click.echo("🔌 Daemon mode")
    elif schedule:
        click.echo(f"⏰ Scheduled mode: {schedule}")
    elif interactive:
        click.echo("🎮 Interactive mode")
    else:
        click.echo("❌ No execution mode specified")
        click.echo("Use --test, --daemon, --schedule, or --interactive")


@main.command()
def version():
    """Show version information."""
    click.echo("🚀 UnrealOn Driver v3.0.0")
    click.echo("Revolutionary web automation framework")


@main.command()
def init():
    """Initialize a new parser project."""
    click.echo("🎯 Initializing new parser project...")
    click.echo("(Feature coming soon)")


if __name__ == "__main__":
    main()
