"""
Backup Status Auditor for DevAudit.

Checks if system backups are configured and recent.

Platforms: Windows, macOS, Linux
Requires Admin: Sometimes (for detailed backup status)
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class BackupAuditor(BaseAuditor):
    """Audit system backup status and configuration."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Backup Status"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """Backup checks are always available."""
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """No version for backup status."""
        return None

    def audit(self) -> Dict:
        """
        Perform backup status audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - backup_configured: bool (If any backup system found)
                - backup_type: str (Windows Backup, Time Machine, etc.)
                - last_backup: str (When last backup ran)
                - days_since_backup: int (Days since last backup)
                - backup_enabled: bool (If backup is active)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Backup auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        backup_info = self._get_backup_info()

        if "error" in backup_info:
            return {
                "installed": True,
                "error": backup_info["error"],
                "warnings": backup_info.get("warnings", []),
                "backup_configured": False,
                "risk_level": RiskLevel.HIGH.value,  # No backups is high risk
                "recommendation": "No backup system detected. Configure backups immediately to protect against data loss.",
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "backup_configured": backup_info.get("backup_configured", False),
            "backup_type": backup_info.get("backup_type", "None"),
            "backup_enabled": backup_info.get("backup_enabled", False),
            "last_backup": backup_info.get("last_backup", "Never"),
            "days_since_backup": backup_info.get("days_since_backup", 999),
            "educational_content": self.get_educational_content()
        }

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        if "warnings" in backup_info:
            result["warnings"] = backup_info["warnings"]

        return result

    def _get_backup_info(self) -> Dict:
        """Get backup information for the current platform."""
        if self.platform == "Windows":
            return self._get_backup_info_windows()
        elif self.platform == "Darwin":
            return self._get_backup_info_macos()
        elif self.platform == "Linux":
            return self._get_backup_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_backup_info_windows(self) -> Dict:
        """Get backup information on Windows."""
        result = {}
        warnings = []

        try:
            # Check Windows Backup status
            ps_backup_cmd = """
            try {
                $Task = Get-ScheduledTask -TaskName "Windows Backup Monitor" -ErrorAction SilentlyContinue
                if ($Task) {
                    $Info = Get-ScheduledTaskInfo -TaskName "Windows Backup Monitor"
                    @{
                        Configured = $true
                        Enabled = $Task.State -eq 'Ready'
                        LastRun = $Info.LastRunTime
                    } | ConvertTo-Json
                } else {
                    @{Configured = $false} | ConvertTo-Json
                }
            } catch {
                @{Configured = $false} | ConvertTo-Json
            }
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_backup_cmd],
                timeout=20
            )

            backup_configured = False
            backup_enabled = False
            last_backup = "Never"
            days_since_backup = 999

            if returncode == 0 and stdout:
                try:
                    backup_data = json.loads(stdout)
                    backup_configured = backup_data.get("Configured", False)

                    if backup_configured:
                        backup_enabled = backup_data.get("Enabled", False)
                        last_run_str = backup_data.get("LastRun", "")

                        if last_run_str:
                            try:
                                # Parse .NET JSON date if needed
                                if "/Date(" in last_run_str:
                                    match = re.search(r'/Date\((\d+)\)/', last_run_str)
                                    if match:
                                        ms_since_epoch = int(match.group(1))
                                        last_run = datetime.fromtimestamp(ms_since_epoch / 1000.0)
                                else:
                                    last_run = datetime.fromisoformat(last_run_str.split('.')[0].replace('T', ' '))

                                last_backup = last_run.strftime("%Y-%m-%d %H:%M:%S")
                                days_since_backup = (datetime.now() - last_run).days
                            except Exception:
                                last_backup = "Unknown"

                except json.JSONDecodeError:
                    warnings.append("Could not parse Windows Backup information")

            # Also check for File History (newer backup system)
            ps_filehistory_cmd = """
            try {
                if (Get-Command Get-WBJob -ErrorAction SilentlyContinue) {
                    $Job = Get-WBJob -Previous 1 -ErrorAction SilentlyContinue
                    if ($Job) {
                        @{
                            Type = 'Windows Backup'
                            LastRun = $Job.EndTime
                        } | ConvertTo-Json
                    }
                }
            } catch {}
            """

            result["backup_configured"] = backup_configured
            result["backup_enabled"] = backup_enabled
            result["backup_type"] = "Windows Backup" if backup_configured else "None"
            result["last_backup"] = last_backup
            result["days_since_backup"] = days_since_backup

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check backup status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_backup_info_macos(self) -> Dict:
        """Get backup information on macOS (Time Machine)."""
        result = {}
        warnings = []

        try:
            # Check Time Machine status using tmutil
            stdout, stderr, returncode = self.run_command(
                ["tmutil", "status"],
                timeout=10
            )

            backup_configured = False
            backup_enabled = False
            last_backup = "Never"
            days_since_backup = 999

            if returncode == 0:
                backup_configured = True
                # Time Machine is available

                # Check if running/enabled
                if "Running = 0" in stdout or "Running = false" in stdout:
                    backup_enabled = False
                else:
                    backup_enabled = True

            # Get latest backup date
            stdout2, stderr2, returncode2 = self.run_command(
                ["tmutil", "latestbackup"],
                timeout=10
            )

            if returncode2 == 0 and stdout2.strip():
                # Extract date from backup path (format: /Volumes/Backup/Backups.backupdb/MachineName/2024-01-15-120000)
                backup_path = stdout2.strip()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2}-\d{6})', backup_path)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        last_run = datetime.strptime(date_str, "%Y-%m-%d-%H%M%S")
                        last_backup = last_run.strftime("%Y-%m-%d %H:%M:%S")
                        days_since_backup = (datetime.now() - last_run).days
                    except ValueError:
                        last_backup = "Unknown"

            result["backup_configured"] = backup_configured
            result["backup_enabled"] = backup_enabled
            result["backup_type"] = "Time Machine" if backup_configured else "None"
            result["last_backup"] = last_backup
            result["days_since_backup"] = days_since_backup

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check Time Machine status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_backup_info_linux(self) -> Dict:
        """Get backup information on Linux."""
        result = {}
        warnings = []

        # Linux has many backup solutions, check for common ones
        backup_configured = False
        backup_type = "None"
        last_backup = "Unknown"
        days_since_backup = 999

        try:
            # Check for common backup tools
            common_backup_tools = {
                "rsnapshot": "/etc/rsnapshot.conf",
                "duplicity": "/etc/duplicity",
                "timeshift": "/etc/timeshift",
                "borg": "~/.config/borg",
                "restic": "~/.config/restic"
            }

            for tool, config_path in common_backup_tools.items():
                path = Path(config_path).expanduser()
                if path.exists():
                    backup_configured = True
                    backup_type = tool.capitalize()
                    warnings.append(f"Found {tool} configuration, but cannot determine last backup time")
                    break

            result["backup_configured"] = backup_configured
            result["backup_enabled"] = backup_configured  # If configured, assume enabled
            result["backup_type"] = backup_type
            result["last_backup"] = last_backup
            result["days_since_backup"] = days_since_backup

            if not backup_configured:
                warnings.append("No common backup tools detected. Consider setting up automated backups.")

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check backup status: {str(e)}",
                "warnings": warnings
            }

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on backup status.

        Risk levels:
            - CRITICAL: No backups configured
            - HIGH: Backups configured but disabled, or 30+ days since last backup
            - MEDIUM: 14-29 days since last backup
            - LOW: 7-13 days since last backup
            - NONE: Backup within last 7 days

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        backup_configured = result.get("backup_configured", False)
        backup_enabled = result.get("backup_enabled", False)
        days_since_backup = result.get("days_since_backup", 999)

        if not backup_configured:
            return RiskLevel.CRITICAL

        if not backup_enabled:
            return RiskLevel.HIGH

        if days_since_backup >= 30:
            return RiskLevel.HIGH
        elif days_since_backup >= 14:
            return RiskLevel.MEDIUM
        elif days_since_backup >= 7:
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE

    def _get_recommendation(self, result: Dict) -> str:
        """
        Get recommendation based on risk level.

        Args:
            result: Audit result dict

        Returns:
            Recommendation string
        """
        risk_level = result.get("risk_level", "none")
        backup_configured = result.get("backup_configured", False)
        backup_enabled = result.get("backup_enabled", False)
        days_since_backup = result.get("days_since_backup", 999)
        backup_type = result.get("backup_type", "None")

        if risk_level == "critical":
            if self.platform == "Windows":
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "HOW TO FIX: Settings → Update & Security → Backup → Add a drive → Enable 'Back up using File History'."
                )
            elif self.platform == "Darwin":
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "HOW TO FIX: System Preferences → Time Machine → Select Backup Disk → Turn On."
                )
            else:
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "HOW TO FIX: Install and configure a backup tool like rsnapshot, timeshift, or borg."
                )

        elif risk_level == "high":
            if not backup_enabled:
                return (
                    f"Backup system ({backup_type}) is configured but DISABLED. "
                    "Enable it immediately. "
                    "HOW TO FIX: Check backup settings and turn on automated backups."
                )
            else:
                return (
                    f"Last backup was {days_since_backup} days ago. "
                    "Run a backup soon to protect recent data. "
                    "HOW TO FIX: Manually trigger a backup or check why automated backups aren't running."
                )

        elif risk_level == "medium":
            return (
                f"Last backup was {days_since_backup} days ago. "
                "Consider backing up more frequently. "
                "HOW TO FIX: Check backup schedule settings."
            )

        elif risk_level == "low":
            return (
                f"Last backup was {days_since_backup} days ago. "
                "Backups are working but could be more frequent."
            )

        else:
            last_backup = result.get("last_backup", "Unknown")
            return f"Backups are configured and recent. Last backup: {last_backup}"

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about backups.

        Returns:
            Dict with educational content from docs/concepts/backups.md
        """
        return get_educational_content("backups")

    def requires_elevation(self) -> bool:
        """
        Check if backup auditor requires admin/root.

        Returns:
            False - Basic backup checks can run without elevation
        """
        return False
