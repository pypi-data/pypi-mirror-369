"""
System Diagnostics CLI Commands

Health checks, troubleshooting, and system analysis.
"""

import click
import questionary
import subprocess
import json
import psutil
import platform
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, List, Any, Optional

console = Console()


@click.group()
def diagnostics_cli():
    """🩺 System diagnostics and health checks."""
    pass


@diagnostics_cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--output', '-o', help='Save report to file')
def health(verbose, output):
    """🩺 Comprehensive system health check."""
    console.print("[bold blue]🩺 Running System Health Check[/bold blue]")
    
    health_report = run_health_check(verbose)
    display_health_report(health_report)
    
    if output:
        save_health_report(health_report, output)
    
    # Exit code based on health status
    if health_report['overall_status'] == 'healthy':
        console.print("[green]✅ System is healthy[/green]")
        exit(0)
    elif health_report['overall_status'] == 'warning':
        console.print("[yellow]⚠️ System has warnings[/yellow]")
        exit(0)
    else:
        console.print("[red]❌ System has critical issues[/red]")
        exit(1)


@diagnostics_cli.command()
@click.option('--module', help='Specific module to diagnose')
@click.option('--fix', is_flag=True, help='Attempt to fix issues automatically')
def troubleshoot(module, fix):
    """🔧 Troubleshoot common issues."""
    console.print("[bold blue]🔧 Running Troubleshooting Analysis[/bold blue]")
    
    issues = diagnose_issues(module)
    display_troubleshooting_results(issues)
    
    if fix and issues['fixable_issues']:
        console.print("[yellow]🔧 Attempting to fix issues...[/yellow]")
        fix_results = auto_fix_issues(issues['fixable_issues'])
        display_fix_results(fix_results)


@diagnostics_cli.command()
@click.option('--include-system', is_flag=True, help='Include system information')
@click.option('--include-network', is_flag=True, help='Include network diagnostics')
def info(include_system, include_network):
    """📋 Show detailed system information."""
    console.print("[bold blue]📋 System Information[/bold blue]")
    
    info_data = collect_system_info(include_system, include_network)
    display_system_info(info_data)


@diagnostics_cli.command()
@click.option('--test-type', default='all',
              type=click.Choice(['all', 'connectivity', 'performance', 'security']),
              help='Type of connectivity test')
def connectivity(test_type):
    """🌐 Test network connectivity and services."""
    console.print(f"[bold blue]🌐 Testing Connectivity - {test_type.upper()}[/bold blue]")
    
    connectivity_results = test_connectivity(test_type)
    display_connectivity_results(connectivity_results)


@diagnostics_cli.command()
def interactive():
    """🎯 Interactive diagnostics workflow."""
    console.print("[bold blue]🩺 Interactive System Diagnostics[/bold blue]")
    
    diagnostic_type = questionary.select(
        "What type of diagnostic would you like to run?",
        choices=[
            "🩺 Full health check (comprehensive analysis)",
            "🔧 Troubleshoot specific issue",
            "📋 System information report",
            "🌐 Network connectivity test",
            "⚡ Performance analysis",
            "🔒 Security configuration check"
        ]
    ).ask()
    
    if "Full health check" in diagnostic_type:
        run_interactive_health_check()
    elif "Troubleshoot specific" in diagnostic_type:
        run_interactive_troubleshooting()
    elif "System information" in diagnostic_type:
        run_interactive_system_info()
    elif "Network connectivity" in diagnostic_type:
        run_interactive_connectivity_test()
    elif "Performance analysis" in diagnostic_type:
        run_interactive_performance_analysis()
    elif "Security configuration" in diagnostic_type:
        run_interactive_security_check()


def run_health_check(verbose: bool = False) -> Dict[str, Any]:
    """Run comprehensive health check."""
    health_checks = {
        'python_environment': check_python_environment(),
        'dependencies': check_dependencies(),
        'sdk_installation': check_sdk_installation(),
        'configuration': check_configuration(),
        'file_permissions': check_file_permissions(),
        'system_resources': check_system_resources(),
        'network_access': check_network_access()
    }
    
    # Calculate overall status
    statuses = [check['status'] for check in health_checks.values()]
    if any(status == 'critical' for status in statuses):
        overall_status = 'critical'
    elif any(status == 'warning' for status in statuses):
        overall_status = 'warning'
    else:
        overall_status = 'healthy'
    
    return {
        'overall_status': overall_status,
        'checks': health_checks,
        'summary': generate_health_summary(health_checks),
        'timestamp': get_timestamp()
    }


def check_python_environment() -> Dict[str, Any]:
    """Check Python environment health."""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append(f"Python {sys.version} is below minimum requirement (3.9+)")
    
    # Check virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        issues.append("Not running in virtual environment (recommended)")
    
    # Check pip version
    try:
        pip_version = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                   capture_output=True, text=True)
        if pip_version.returncode != 0:
            issues.append("pip is not accessible")
    except Exception:
        issues.append("pip check failed")
    
    return {
        'status': 'critical' if any('minimum requirement' in issue for issue in issues) else 'warning' if issues else 'healthy',
        'issues': issues,
        'python_version': sys.version,
        'virtual_env': in_venv
    }


