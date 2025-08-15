"""
Test Runner Commands

Test execution for UnrealOn SDK.
"""

import subprocess
from rich.console import Console
from typing import Dict, Any

console = Console()


def run_all_tests() -> Dict[str, Any]:
    """Run all tests."""
    console.print("[bold blue]🧪 Running all tests...[/bold blue]")
    
    with console.status("[bold green]Testing..."):
        try:
            result = subprocess.run([
                'python', '-m', 'pytest',
                'unrealon_sdk/tests/unit/',
                '--tb=short', '-v'
            ], capture_output=True, text=True)
            
            # Parse results
            lines = result.stdout.split('\n')
            passed = failed = 0
            
            for line in lines:
                if 'passed' in line and 'failed' in line:
                    # Extract statistics
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'passed' in part:
                            try:
                                passed = int(parts[i-1])
                            except:
                                pass
                        if 'failed' in part:
                            try:
                                failed = int(parts[i-1])
                            except:
                                pass
            
            if failed == 0:
                console.print(f"[green]✅ All {passed} tests passed successfully[/green]")
                return {'status': 'passed', 'passed': passed, 'failed': 0}
            else:
                console.print(f"[red]❌ {failed} tests failed out of {passed + failed}[/red]")
                return {'status': 'failed', 'passed': passed, 'failed': failed}
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return {'status': 'error', 'message': str(e)}
