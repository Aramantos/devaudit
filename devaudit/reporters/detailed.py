"""
Detailed report generator - creates comprehensive text reports.
"""

import json
from pathlib import Path
from datetime import datetime


class DetailedReporter:
    """Generates detailed text reports with full audit data."""

    def generate(self, results: dict, output_file: Path):
        """Generate a detailed report file."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("DevAudit - Detailed Environment Report")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # Detailed sections for each tool
        for tool_name, data in results.items():
            lines.append("")
            lines.append(f"{'=' * 80}")
            lines.append(f"{tool_name}")
            lines.append(f"{'=' * 80}")

            if "error" in data:
                lines.append(f"❌ ERROR: {data['error']}")
                continue

            if not data.get("installed"):
                lines.append("❌ Not installed")
                continue

            lines.append(f"✅ Installed: {data.get('version', 'Unknown version')}")
            lines.append("")

            # Tool-specific details
            if tool_name == "Python":
                self._add_python_details(lines, data)
            elif tool_name == "Node.js/npm":
                self._add_node_details(lines, data)
            elif tool_name == "Docker":
                self._add_docker_details(lines, data)
            elif tool_name == "Go":
                self._add_go_details(lines, data)
            elif tool_name == "System":
                self._add_system_details(lines, data)

        # Cleanup section
        lines.append("")
        lines.append(f"{'=' * 80}")
        lines.append("CLEANUP CANDIDATES")
        lines.append(f"{'=' * 80}")
        lines.append("")

        cleanup_found = False
        for tool_name, data in results.items():
            candidates = data.get("cleanup_candidates", [])
            if candidates:
                cleanup_found = True
                lines.append(f"{tool_name}:")
                for candidate in candidates:
                    lines.append(f"  • {candidate['description']}")
                    if "total_size_mb" in candidate:
                        lines.append(f"    Total size: {candidate['total_size_mb']:.1f} MB")
                lines.append("")

        if not cleanup_found:
            lines.append("✨ No cleanup candidates found!")

        # Write to file
        output_file.write_text("\n".join(lines), encoding="utf-8")

    def _add_python_details(self, lines: list, data: dict):
        """Add Python-specific details."""
        packages = data.get("packages", [])
        frameworks = data.get("frameworks", {})
        outdated = data.get("outdated_packages", [])

        if frameworks:
            lines.append("Frameworks Detected:")
            for fw, installed in frameworks.items():
                status = "✅" if installed else "❌"
                lines.append(f"  {status} {fw}")
            lines.append("")

        if packages:
            lines.append(f"Installed Packages ({len(packages)} total):")
            for pkg in packages[:20]:  # Show first 20
                lines.append(f"  • {pkg['name']} ({pkg['version']})")
            if len(packages) > 20:
                lines.append(f"  ... and {len(packages) - 20} more")
            lines.append("")

        if outdated:
            lines.append(f"Outdated Packages ({len(outdated)} total):")
            for pkg in outdated[:10]:  # Show first 10
                lines.append(f"  • {pkg['name']}: {pkg['current']} → {pkg['latest']}")
            if len(outdated) > 10:
                lines.append(f"  ... and {len(outdated) - 10} more")

    def _add_node_details(self, lines: list, data: dict):
        """Add Node.js-specific details."""
        packages = data.get("global_packages", [])
        frameworks = data.get("frameworks", {})
        outdated = data.get("outdated_packages", [])

        if frameworks:
            lines.append("Frameworks Detected:")
            for fw in frameworks.keys():
                lines.append(f"  ✅ {fw}")
            lines.append("")

        if packages:
            lines.append(f"Global Packages ({len(packages)} total):")
            for pkg in packages[:20]:
                lines.append(f"  • {pkg['name']} ({pkg['version']})")
            if len(packages) > 20:
                lines.append(f"  ... and {len(packages) - 20} more")
            lines.append("")

        if outdated:
            lines.append(f"Outdated Packages ({len(outdated)} total):")
            for pkg in outdated[:10]:
                lines.append(f"  • {pkg['name']}: {pkg['current']} → {pkg['latest']}")
            if len(outdated) > 10:
                lines.append(f"  ... and {len(outdated) - 10} more")

    def _add_docker_details(self, lines: list, data: dict):
        """Add Docker-specific details."""
        stats = data.get("stats", {})
        containers = data.get("containers", [])
        images = data.get("images", [])

        lines.append("Statistics:")
        lines.append(f"  Containers: {stats.get('total_containers', 0)} "
                    f"({stats.get('running_containers', 0)} running, "
                    f"{stats.get('stopped_containers', 0)} stopped)")
        lines.append(f"  Images: {stats.get('total_images', 0)}")
        lines.append(f"  Dangling Images: {stats.get('dangling_images', 0)}")
        lines.append("")

        if containers:
            lines.append(f"Containers ({len(containers)} total):")
            for container in containers[:10]:
                status = "🟢" if container['status'].startswith("Up") else "🔴"
                lines.append(f"  {status} {container['name']} ({container['image']})")
            if len(containers) > 10:
                lines.append(f"  ... and {len(containers) - 10} more")
            lines.append("")

        if images:
            lines.append(f"Images ({len(images)} total):")
            for image in images[:10]:
                lines.append(f"  • {image['name']} ({image['size']})")
            if len(images) > 10:
                lines.append(f"  ... and {len(images) - 10} more")

    def _add_go_details(self, lines: list, data: dict):
        """Add Go-specific details."""
        modules = data.get("modules", [])
        cache_path = data.get("module_cache_path")

        if cache_path:
            lines.append(f"Module Cache: {cache_path}")
            lines.append("")

        if modules:
            lines.append(f"Modules ({len(modules)} total):")
            for module in modules[:15]:
                lines.append(f"  • {module}")
            if len(modules) > 15:
                lines.append(f"  ... and {len(modules) - 15} more")

    def _add_system_details(self, lines: list, data: dict):
        """Add system-specific details."""
        platform = data.get("platform", {})
        tools = data.get("tools", {})

        lines.append("Platform:")
        lines.append(f"  System: {platform.get('system', 'Unknown')}")
        lines.append(f"  Release: {platform.get('release', 'Unknown')}")
        lines.append(f"  Machine: {platform.get('machine', 'Unknown')}")
        lines.append("")

        lines.append("Development Tools:")
        for tool_name, tool_data in tools.items():
            if tool_data.get("installed"):
                lines.append(f"  ✅ {tool_name}: {tool_data.get('version', 'Unknown')}")
            else:
                lines.append(f"  ❌ {tool_name}")
