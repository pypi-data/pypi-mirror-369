"""
Health Check Commands

System health diagnostics for UnrealOn SDK.
"""

import sys
from rich.console import Console
from typing import Dict, List, Any

console = Console()


def run_health_check() -> Dict[str, Any]:
    """System health check."""
    console.print("[bold blue]🩺 System diagnostics...[/bold blue]")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append("Python version below 3.9")
    
    # Check SDK
    try:
        import unrealon_sdk
        console.print("[green]✅ SDK installed[/green]")
    except ImportError:
        issues.append("SDK not installed")
    
    # Check dependencies
    deps = ['pydantic', 'aiohttp', 'click', 'rich']
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            issues.append(f"Missing: {dep}")
    
    if not issues:
        console.print("[green]✅ System is healthy![/green]")
        return {'status': 'healthy', 'issues': []}
    else:
        console.print("[yellow]⚠️ Issues found:[/yellow]")
        for issue in issues:
            console.print(f"[red]• {issue}[/red]")
        return {'status': 'issues', 'issues': issues}
