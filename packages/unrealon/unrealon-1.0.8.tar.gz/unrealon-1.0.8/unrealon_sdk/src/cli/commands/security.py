"""
Security Analysis Commands

Simple security scanning for UnrealOn SDK.
"""

import subprocess
from rich.console import Console
from typing import Dict, Any

console = Console()


def run_security_scan() -> Dict[str, Any]:
    """Run quick security vulnerability scan."""
    console.print("[bold blue]🔒 Security vulnerability scan...[/bold blue]")
    
    with console.status("[bold green]Scanning..."):
        try:
            # Bandit scan for high severity issues
            result = subprocess.run(
                ['bandit', '-r', 'unrealon_sdk/', '--severity-level', 'high'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                console.print("[green]✅ No critical vulnerabilities found[/green]")
                return {'status': 'clean', 'issues': 0}
            else:
                console.print("[red]❌ Security issues detected[/red]")
                console.print(result.stdout)
                return {'status': 'issues', 'issues': 1, 'output': result.stdout}
                
        except FileNotFoundError:
            console.print("[yellow]⚠️ Bandit not installed: pip install bandit[/yellow]")
            return {'status': 'error', 'message': 'Bandit not installed'}