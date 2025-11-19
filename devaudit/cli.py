"""
DevAudit CLI - Main command-line interface
"""

import click
import sys
import os
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Ensure UTF-8 encoding on Windows
if sys.platform == "win32":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

from .auditors import (
    PythonAuditor,
    NodeAuditor,
    DockerAuditor,
    GoAuditor,
    SystemAuditor,
)
from .reporters import ConsoleReporter, SummaryReporter, DetailedReporter, JSONReporter

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="devaudit")
def main():
    """
    DevAudit - Developer Environment Auditing Tool

    Audit your development environment, track dependencies,
    and identify cleanup candidates.
    """
    pass


@main.command()
@click.option('--python', is_flag=True, help='Audit Python only')
@click.option('--node', is_flag=True, help='Audit Node.js only')
@click.option('--docker', is_flag=True, help='Audit Docker only')
@click.option('--go', is_flag=True, help='Audit Go only')
@click.option('--system', is_flag=True, help='Audit system tools only')
@click.option('--target', type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help='Target directory to audit (project-specific scan)')
@click.option('--no-reports', is_flag=True, help='Skip generating report files')
@click.option('--output-dir', type=click.Path(), default=None, help='Custom output directory for reports')
@click.option('--format', type=click.Choice(['text', 'json', 'both']), default='text', help='Output format (text, json, or both)')
def scan(python, node, docker, go, system, target, no_reports, output_dir, format):
    """Scan and audit development environment"""

    if target:
        console.print(f"\n[bold cyan]DevAudit - Project Scan[/bold cyan]")
        console.print(f"[dim]Target: {target}[/dim]\n")
    else:
        console.print("\n[bold cyan]DevAudit - Environment Scan[/bold cyan]\n")

    # Determine which auditors to run
    auditors = []
    if python or node or docker or go or system:
        # Run specific auditors
        if python:
            auditors.append(PythonAuditor(target_dir=target))
        if node:
            auditors.append(NodeAuditor(target_dir=target))
        if docker:
            auditors.append(DockerAuditor(target_dir=target))
        if go:
            auditors.append(GoAuditor(target_dir=target))
        if system:
            auditors.append(SystemAuditor(target_dir=target))
    else:
        # Run all auditors
        auditors = [
            PythonAuditor(target_dir=target),
            NodeAuditor(target_dir=target),
            DockerAuditor(target_dir=target),
            GoAuditor(target_dir=target),
            SystemAuditor(target_dir=target),
        ]

    # Run audits with progress
    results = {}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for auditor in auditors:
            task = progress.add_task(f"Auditing {auditor.name}...", total=None)
            try:
                results[auditor.name] = auditor.audit()
            except Exception as e:
                console.print(f"[red]Error auditing {auditor.name}: {str(e)}[/red]")
                results[auditor.name] = {
                    "installed": False,
                    "error": str(e)
                }
            progress.update(task, completed=True)

    console.print()

    # Handle output format
    if format == 'json':
        # JSON-only output - print to stdout
        json_reporter = JSONReporter()
        print(json_reporter.to_string(results))
        return

    # Display results to console (for text and both formats)
    if format in ['text', 'both']:
        reporter = ConsoleReporter(console)
        reporter.display(results)

    # Generate report files (unless disabled)
    if not no_reports:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Determine output directory
        if output_dir:
            base_dir = Path(output_dir)
        else:
            base_dir = Path.cwd() / "devaudit_reports"

        base_dir.mkdir(parents=True, exist_ok=True)

        # Generate text reports (for text and both formats)
        if format in ['text', 'both']:
            # Generate summary report
            summary_file = base_dir / f"summary_{timestamp}.txt"
            summary_reporter = SummaryReporter()
            summary_reporter.generate(results, summary_file)

            # Generate detailed report
            detailed_file = base_dir / f"detailed_{timestamp}.txt"
            detailed_reporter = DetailedReporter()
            detailed_reporter.generate(results, detailed_file)

            console.print(f"\n[green]Reports saved:[/green]")
            console.print(f"  Summary: {summary_file}")
            console.print(f"  Detailed: {detailed_file}")

        # Generate JSON report (for json and both formats)
        if format in ['json', 'both']:
            json_file = base_dir / f"audit_{timestamp}.json"
            json_reporter = JSONReporter()
            json_reporter.generate(results, json_file)

            console.print(f"  JSON: {json_file}")

        if format in ['text', 'both']:
            console.print()


@main.command()
def fix_docker():
    """Fix common Docker Desktop issues (Windows only)"""
    import platform

    if platform.system() != "Windows":
        console.print("[yellow]This command is only available on Windows[/yellow]")
        return

    console.print("\n[bold cyan]Docker Desktop Fix Utility[/bold cyan]\n")
    console.print("[yellow]This will:[/yellow]")
    console.print("  - Stop Docker Desktop processes")
    console.print("  - Shutdown WSL instances")
    console.print("  - Remove stale lock files")
    console.print("  - Restart Docker service\n")

    if not click.confirm("Continue?"):
        console.print("[dim]Cancelled[/dim]")
        return

    from .fixers.docker_fix import fix_docker_desktop
    fix_docker_desktop(console)


@main.command()
@click.argument('report1', type=click.Path(exists=True))
@click.argument('report2', type=click.Path(exists=True))
def compare(report1, report2):
    """Compare two audit reports"""
    console.print(f"\n[bold cyan]Comparing Reports[/bold cyan]\n")
    console.print(f"Report 1: {report1}")
    console.print(f"Report 2: {report2}\n")
    console.print("[yellow]Compare feature coming in v0.2.0[/yellow]\n")


@main.command()
@click.option('--port', default=8888, help='Port to run server on (default: 8888)')
@click.option('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
@click.option('--no-browser', is_flag=True, help='Do not open browser automatically')
def serve(port, host, no_browser):
    """Start local web dashboard server"""
    console.print(f"\n[bold cyan]DevAudit Dashboard Server[/bold cyan]\n")
    console.print(f"[green]Starting server...[/green]")
    console.print(f"[dim]Dashboard URL:[/dim] http://{host}:{port}")
    console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        from .server import start_server
        start_server(host=host, port=port, open_browser=not no_browser)
    except ImportError as e:
        console.print("[red]Error: Missing dependencies for web server[/red]")
        console.print("[yellow]Install with: pip install 'devaudit[server]'[/yellow]")
        console.print(f"[dim]Details: {str(e)}[/dim]\n")
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server: {str(e)}[/red]\n")


if __name__ == "__main__":
    main()
