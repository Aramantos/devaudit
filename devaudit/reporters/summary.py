"""
Summary report generator - creates concise text reports.
"""

from pathlib import Path
from datetime import datetime


class SummaryReporter:
    """Generates summary text reports."""

    def generate(self, results: dict, output_file: Path):
        """Generate a summary report file."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("DevAudit - Environment Summary")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")

        # Tool Overview
        lines.append("INSTALLED TOOLS")
        lines.append("-" * 60)

        for tool_name, data in results.items():
            if "error" in data:
                status = "❌ ERROR"
                version = data.get("error", "Unknown")[:50]
            elif data.get("installed"):
                status = "✅ Installed"
                version = data.get("version", "Unknown")
            else:
                status = "❌ Not Found"
                version = "—"

            lines.append(f"{tool_name:<20} {status:<15} {version}")

        lines.append("")

        # Cleanup Summary
        cleanup_count = sum(
            len(data.get("cleanup_candidates", []))
            for data in results.values()
        )

        if cleanup_count > 0:
            lines.append("CLEANUP CANDIDATES")
            lines.append("-" * 60)

            for tool_name, data in results.items():
                candidates = data.get("cleanup_candidates", [])
                for candidate in candidates:
                    lines.append(f"  [{tool_name}] {candidate['description']}")

            lines.append("")
        else:
            lines.append("✨ No cleanup candidates found!")
            lines.append("")

        # Write to file
        output_file.write_text("\n".join(lines), encoding="utf-8")
