"""
Performance Benchmark Commands

Simple performance testing for UnrealOn SDK.
"""

import subprocess
from rich.console import Console
from typing import Dict, Any

console = Console()


def run_performance_benchmark() -> Dict[str, Any]:
    """Run performance benchmarks."""
    console.print("[bold blue]⚡ Performance benchmarks...[/bold blue]")
    
    with console.status("[bold green]Running tests..."):
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'unrealon_sdk/tests/unit/test_performance_quick.py',
                '--benchmark-only', '-v'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[green]✅ All benchmarks passed successfully[/green]")
                
                # Show brief statistics
                lines = result.stdout.split('\n')
                for line in lines[-10:]:
                    if 'test_' in line and 'PASSED' in line:
                        console.print(f"[dim]{line}[/dim]")
                        
                return {'status': 'passed', 'output': result.stdout}
            else:
                console.print("[red]❌ Performance issues detected[/red]")
                return {'status': 'failed', 'output': result.stderr}
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return {'status': 'error', 'message': str(e)}