def check_dependencies() -> Dict[str, Any]:
    """Check project dependencies."""
    issues = []
    missing_deps = []
    
    # Check core dependencies
    required_deps = [
        'pydantic', 'aiohttp', 'python-socketio', 'click', 'questionary', 'rich'
    ]
    
    for dep in required_deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
    
    # Check for outdated packages
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], 
                              capture_output=True, text=True)
        if result.stdout and len(result.stdout.split('\n')) > 2:
            issues.append("Some packages may be outdated")
    except Exception:
        pass
    
    return {
        'status': 'critical' if missing_deps else 'warning' if issues else 'healthy',
        'issues': issues,
        'missing_dependencies': missing_deps
    }


def check_sdk_installation() -> Dict[str, Any]:
    """Check SDK installation."""
    issues = []
    
    # Check if unrealon_sdk module is importable
    try:
        import unrealon_sdk
        sdk_path = Path(unrealon_sdk.__file__).parent
    except ImportError:
        issues.append("UnrealOn SDK is not properly installed")
        return {'status': 'critical', 'issues': issues}
    
    # Check core modules
    core_modules = ['core', 'internal', 'enterprise', 'dto']
    for module in core_modules:
        module_path = sdk_path / module
        if not module_path.exists():
            issues.append(f"Missing core module: {module}")
    
    # Check test directory
    test_path = sdk_path / 'tests'
    if not test_path.exists():
        issues.append("Test directory not found")
    
    return {
        'status': 'critical' if any('Missing core module' in issue for issue in issues) else 'warning' if issues else 'healthy',
        'issues': issues,
        'sdk_path': str(sdk_path)
    }


def check_configuration() -> Dict[str, Any]:
    """Check configuration validity."""
    issues = []
    
    try:
        from unrealon_sdk.src.core.config import AdapterConfig
        
        # Test config creation
        test_config = AdapterConfig(
            api_key="test_key_validation",
            server_url="ws://localhost:8080",
            parser_id="test_parser",
            parser_name="Test Parser"
        )
        
    except Exception as e:
        issues.append(f"Configuration validation failed: {str(e)}")
    
    return {
        'status': 'critical' if issues else 'healthy',
        'issues': issues
    }


def check_file_permissions() -> Dict[str, Any]:
    """Check file permissions."""
    issues = []
    
    # Check write permissions in current directory
    current_dir = Path.cwd()
    if not current_dir.is_dir() or not os.access(current_dir, os.W_OK):
        issues.append("No write permission in current directory")
    
    # Check SDK directory permissions
    try:
        import unrealon_sdk
        sdk_path = Path(unrealon_sdk.__file__).parent
        if not os.access(sdk_path, os.R_OK):
            issues.append("No read permission for SDK directory")
    except Exception:
        pass
    
    return {
        'status': 'warning' if issues else 'healthy',
        'issues': issues
    }


def check_system_resources() -> Dict[str, Any]:
    """Check system resources."""
    issues = []
    
    # Check memory
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        issues.append(f"High memory usage: {memory.percent:.1f}%")
    
    # Check disk space
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        issues.append(f"Low disk space: {disk.percent:.1f}% used")
    
    # Check CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        issues.append(f"High CPU usage: {cpu_percent:.1f}%")
    
    return {
        'status': 'warning' if issues else 'healthy',
        'issues': issues,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
        'cpu_percent': cpu_percent
    }


def check_network_access() -> Dict[str, Any]:
    """Check network access."""
    issues = []
    
    # Test DNS resolution
    try:
        import socket
        socket.gethostbyname('google.com')
    except Exception:
        issues.append("DNS resolution failed")
    
    # Test HTTP connectivity
    try:
        import requests
        response = requests.get('https://httpbin.org/get', timeout=10)
        if response.status_code != 200:
            issues.append("HTTP connectivity issues")
    except Exception:
        issues.append("HTTP connectivity failed")
    
    return {
        'status': 'warning' if issues else 'healthy',
        'issues': issues
    }


def generate_health_summary(checks: Dict[str, Any]) -> Dict[str, Any]:
    """Generate health check summary."""
    total_checks = len(checks)
    healthy_checks = sum(1 for check in checks.values() if check['status'] == 'healthy')
    warning_checks = sum(1 for check in checks.values() if check['status'] == 'warning')
    critical_checks = sum(1 for check in checks.values() if check['status'] == 'critical')
    
    return {
        'total_checks': total_checks,
        'healthy': healthy_checks,
        'warnings': warning_checks,
        'critical': critical_checks,
        'health_score': (healthy_checks / total_checks) * 100
    }


