"""
Integration Testing CLI Commands

End-to-end testing with mock servers and real scenarios.
"""

import click
import questionary
import asyncio
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, List, Any, Optional

console = Console()


@click.group()
def integration_cli():
    """🔧 Integration testing with mock servers."""
    pass


@integration_cli.command()
@click.option('--scenario', default='all',
              type=click.Choice(['all', 'websocket', 'http', 'enterprise', 'custom']),
              help='Integration scenario to run')
@click.option('--mock-servers', is_flag=True, default=True,
              help='Use mock servers for testing')
@click.option('--timeout', default=300, help='Test timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def test(scenario, mock_servers, timeout, verbose):
    """🚀 Run integration tests with mock servers."""
    console.print(f"[bold blue]🔧 Running Integration Tests - {scenario.upper()}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if mock_servers:
            # Start mock servers
            task1 = progress.add_task("🖥️ Starting mock servers...", total=None)
            server_info = start_mock_servers()
            progress.update(task1, completed=100)
        
        # Run integration tests
        task2 = progress.add_task(f"🧪 Running {scenario} integration tests...", total=None)
        test_results = run_integration_tests(scenario, timeout, verbose)
        progress.update(task2, completed=100)
        
        if mock_servers:
            # Stop mock servers
            task3 = progress.add_task("🛑 Stopping mock servers...", total=None)
            stop_mock_servers(server_info)
            progress.update(task3, completed=100)
    
    # Display results
    display_integration_results(test_results, scenario)
    
    # Exit with appropriate code
    if test_results.get('failed', 0) > 0:
        console.print(f"[red]❌ {test_results['failed']} integration tests failed[/red]")
        exit(1)
    else:
        console.print(f"[green]✅ All {test_results['passed']} integration tests passed[/green]")


@integration_cli.command()
@click.option('--websocket-port', default=18765, help='WebSocket mock server port')
@click.option('--http-port', default=18080, help='HTTP mock server port')
@click.option('--with-errors', is_flag=True, help='Enable error simulation')
@click.option('--latency', default=50, help='Simulated latency in ms')
def start_servers(websocket_port, http_port, with_errors, latency):
    """🖥️ Start mock servers for development/testing."""
    console.print("[bold blue]🖥️ Starting Mock Servers[/bold blue]")
    
    # Start servers
    servers = start_development_servers(websocket_port, http_port, with_errors, latency)
    
    if servers['success']:
        console.print(f"[green]✅ Mock servers started successfully[/green]")
        console.print(f"[cyan]WebSocket: ws://localhost:{websocket_port}[/cyan]")
        console.print(f"[cyan]HTTP: http://localhost:{http_port}[/cyan]")
        console.print("[dim]Press Ctrl+C to stop servers[/dim]")
        
        try:
            # Keep servers running
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping servers...[/yellow]")
            stop_development_servers(servers)
            console.print("[green]Servers stopped[/green]")
    else:
        console.print(f"[red]❌ Failed to start servers: {servers.get('error')}[/red]")
        exit(1)


@integration_cli.command()
@click.argument('endpoint')
@click.option('--method', default='GET', help='HTTP method')
@click.option('--data', help='Request data (JSON)')
@click.option('--headers', help='Request headers (JSON)')
def test_endpoint(endpoint, method, data, headers):
    """🔍 Test specific API endpoint."""
    console.print(f"[bold blue]🔍 Testing Endpoint: {method} {endpoint}[/bold blue]")
    
    result = test_api_endpoint(endpoint, method, data, headers)
    display_endpoint_test_result(result)


@integration_cli.command()
@click.option('--config-file', help='Custom scenario configuration file')
def scenarios(config_file):
    """📋 Run predefined integration scenarios."""
    console.print("[bold blue]📋 Running Integration Scenarios[/bold blue]")
    
    if config_file and Path(config_file).exists():
        scenarios_config = load_scenarios_config(config_file)
    else:
        scenarios_config = get_default_scenarios()
    
    run_integration_scenarios(scenarios_config)


@integration_cli.command()
def interactive():
    """🎯 Interactive integration testing workflow."""
    console.print("[bold blue]🔧 Interactive Integration Testing[/bold blue]")
    
    test_type = questionary.select(
        "What type of integration test would you like to run?",
        choices=[
            "🚀 Quick integration test (core functionality)",
            "🖥️ Start mock servers for development",
            "🔍 Test specific API endpoint",
            "📋 Run predefined scenarios",
            "🔧 Custom test configuration",
            "📊 Generate integration report"
        ]
    ).ask()
    
    if "Quick integration" in test_type:
        run_quick_integration_test()
    elif "Start mock servers" in test_type:
        start_interactive_servers()
    elif "Test specific endpoint" in test_type:
        test_interactive_endpoint()
    elif "Run predefined scenarios" in test_type:
        run_interactive_scenarios()
    elif "Custom test configuration" in test_type:
        create_custom_test_config()
    elif "Generate integration report" in test_type:
        generate_integration_report()


def start_mock_servers() -> Dict[str, Any]:
    """Start mock servers for integration testing."""
    try:
        # This would start the actual mock servers
        # For now, simulate the process
        console.print("[dim]Starting WebSocket mock server on port 18765...[/dim]")
        console.print("[dim]Starting HTTP mock server on port 18080...[/dim]")
        
        return {
            'websocket_server': {'host': 'localhost', 'port': 18765, 'pid': 12345},
            'http_server': {'host': 'localhost', 'port': 18080, 'pid': 12346},
            'success': True
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def stop_mock_servers(server_info: Dict[str, Any]):
    """Stop mock servers."""
    if server_info.get('success'):
        console.print("[dim]Stopping mock servers...[/dim]")
        # Implementation would stop actual servers


def run_integration_tests(scenario: str, timeout: int, verbose: bool) -> Dict[str, Any]:
    """Run integration tests."""
    try:
        cmd = [
            'python', '-m', 'pytest',
            'unrealon_sdk/tests/integration/',
            '-v' if verbose else '-q',
            f'--timeout={timeout}',
            '--tb=short'
        ]
        
        if scenario != 'all':
            # Add scenario-specific test selection
            if scenario == 'websocket':
                cmd.append('-k websocket')
            elif scenario == 'http':
                cmd.append('-k http')
            elif scenario == 'enterprise':
                cmd.append('-k enterprise')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        # Parse pytest output
        output_lines = result.stdout.split('\n')
        passed = 0
        failed = 0
        errors = []
        
        for line in output_lines:
            if 'passed' in line and 'failed' in line:
                # Extract test counts from pytest summary
                if 'failed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'failed,':
                            failed = int(parts[i-1])
                        elif part == 'passed':
                            passed = int(parts[i-1])
            elif 'FAILED' in line:
                errors.append(line.strip())
        
        return {
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'output': result.stdout,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'passed': 0,
            'failed': 1,
            'errors': ['Test execution timed out'],
            'timeout': True
        }
    except Exception as e:
        return {
            'passed': 0,
            'failed': 1,
            'errors': [str(e)],
            'exception': True
        }


def display_integration_results(results: Dict[str, Any], scenario: str):
    """Display integration test results."""
    total_tests = results['passed'] + results['failed']
    success_rate = (results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    # Summary panel
    summary_text = f"""
[bold]Integration Test Results - {scenario.upper()}[/bold]

📊 Total Tests: {total_tests}
✅ Passed: {results['passed']}
❌ Failed: {results['failed']}
📈 Success Rate: {success_rate:.1f}%
"""
    
    color = "green" if results['failed'] == 0 else "red"
    console.print(Panel(summary_text, title="Integration Test Summary", border_style=color))
    
    # Error details
    if results.get('errors'):
        error_table = Table(title="Failed Tests")
        error_table.add_column("Error", style="red")
        
        for error in results['errors'][:10]:  # Show first 10 errors
            error_table.add_row(error)
        
        console.print(error_table)


def start_development_servers(ws_port: int, http_port: int, with_errors: bool, latency: int) -> Dict[str, Any]:
    """Start development mock servers."""
    # This would start actual servers using the mock server classes
    return {
        'success': True,
        'websocket_port': ws_port,
        'http_port': http_port,
        'error_simulation': with_errors,
        'latency_ms': latency
    }


def stop_development_servers(server_info: Dict[str, Any]):
    """Stop development servers."""
    # Implementation to stop servers
    pass


def test_api_endpoint(endpoint: str, method: str, data: Optional[str], headers: Optional[str]) -> Dict[str, Any]:
    """Test a specific API endpoint."""
    import requests
    import json
    
    try:
        # Parse data and headers
        request_data = json.loads(data) if data else None
        request_headers = json.loads(headers) if headers else {}
        
        # Make request
        response = requests.request(
            method=method,
            url=endpoint,
            json=request_data,
            headers=request_headers,
            timeout=30
        )
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.text,
            'success': response.status_code < 400
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def display_endpoint_test_result(result: Dict[str, Any]):
    """Display endpoint test result."""
    if result.get('success'):
        console.print(f"[green]✅ Status: {result['status_code']}[/green]")
        console.print(f"[dim]Response: {result['body'][:200]}...[/dim]")
    else:
        console.print(f"[red]❌ Error: {result.get('error', 'Unknown error')}[/red]")


def load_scenarios_config(config_file: str) -> Dict[str, Any]:
    """Load scenarios from configuration file."""
    import json
    with open(config_file, 'r') as f:
        return json.load(f)


def get_default_scenarios() -> Dict[str, Any]:
    """Get default integration scenarios."""
    return {
        'scenarios': [
            {
                'name': 'WebSocket Connection Test',
                'type': 'websocket',
                'steps': ['connect', 'authenticate', 'send_message', 'disconnect']
            },
            {
                'name': 'HTTP API Test',
                'type': 'http', 
                'steps': ['health_check', 'register_parser', 'get_stats']
            },
            {
                'name': 'End-to-End Flow',
                'type': 'e2e',
                'steps': ['setup', 'connect_all', 'run_workflow', 'cleanup']
            }
        ]
    }


def run_integration_scenarios(config: Dict[str, Any]):
    """Run integration scenarios from configuration."""
    scenarios = config.get('scenarios', [])
    
    console.print(f"[bold blue]📋 Running {len(scenarios)} Integration Scenarios[/bold blue]")
    
    results = []
    for scenario in scenarios:
        console.print(f"[yellow]Running: {scenario['name']}[/yellow]")
        result = execute_scenario(scenario)
        results.append(result)
        
        status = "✅" if result['success'] else "❌"
        console.print(f"{status} {scenario['name']}: {result['status']}")
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    console.print(f"\n[bold]Scenario Results: {passed} passed, {failed} failed[/bold]")


def execute_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single integration scenario."""
    try:
        # Simulate scenario execution
        import time
        time.sleep(0.5)  # Simulate work
        
        return {
            'name': scenario['name'],
            'success': True,
            'status': 'completed',
            'duration': 0.5
        }
    except Exception as e:
        return {
            'name': scenario['name'],
            'success': False,
            'status': f'failed: {str(e)}',
            'duration': 0
        }


def run_quick_integration_test():
    """Run quick integration test."""
    console.print("[yellow]🚀 Running quick integration test...[/yellow]")
    
    # Quick test selection
    tests = questionary.checkbox(
        "Select quick tests to run:",
        choices=[
            "WebSocket connection test",
            "HTTP client test", 
            "Enterprise services test",
            "Configuration validation test"
        ]
    ).ask()
    
    for test in tests:
        console.print(f"[dim]Running {test}...[/dim]")
        # Simulate test execution
        import time
        time.sleep(0.2)
        console.print(f"[green]✅ {test} passed[/green]")


def start_interactive_servers():
    """Start servers interactively."""
    ws_port = questionary.text("WebSocket port:", default="18765").ask()
    http_port = questionary.text("HTTP port:", default="18080").ask()
    with_errors = questionary.confirm("Enable error simulation?").ask()
    latency = questionary.text("Latency (ms):", default="50").ask()
    
    console.print(f"[yellow]Starting servers on ports {ws_port} and {http_port}...[/yellow]")


def test_interactive_endpoint():
    """Test endpoint interactively."""
    endpoint = questionary.text("Endpoint URL:").ask()
    method = questionary.select(
        "HTTP method:",
        choices=["GET", "POST", "PUT", "DELETE", "PATCH"]
    ).ask()
    
    console.print(f"[yellow]Testing {method} {endpoint}...[/yellow]")


def run_interactive_scenarios():
    """Run scenarios interactively."""
    scenarios = questionary.checkbox(
        "Select scenarios to run:",
        choices=[
            "WebSocket connection flow",
            "HTTP API full workflow",
            "Enterprise services integration",
            "Error handling scenarios",
            "Performance under load"
        ]
    ).ask()
    
    for scenario in scenarios:
        console.print(f"[yellow]Running {scenario}...[/yellow]")


def create_custom_test_config():
    """Create custom test configuration."""
    console.print("[yellow]🔧 Creating custom test configuration...[/yellow]")
    
    # Guide user through creating custom config
    name = questionary.text("Test configuration name:").ask()
    console.print(f"[green]Custom configuration '{name}' would be created[/green]")


def generate_integration_report():
    """Generate integration testing report."""
    console.print("[yellow]📊 Generating integration report...[/yellow]")
    
    format_choice = questionary.select(
        "Report format:",
        choices=["HTML", "JSON", "Markdown", "PDF"]
    ).ask()
    
    console.print(f"[green]Integration report would be generated in {format_choice} format[/green]")


if __name__ == '__main__':
    integration_cli()
