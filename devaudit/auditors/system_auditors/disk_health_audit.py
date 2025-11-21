"""
Disk Health Auditor for DevAudit.

Checks disk space, disk health (SMART status where available), and alerts on low space.

Platforms: Windows, macOS, Linux
Requires Admin: No (for basic checks), Yes (for SMART data)
"""

import re
import json
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class DiskHealthAuditor(BaseAuditor):
    """Audit disk health and available space."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Disk Health"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """Disk health checks are always available."""
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """No version for disk health."""
        return None

    def audit(self) -> Dict:
        """
        Perform disk health audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - disks: List[Dict] (Disk information)
                - low_space_count: int (Number of disks with low space)
                - critical_space_count: int (Number of disks with critical space)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Disk Health auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        disk_info = self._get_disk_info()

        if "error" in disk_info:
            return {
                "installed": True,
                "error": disk_info["error"],
                "warnings": disk_info.get("warnings", []),
                "risk_level": RiskLevel.NONE.value,
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "disks": disk_info.get("disks", []),
            "low_space_count": 0,
            "critical_space_count": 0,
            "small_drives_skipped": 0,
            "educational_content": self.get_educational_content()
        }

        # Count disks with low/critical space
        # Skip small drives (<10GB) to avoid false positives from USB sticks
        MIN_SIZE_FOR_ALERTS_GB = 10

        for disk in result["disks"]:
            percent_used = disk.get("percent_used", 0)
            total_gb = disk.get("total_gb", 0)

            # Skip small drives (likely USB sticks or recovery partitions)
            if total_gb < MIN_SIZE_FOR_ALERTS_GB:
                if percent_used >= 85:
                    result["small_drives_skipped"] += 1
                continue

            if percent_used >= 95:
                result["critical_space_count"] += 1
            elif percent_used >= 85:
                result["low_space_count"] += 1

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        if "warnings" in disk_info:
            result["warnings"] = disk_info["warnings"]

        return result

    def _get_disk_info(self) -> Dict:
        """Get disk information for the current platform."""
        if self.platform == "Windows":
            return self._get_disk_info_windows()
        elif self.platform == "Darwin":
            return self._get_disk_info_macos()
        elif self.platform == "Linux":
            return self._get_disk_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_disk_info_windows(self) -> Dict:
        """Get disk information on Windows using PowerShell."""
        result = {}
        warnings = []
        disks = []

        try:
            # Get disk information using Get-PSDrive
            ps_disk_cmd = """
            Get-PSDrive -PSProvider FileSystem |
            Where-Object { $_.Used -ne $null } |
            Select-Object Name, Used, Free |
            ConvertTo-Json
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_disk_cmd],
                timeout=20
            )

            if returncode == 0 and stdout:
                try:
                    disk_data = json.loads(stdout)
                    if isinstance(disk_data, dict):
                        disk_data = [disk_data]

                    for disk in disk_data:
                        name = disk.get("Name", "Unknown")
                        used = disk.get("Used", 0)
                        free = disk.get("Free", 0)
                        total = used + free

                        if total > 0:
                            percent_used = (used / total) * 100
                            disks.append({
                                "name": f"{name}:",
                                "total_gb": round(total / (1024**3), 2),
                                "used_gb": round(used / (1024**3), 2),
                                "free_gb": round(free / (1024**3), 2),
                                "percent_used": round(percent_used, 1)
                            })

                except json.JSONDecodeError:
                    warnings.append("Could not parse disk information")

            result["disks"] = disks

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check disk health: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_disk_info_macos(self) -> Dict:
        """Get disk information on macOS."""
        result = {}
        warnings = []
        disks = []

        try:
            # Use df command to get disk information
            stdout, stderr, returncode = self.run_command(
                ["df", "-H"],
                timeout=10
            )

            if returncode == 0 and stdout:
                lines = stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        # Skip system/virtual filesystems
                        if parts[0].startswith('/dev/disk'):
                            filesystem = parts[0]
                            total_str = parts[1]
                            used_str = parts[2]
                            free_str = parts[3]
                            percent_str = parts[4]
                            mount = parts[5]

                            # Parse sizes (df -H gives human-readable with G/M/K suffixes)
                            total_gb = self._parse_size_to_gb(total_str)
                            used_gb = self._parse_size_to_gb(used_str)
                            free_gb = self._parse_size_to_gb(free_str)
                            percent_used = float(percent_str.replace('%', ''))

                            disks.append({
                                "name": mount,
                                "filesystem": filesystem,
                                "total_gb": total_gb,
                                "used_gb": used_gb,
                                "free_gb": free_gb,
                                "percent_used": percent_used
                            })

            result["disks"] = disks

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check disk health: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_disk_info_linux(self) -> Dict:
        """Get disk information on Linux."""
        result = {}
        warnings = []
        disks = []

        try:
            # Use df command to get disk information
            stdout, stderr, returncode = self.run_command(
                ["df", "-h"],
                timeout=10
            )

            if returncode == 0 and stdout:
                lines = stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        # Skip tmpfs and other virtual filesystems
                        if parts[0].startswith('/dev/'):
                            filesystem = parts[0]
                            total_str = parts[1]
                            used_str = parts[2]
                            free_str = parts[3]
                            percent_str = parts[4]
                            mount = parts[5]

                            # Parse sizes
                            total_gb = self._parse_size_to_gb(total_str)
                            used_gb = self._parse_size_to_gb(used_str)
                            free_gb = self._parse_size_to_gb(free_str)
                            percent_used = float(percent_str.replace('%', ''))

                            disks.append({
                                "name": mount,
                                "filesystem": filesystem,
                                "total_gb": total_gb,
                                "used_gb": used_gb,
                                "free_gb": free_gb,
                                "percent_used": percent_used
                            })

            result["disks"] = disks

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check disk health: {str(e)}",
                "warnings": warnings
            }

        return result

    def _parse_size_to_gb(self, size_str: str) -> float:
        """
        Parse human-readable size to GB.

        Args:
            size_str: Size string like "500G", "1.5T", "200M"

        Returns:
            Size in GB
        """
        size_str = size_str.upper()
        value = float(re.sub(r'[^0-9.]', '', size_str))

        if 'T' in size_str:
            return round(value * 1024, 2)
        elif 'G' in size_str:
            return round(value, 2)
        elif 'M' in size_str:
            return round(value / 1024, 2)
        elif 'K' in size_str:
            return round(value / (1024 * 1024), 2)
        else:
            # Assume bytes
            return round(value / (1024**3), 2)

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on disk space.

        Risk levels:
            - CRITICAL: Any disk >= 95% full (excluding small drives <10GB)
            - HIGH: Any disk >= 90% full (excluding small drives <10GB)
            - MEDIUM: Any disk >= 85% full (excluding small drives <10GB)
            - LOW: Any disk >= 75% full (excluding small drives <10GB)
            - NONE: All disks < 75% full

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        MIN_SIZE_FOR_ALERTS_GB = 10
        critical_count = result.get("critical_space_count", 0)
        low_space_count = result.get("low_space_count", 0)

        if critical_count > 0:
            return RiskLevel.CRITICAL

        # Check for high (90%+) or medium (85%+), skipping small drives
        for disk in result.get("disks", []):
            total_gb = disk.get("total_gb", 0)
            percent_used = disk.get("percent_used", 0)

            # Skip small drives (likely USB sticks or recovery partitions)
            if total_gb < MIN_SIZE_FOR_ALERTS_GB:
                continue

            if percent_used >= 90:
                return RiskLevel.HIGH
            elif percent_used >= 85:
                return RiskLevel.MEDIUM
            elif percent_used >= 75:
                return RiskLevel.LOW

        return RiskLevel.NONE

    def _get_recommendation(self, result: Dict) -> str:
        """
        Get recommendation based on risk level.

        Args:
            result: Audit result dict

        Returns:
            Recommendation string
        """
        MIN_SIZE_FOR_ALERTS_GB = 10
        risk_level = result.get("risk_level", "none")
        critical_count = result.get("critical_space_count", 0)
        low_space_count = result.get("low_space_count", 0)
        small_drives_skipped = result.get("small_drives_skipped", 0)

        # Build note about skipped small drives
        skip_note = f" (Note: {small_drives_skipped} small drive(s) <10GB excluded)" if small_drives_skipped > 0 else ""

        if risk_level == "critical":
            # Only show large drives (>= 10GB) that are critical
            disk_names = [
                d["name"] for d in result.get("disks", [])
                if d.get("percent_used", 0) >= 95 and d.get("total_gb", 0) >= MIN_SIZE_FOR_ALERTS_GB
            ]
            return (
                f"CRITICAL: {critical_count} disk(s) are 95%+ full ({', '.join(disk_names)}){skip_note}. "
                "Free up space IMMEDIATELY to prevent system instability. "
                "HOW TO FIX: Windows Storage Settings → Delete temp files, old downloads, or move files to external storage."
            )
        elif risk_level == "high":
            # Only show large drives (>= 10GB) that are high risk
            disk_names = [
                d["name"] for d in result.get("disks", [])
                if d.get("percent_used", 0) >= 90 and d.get("total_gb", 0) >= MIN_SIZE_FOR_ALERTS_GB
            ]
            return (
                f"Disk(s) are 90%+ full ({', '.join(disk_names)}){skip_note}. "
                "Free up space soon to avoid issues. "
                "HOW TO FIX: Run Disk Cleanup or delete unnecessary files."
            )
        elif risk_level == "medium":
            return (
                f"{low_space_count} disk(s) running low on space (85%+ full){skip_note}. "
                "Consider cleaning up files. "
                "HOW TO FIX: Check Downloads, Temp folders, and old projects."
            )
        elif risk_level == "low":
            return (
                f"Disk space is getting low on some drives (75%+ full){skip_note}. "
                "Monitor usage and clean up when convenient."
            )
        else:
            healthy_msg = "All disks have healthy free space."
            if small_drives_skipped > 0:
                healthy_msg += f" ({small_drives_skipped} small drive(s) <10GB not monitored for alerts)"
            return healthy_msg

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about disk health.

        Returns:
            Dict with educational content from docs/concepts/disk-health.md
        """
        return get_educational_content("disk-health")

    def requires_elevation(self) -> bool:
        """
        Check if disk health auditor requires admin/root.

        Returns:
            False - Basic disk space checks don't require elevation
        """
        return False