def display_health_report(report: Dict[str, Any]):
    """Display health check report."""
    summary = report['summary']
    
    # Health score panel
    health_score = summary['health_score']
    if health_score >= 90:
        score_color = "green"
        score_emoji = "💚"
    elif health_score >= 70:
        score_color = "yellow"
        score_emoji = "💛"
    else:
        score_color = "red"
        score_emoji = "❤️"
    
    summary_text = f"""
[bold]System Health Report[/bold]

{score_emoji} Health Score: {health_score:.1f}%
✅ Healthy: {summary['healthy']}/{summary['total_checks']}
⚠️  Warnings: {summary['warnings']}
❌ Critical: {summary['critical']}

[bold]Overall Status: {report['overall_status'].upper()}[/bold]
"""
    
    console.print(Panel(summary_text, title="Health Check Summary", border_style=score_color))
    
    # Detailed checks table
    table = Table(title="Detailed Health Checks")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Issues", style="yellow")
    
    for check_name, check_data in report['checks'].items():
        status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}
        status_display = f"{status_emoji.get(check_data['status'], '❓')} {check_data['status']}"
        issues_display = "; ".join(check_data['issues']) if check_data['issues'] else "None"
        
        table.add_row(
            check_name.replace('_', ' ').title(),
            status_display,
            issues_display[:100] + "..." if len(issues_display) > 100 else issues_display
        )
    
    console.print(table)


def diagnose_issues(module: Optional[str]) -> Dict[str, Any]:
    """Diagnose common issues."""
    # Implementation for issue diagnosis
    return {
        'issues_found': [],
        'fixable_issues': [],
        'recommendations': []
    }


def display_troubleshooting_results(issues: Dict[str, Any]):
    """Display troubleshooting results."""
    # Implementation for displaying troubleshooting results
    pass


def auto_fix_issues(fixable_issues: List[Dict]) -> Dict[str, Any]:
    """Automatically fix issues."""
    # Implementation for auto-fixing issues
    return {'fixed': [], 'failed': []}


def display_fix_results(results: Dict[str, Any]):
    """Display fix results."""
    # Implementation for displaying fix results
    pass


def collect_system_info(include_system: bool, include_network: bool) -> Dict[str, Any]:
    """Collect comprehensive system information."""
    info = {
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'platform': platform.platform()
        },
        'sdk': get_sdk_info()
    }
    
    if include_system:
        info['system'] = get_system_info()
    
    if include_network:
        info['network'] = get_network_info()
    
    return info


def get_sdk_info() -> Dict[str, Any]:
    """Get SDK information."""
    try:
        import unrealon_sdk
        return {
            'version': getattr(unrealon_sdk, '__version__', 'unknown'),
            'path': str(Path(unrealon_sdk.__file__).parent)
        }
    except ImportError:
        return {'error': 'SDK not installed'}


def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        'cpu_count': psutil.cpu_count(),
        'memory_gb': psutil.virtual_memory().total / (1024**3),
        'disk_gb': psutil.disk_usage('/').total / (1024**3),
        'platform': platform.platform(),
        'python_version': platform.python_version()
    }


def get_network_info() -> Dict[str, Any]:
    """Get network information."""
    return {
        'hostname': platform.node(),
        'network_interfaces': len(psutil.net_if_addrs())
    }


def display_system_info(info: Dict[str, Any]):
    """Display system information."""
    # Create info panels
    for category, data in info.items():
        if isinstance(data, dict):
            info_text = "\n".join([f"{k}: {v}" for k, v in data.items()])
            console.print(Panel(info_text, title=category.title()))


def test_connectivity(test_type: str) -> Dict[str, Any]:
    """Test network connectivity."""
    # Implementation for connectivity testing
    return {'status': 'healthy', 'tests': []}


def display_connectivity_results(results: Dict[str, Any]):
    """Display connectivity test results."""
    # Implementation for displaying connectivity results
    pass


def get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().isoformat()


def save_health_report(report: Dict[str, Any], output: str):
    """Save health report to file."""
    with open(output, 'w') as f:
        json.dump(report, f, indent=2)
    console.print(f"[green]Health report saved to {output}[/green]")


def run_interactive_health_check():
    """Run interactive health check."""
    verbose = questionary.confirm("Enable verbose output?").ask()
    console.print("[yellow]🩺 Running comprehensive health check...[/yellow]")


def run_interactive_troubleshooting():
    """Run interactive troubleshooting."""
    module = questionary.text("Module to diagnose (optional):").ask()
    console.print(f"[yellow]🔧 Troubleshooting {module or 'all modules'}...[/yellow]")


def run_interactive_system_info():
    """Run interactive system info."""
    include_system = questionary.confirm("Include system information?").ask()
    include_network = questionary.confirm("Include network information?").ask()
    console.print("[yellow]📋 Collecting system information...[/yellow]")


def run_interactive_connectivity_test():
    """Run interactive connectivity test."""
    test_type = questionary.select(
        "Connectivity test type:",
        choices=["all", "connectivity", "performance", "security"]
    ).ask()
    console.print(f"[yellow]🌐 Testing {test_type} connectivity...[/yellow]")


def run_interactive_performance_analysis():
    """Run interactive performance analysis."""
    console.print("[yellow]⚡ Running performance analysis...[/yellow]")


def run_interactive_security_check():
    """Run interactive security check."""
    console.print("[yellow]🔒 Checking security configuration...[/yellow]")


# Import os for file permissions check
import os


if __name__ == '__main__':
    diagnostics_cli()
