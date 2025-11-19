"""
JSON report generator for programmatic access and dashboard integration.
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime


class JSONReporter:
    """Generate JSON reports for machine consumption."""

    def generate(self, results: Dict, output_file: Path):
        """
        Generate a JSON report file.

        Args:
            results: Audit results dictionary
            output_file: Path to output JSON file
        """
        report_data = self._prepare_report_data(results)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

    def to_string(self, results: Dict) -> str:
        """
        Return JSON report as string.

        Args:
            results: Audit results dictionary

        Returns:
            JSON string
        """
        report_data = self._prepare_report_data(results)
        return json.dumps(report_data, indent=2, default=str)

    def _prepare_report_data(self, results: Dict) -> Dict:
        """
        Prepare report data with metadata.

        Args:
            results: Raw audit results

        Returns:
            Formatted report data with metadata
        """
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool": "DevAudit",
                "version": "0.2.0",
                "format_version": "1.0"
            },
            "summary": self._generate_summary(results),
            "results": results
        }

    def _generate_summary(self, results: Dict) -> Dict:
        """
        Generate summary statistics from results.

        Args:
            results: Audit results dictionary

        Returns:
            Summary statistics
        """
        tools_detected = sum(1 for r in results.values() if r.get('installed', False))
        total_tools = len(results)

        total_packages = 0
        total_outdated = 0
        total_cleanup = 0

        for tool_result in results.values():
            if isinstance(tool_result, dict):
                packages = tool_result.get('packages', [])
                total_packages += len(packages) if isinstance(packages, list) else 0

                outdated = tool_result.get('outdated_packages', [])
                total_outdated += len(outdated) if isinstance(outdated, list) else 0

                cleanup = tool_result.get('cleanup_candidates', [])
                total_cleanup += len(cleanup) if isinstance(cleanup, list) else 0

        return {
            "tools_detected": tools_detected,
            "total_tools": total_tools,
            "total_packages": total_packages,
            "total_outdated_packages": total_outdated,
            "total_cleanup_candidates": total_cleanup
        }
