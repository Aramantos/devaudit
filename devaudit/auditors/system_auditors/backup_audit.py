"""
Backup Status Auditor for DevAudit.

Checks if system backups are configured and recent.

Platforms: Windows, macOS, Linux
Requires Admin: Sometimes (for detailed backup status)
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content

logger = logging.getLogger(__name__)


class BackupAuditor(BaseAuditor):
    """Audit system backup status and configuration."""

    # Linux: a backup tool's config file means it is set up, though we cannot
    # read when it last ran from the file alone.
    LINUX_BACKUP_CONFIGS = {
        "rsnapshot": "/etc/rsnapshot.conf",
        "duplicity": "/etc/duplicity",
        "timeshift": "/etc/timeshift",
        "borg": "~/.config/borg",
        "restic": "~/.config/restic",
    }

    # Linux: a systemd timer whose name says backup, or names a backup tool, is
    # a scheduled backup we can read (when it last fired, whether its service
    # succeeded). Worked case: the Raspberry Pi's pi-backup.timer, which read
    # CRITICAL "no backup" before this (M1's first Linux run, 2026-07-04).
    BACKUP_TIMER_WORDS = ("backup", "restic", "borg", "rsnapshot", "duplicity", "timeshift")

    # Debian and Ubuntu enable dpkg-db-backup.timer by default. It copies the
    # package manager's own database, not the user's data, so it is no backup.
    NOT_USER_BACKUPS = frozenset({"dpkg-db-backup.timer"})

    # Unit-file states in which a timer will not fire.
    TIMER_OFF_STATES = frozenset({"disabled", "masked", "masked-runtime", "bad"})

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

        # Honest states (Linux): set up but last run unknown, never run, or the
        # last run failed, and the systemd timer and service behind the backup.
        for key in (
            "status_unknown", "never_run", "last_run_failed", "last_result",
            "backup_timer", "backup_service", "backup_timers",
        ):
            if key in backup_info:
                result[key] = backup_info[key]

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
        """Get backup information on Linux.

        A scheduled backup (a systemd timer) is read first, because systemd
        says when it last ran and whether it succeeded. A backup tool's config
        file comes second: it is set up, but when it last ran is unknown.
        """
        warnings = []

        try:
            timers = self._find_backup_timers_linux()
            if timers:
                return self._backup_info_from_timer(timers)

            for tool, config_path in self.LINUX_BACKUP_CONFIGS.items():
                if Path(config_path).expanduser().exists():
                    logger.info("found %s configuration at %s, last run unknown", tool, config_path)
                    return {
                        "backup_configured": True,
                        "backup_enabled": True,  # Configured, assume enabled
                        "backup_type": tool.capitalize(),
                        "last_backup": "Unknown",
                        "days_since_backup": None,
                        "status_unknown": True,
                        "warnings": [f"Found {tool} configuration, but cannot determine last backup time"],
                    }

            warnings.append("No common backup tools detected. Consider setting up automated backups.")
            return {
                "backup_configured": False,
                "backup_enabled": False,
                "backup_type": "None",
                "last_backup": "Unknown",
                "days_since_backup": 999,
                "warnings": warnings,
            }

        except Exception as e:
            logger.warning("backup check failed: %s", e)
            return {
                "error": f"Failed to check backup status: {str(e)}",
                "warnings": warnings
            }

    def _find_backup_timers_linux(self) -> List[Dict]:
        """Every systemd timer that looks like a user-data backup, with its last run."""
        systemctl = self.find_command("systemctl")
        if not systemctl:
            return []
        stdout, stderr, returncode = self.run_command(
            [systemctl, "list-unit-files", "--type=timer", "--no-legend", "--no-pager"],
            timeout=10
        )
        if returncode != 0:
            # e.g. a container not booted with systemd
            logger.debug("systemctl list-unit-files failed (rc %s): %s", returncode, stderr.strip())
            return []

        timers = []
        for line in stdout.splitlines():
            parts = line.split()
            if len(parts) < 2 or not parts[0].endswith(".timer"):
                continue
            name, state = parts[0], parts[1]
            if name in self.NOT_USER_BACKUPS:
                continue
            if not any(word in name.lower() for word in self.BACKUP_TIMER_WORDS):
                continue
            timer_props = self._systemctl_show(systemctl, name, "Unit,LastTriggerUSec")
            service = timer_props.get("Unit") or name[: -len(".timer")] + ".service"
            service_props = self._systemctl_show(systemctl, service, "Result")
            timers.append({
                "timer": name,
                "service": service,
                "enabled": state not in self.TIMER_OFF_STATES,
                "last_run": self._parse_systemd_time(timer_props.get("LastTriggerUSec", "")),
                "result": service_props.get("Result", ""),
            })
        logger.debug("backup timers found: %s", [t["timer"] for t in timers])
        return timers

    def _systemctl_show(self, systemctl: str, unit: str, properties: str) -> Dict[str, str]:
        """`systemctl show` as a dict (Key=Value lines). Empty when it fails."""
        stdout, stderr, returncode = self.run_command(
            [systemctl, "show", unit, f"--property={properties}", "--no-pager"],
            timeout=10
        )
        if returncode != 0:
            logger.debug("systemctl show %s failed (rc %s): %s", unit, returncode, stderr.strip())
            return {}
        return dict(line.split("=", 1) for line in stdout.splitlines() if "=" in line)

    @staticmethod
    def _parse_systemd_time(value: str) -> Optional[datetime]:
        """'Wed 2026-11-11 03:45:47 GMT' -> datetime. 'n/a' or empty (never fired) -> None.

        The zone is dropped: a day count does not need it.
        """
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value or "")
        if not match:
            return None
        return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")

    def _backup_info_from_timer(self, timers: List[Dict]) -> Dict:
        """Read the backup from its timers: an enabled one, most recently run, leads."""
        timers = sorted(
            timers,
            key=lambda t: (t["enabled"], t["last_run"] or datetime.min),
            reverse=True,
        )
        lead = timers[0]
        info = {
            "backup_configured": True,
            "backup_enabled": lead["enabled"],
            "backup_type": f"systemd timer {lead['timer']}",
            "backup_timer": lead["timer"],
            "backup_service": lead["service"],
            "backup_timers": [t["timer"] for t in timers],
        }
        if lead["last_run"] is None:
            info["never_run"] = True
            info["last_backup"] = "Never"
            info["days_since_backup"] = None
        else:
            info["last_backup"] = lead["last_run"].strftime("%Y-%m-%d %H:%M:%S")
            info["days_since_backup"] = max(0, (datetime.now() - lead["last_run"]).days)
        if lead["result"] and lead["result"] != "success":
            info["last_run_failed"] = True
            info["last_result"] = lead["result"]
        return info

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

        # The last run failed, or it has never run: no recent copy exists.
        if result.get("last_run_failed") or result.get("never_run"):
            return RiskLevel.HIGH

        # Set up, but when it last ran cannot be read: MEDIUM, never a made-up
        # day count (honest degradation, context.md Decision 4).
        if result.get("status_unknown") or days_since_backup is None:
            return RiskLevel.MEDIUM

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

        # A red says what was checked, so it names what is missing (caretaker's
        # read of John's PC, 2026-11-12: its CRITICAL is true, and should say why).
        if risk_level == "critical":
            if self.platform == "Windows":
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "(DevAudit looked for Windows Backup. It does not yet read File History, "
                    "system images or other backup apps.) "
                    "HOW TO FIX: Settings → Update & Security → Backup → Add a drive → Enable 'Back up using File History'."
                )
            elif self.platform == "Darwin":
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "(DevAudit looked for Time Machine.) "
                    "HOW TO FIX: System Preferences → Time Machine → Select Backup Disk → Turn On."
                )
            else:
                return (
                    "CRITICAL: No backup system detected! Your data is at risk. "
                    "(DevAudit looked for a systemd timer named for a backup, and for rsnapshot, "
                    "duplicity, timeshift, borg and restic configuration.) "
                    "HOW TO FIX: Install and configure a backup tool like rsnapshot, timeshift, or borg, "
                    "or run your own backup script from a systemd timer with 'backup' in its name "
                    "(DevAudit reads when such a timer last ran)."
                )

        timer = result.get("backup_timer")
        service = result.get("backup_service")

        if risk_level == "high" and backup_enabled and result.get("last_run_failed"):
            return (
                f"The last run of {service} FAILED (systemd result: {result.get('last_result')}), "
                "so your most recent backup may be missing. "
                f"HOW TO CHECK: journalctl -u {service} -n 50"
            )

        if risk_level == "high" and backup_enabled and result.get("never_run"):
            return (
                f"Backup ({backup_type}) is set up but has not run yet, so no backup copy exists. "
                f"HOW TO CHECK: systemctl list-timers {timer}"
            )

        if risk_level == "medium" and (result.get("status_unknown") or days_since_backup is None):
            return (
                f"Backup ({backup_type}) is configured, but DevAudit cannot read when it last ran. "
                "Check its logs to confirm backups are completing."
            )

        if risk_level == "high":
            if not backup_enabled:
                how = f"sudo systemctl enable --now {timer}" if timer else "Check backup settings and turn on automated backups."
                return (
                    f"Backup system ({backup_type}) is configured but DISABLED. "
                    "Enable it immediately. "
                    f"HOW TO FIX: {how}"
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
            text = f"Backups are configured and recent. Last backup: {last_backup}"
            if timer:
                # Found by the timer's name: that proves it ran, not what it copies.
                text += (
                    f". DevAudit reads that {timer} ran, not what it copies: "
                    "check it covers the files you care about."
                )
            return text

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
