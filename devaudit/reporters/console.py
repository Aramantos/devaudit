"""
Console reporter using Rich for beautiful terminal output.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


class ConsoleReporter:
    """Displays audit results in the console with Rich formatting."""

    def __init__(self, console: Console):
        self.console = console

    def display(self, results: dict):
        """Display audit results to console."""

        # Overview Table
        self._display_overview(results)

        # Detailed sections for each tool
        for tool_name, data in results.items():
            if data.get("installed"):
                self._display_tool_details(tool_name, data)

        # Cleanup Candidates Summary
        self._display_cleanup_summary(results)

    def _display_overview(self, results: dict):
        """Display overview table of all audited tools."""
        table = Table(title="🔍 Environment Overview", show_header=True, header_style="bold cyan")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Version")

        for tool_name, data in results.items():
            if "error" in data:
                status = "[red]❌ Error[/red]"
                version = data.get("error", "Unknown error")[:50]
            elif data.get("installed"):
                status = "[green]✅ Installed[/green]"
                version = data.get("version", "Unknown")
            else:
                status = "[dim]❌ Not Found[/dim]"
                version = "[dim]—[/dim]"

            table.add_row(tool_name, status, version)

        self.console.print(table)
        self.console.print()

    def _display_tool_details(self, tool_name: str, data: dict):
        """Display detailed information for a specific tool."""

        # Python details
        if tool_name == "Python" and data.get("packages"):
            self._display_python_details(data)

        # Node.js details
        elif tool_name == "Node.js/npm" and data.get("global_packages"):
            self._display_node_details(data)

        # Docker details
        elif tool_name == "Docker" and (data.get("containers") or data.get("images")):
            self._display_docker_details(data)

        # Go details
        elif tool_name == "Go" and data.get("modules"):
            self._display_go_details(data)

    def _display_python_details(self, data: dict):
        """Display Python-specific details."""
        packages = data.get("packages", [])
        frameworks = data.get("frameworks", {})
        outdated = data.get("outdated_packages", [])

        if frameworks:
            detected = [fw for fw, installed in frameworks.items() if installed]
            if detected:
                self.console.print(f"[green]🐍 Python Frameworks:[/green] {', '.join(detected)}")

        if outdated:
            self.console.print(f"[yellow]⚠ {len(outdated)} outdated Python packages[/yellow]")

        self.console.print()

    def _display_node_details(self, data: dict):
        """Display Node.js-specific details."""
        packages = data.get("global_packages", [])
        frameworks = data.get("frameworks", {})
        outdated = data.get("outdated_packages", [])

        if frameworks:
            self.console.print(f"[green]📦 Node.js Frameworks:[/green] {', '.join(frameworks.keys())}")

        if outdated:
            self.console.print(f"[yellow]⚠ {len(outdated)} outdated npm packages[/yellow]")

        self.console.print()

    def _display_docker_details(self, data: dict):
        """Display Docker-specific details."""
        stats = data.get("stats", {})

        if stats:
            self.console.print("[cyan]🐳 Docker Summary:[/cyan]")
            self.console.print(f"  Containers: {stats.get('total_containers', 0)} "
                             f"({stats.get('running_containers', 0)} running, "
                             f"{stats.get('stopped_containers', 0)} stopped)")
            self.console.print(f"  Images: {stats.get('total_images', 0)}")
            if stats.get('dangling_images', 0) > 0:
                self.console.print(f"  [yellow]Dangling: {stats['dangling_images']}[/yellow]")

        self.console.print()

    def _display_go_details(self, data: dict):
        """Display Go-specific details."""
        modules = data.get("modules", [])

        if modules:
            self.console.print(f"[cyan]🔷 Go Modules:[/cyan] {len(modules)} modules in current project")

        self.console.print()

    def _display_cleanup_summary(self, results: dict):
        """Display summary of cleanup candidates."""
        all_candidates = []

        for tool_name, data in results.items():
            candidates = data.get("cleanup_candidates", [])
            for candidate in candidates:
                all_candidates.append({
                    "tool": tool_name,
                    **candidate
                })

        if not all_candidates:
            self.console.print("[green]✨ No cleanup candidates found![/green]\n")
            return

        table = Table(title="🧹 Cleanup Candidates", show_header=True, header_style="bold yellow")
        table.add_column("Tool", style="cyan")
        table.add_column("Type")
        table.add_column("Count", justify="right")
        table.add_column("Description")

        for candidate in all_candidates:
            table.add_row(
                candidate["tool"],
                candidate["type"],
                str(candidate["count"]),
                candidate["description"]
            )

        self.console.print(table)
        self.console.print()
