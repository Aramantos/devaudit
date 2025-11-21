"""
OS Update Auditor for DevAudit.

Checks if the operating system is up-to-date and detects pending updates.

Platforms: Windows, macOS, Linux
Requires Admin: Yes (on most platforms for accurate update detection)
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class OSUpdateAuditor(BaseAuditor):
    """Audit OS update status and pending updates."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "OS Updates"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """
        Check if OS update auditor can run.

        OS updates are always "available" (every OS has update mechanism),
        but we might need proper permissions to check them.
        """
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """Get current OS version."""
        update_info = self._get_update_info()
        return update_info.get("os_version")

    def audit(self) -> Dict:
        """
        Perform OS update audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - os_name: str (Operating system name)
                - os_version: str (Current OS version)
                - last_update_check: str (When updates were last checked)
                - pending_updates: List[Dict] (Available updates)
                - update_count: int (Number of pending updates)
                - security_updates: int (Number of security updates)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"OS Update auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        update_info = self._get_update_info()

        if "error" in update_info:
            return {
                "installed": True,
                "error": update_info["error"],
                "warnings": update_info.get("warnings", []),
                "risk_level": RiskLevel.NONE.value,
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "os_name": update_info.get("os_name", "Unknown"),
            "os_version": update_info.get("os_version", "Unknown"),
            "last_update_check": update_info.get("last_update_check", "Unknown"),
            "pending_updates": update_info.get("pending_updates", []),
            "update_count": len(update_info.get("pending_updates", [])),
            "security_updates": update_info.get("security_updates", 0),
            "educational_content": self.get_educational_content()
        }

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        return result

    def _get_update_info(self) -> Dict:
        """
        Get OS update information for the current platform.

        Returns:
            Dict with os_name, os_version, pending_updates, etc.
        """
        if self.platform == "Windows":
            return self._get_update_info_windows()
        elif self.platform == "Darwin":
            return self._get_update_info_macos()
        elif self.platform == "Linux":
            return self._get_update_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_update_info_windows(self) -> Dict:
        """Get OS update information on Windows using PowerShell."""
        result = {}
        warnings = []

        try:
            # Get Windows version - use WMI for more reliable detection
            ps_version_cmd = """
            $OS = Get-CimInstance -ClassName Win32_OperatingSystem
            $Build = [System.Environment]::OSVersion.Version.Build
            @{
                Caption = $OS.Caption
                Version = $OS.Version
                Build = $Build
            } | ConvertTo-Json
            """
            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_version_cmd],
                timeout=20
            )

            if returncode == 0 and stdout:
                try:
                    data = json.loads(stdout)
                    # Caption is like "Microsoft Windows 11 Pro" or "Microsoft Windows 10 Pro"
                    caption = data.get("Caption", "Windows")
                    # Remove "Microsoft" prefix if present
                    os_name = caption.replace("Microsoft ", "")
                    result["os_name"] = os_name

                    # Use build number for version (more accurate)
                    build = data.get("Build", data.get("Version", "Unknown"))
                    result["os_version"] = str(build)
                except json.JSONDecodeError:
                    result["os_name"] = "Windows"
                    result["os_version"] = "Unknown"

            # Check for pending updates using Windows Update COM object
            # Note: This requires admin privileges for full info
            ps_update_cmd = """
            try {
                $Session = New-Object -ComObject Microsoft.Update.Session
                $Searcher = $Session.CreateUpdateSearcher()
                $SearchResult = $Searcher.Search("IsInstalled=0")
                $Updates = @()
                foreach ($Update in $SearchResult.Updates) {
                    $Updates += @{
                        Title = $Update.Title
                        IsSecurityUpdate = $Update.Categories | Where-Object {$_.Name -eq 'Security Updates'} | Measure-Object | Select-Object -ExpandProperty Count
                        Severity = $Update.MsrcSeverity
                    }
                }
                $Updates | ConvertTo-Json
            } catch {
                Write-Output "ERROR: $($_.Exception.Message)"
            }
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_update_cmd],
                timeout=30
            )

            pending_updates = []
            security_count = 0

            if returncode == 0 and stdout:
                if "ERROR:" in stdout or "Access is denied" in stdout:
                    warnings.append("Administrator privileges required for detailed update information")
                    result["warnings"] = warnings
                else:
                    try:
                        updates_data = json.loads(stdout)
                        if isinstance(updates_data, dict):
                            updates_data = [updates_data]

                        for update in updates_data:
                            is_security = update.get("IsSecurityUpdate", 0) > 0
                            pending_updates.append({
                                "title": update.get("Title", "Unknown Update"),
                                "is_security": is_security,
                                "severity": update.get("Severity", "Unknown")
                            })
                            if is_security:
                                security_count += 1
                    except json.JSONDecodeError:
                        warnings.append("Could not parse Windows Update information")

            result["pending_updates"] = pending_updates
            result["security_updates"] = security_count

            # Try to get last update check time
            ps_last_check = "(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\Results\\Detect' -ErrorAction SilentlyContinue).LastSuccessTime"
            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_last_check],
                timeout=10
            )
            if returncode == 0 and stdout.strip():
                result["last_update_check"] = stdout.strip()
            else:
                result["last_update_check"] = "Unknown"

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check Windows updates: {str(e)}",
                "warnings": ["Administrator privileges may be required"]
            }

        return result

    def _get_update_info_macos(self) -> Dict:
        """Get OS update information on macOS."""
        result = {}
        warnings = []

        try:
            # Get macOS version
            stdout, stderr, returncode = self.run_command(
                ["sw_vers"],
                timeout=10
            )

            if returncode == 0 and stdout:
                result["os_name"] = "macOS"
                version_match = re.search(r'ProductVersion:\s*(.+)', stdout)
                if version_match:
                    result["os_version"] = version_match.group(1).strip()
                else:
                    result["os_version"] = "Unknown"

            # Check for available updates using softwareupdate
            stdout, stderr, returncode = self.run_command(
                ["softwareupdate", "--list"],
                timeout=60
            )

            pending_updates = []
            security_count = 0

            if returncode == 0:
                if "No new software available" in stdout:
                    result["pending_updates"] = []
                    result["security_updates"] = 0
                else:
                    # Parse update list
                    # Format varies, but typically:
                    # * Label: Update Name-1.0
                    #   Title: Update Title, Version: 1.0, Size: 123MB
                    lines = stdout.split('\n')
                    for line in lines:
                        if line.strip().startswith('*'):
                            # Extract update title
                            title_match = re.search(r'\* (.+)', line)
                            if title_match:
                                title = title_match.group(1).strip()
                                is_security = 'security' in title.lower()
                                pending_updates.append({
                                    "title": title,
                                    "is_security": is_security,
                                    "severity": "High" if is_security else "Unknown"
                                })
                                if is_security:
                                    security_count += 1

                    result["pending_updates"] = pending_updates
                    result["security_updates"] = security_count
            else:
                if "no network connection" in stderr.lower():
                    warnings.append("No network connection to check for updates")
                elif "root" in stderr.lower() or "permission" in stderr.lower():
                    warnings.append("Administrator privileges may be required")
                else:
                    warnings.append("Could not check for updates")

            # macOS doesn't easily expose last update check time
            result["last_update_check"] = "Unknown (check System Preferences)"

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check macOS updates: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_update_info_linux(self) -> Dict:
        """Get OS update information on Linux."""
        result = {}
        warnings = []

        try:
            # Detect Linux distribution
            distro_name = "Linux"
            distro_version = "Unknown"

            # Try reading /etc/os-release (modern standard)
            os_release_path = Path("/etc/os-release")
            if os_release_path.exists():
                try:
                    os_release_content = os_release_path.read_text()
                    name_match = re.search(r'^NAME="?([^"\n]+)"?', os_release_content, re.MULTILINE)
                    if name_match:
                        distro_name = name_match.group(1)
                    version_match = re.search(r'^VERSION="?([^"\n]+)"?', os_release_content, re.MULTILINE)
                    if version_match:
                        distro_version = version_match.group(1)
                except Exception:
                    pass

            result["os_name"] = distro_name
            result["os_version"] = distro_version

            # Check for updates based on package manager
            pending_updates = []
            security_count = 0

            # Try apt (Debian/Ubuntu)
            if self.check_command_exists("apt-get"):
                # Update package lists first (requires root, but we'll try)
                stdout, stderr, returncode = self.run_command(
                    ["apt-get", "update"],
                    timeout=60
                )

                # Check for upgradeable packages
                stdout, stderr, returncode = self.run_command(
                    ["apt", "list", "--upgradable"],
                    timeout=30
                )

                if returncode == 0 and stdout:
                    lines = stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 1:
                                pkg_name = parts[0].split('/')[0]
                                pending_updates.append({
                                    "title": f"{pkg_name} update",
                                    "is_security": False,  # Would need to check security updates separately
                                    "severity": "Unknown"
                                })

                # Try to get security updates count
                stdout, stderr, returncode = self.run_command(
                    ["apt-get", "--just-print", "upgrade"],
                    timeout=30
                )
                if returncode == 0 and stdout:
                    # Look for security updates
                    security_count = stdout.count('-security')

            # Try yum/dnf (RHEL/CentOS/Fedora)
            elif self.check_command_exists("yum") or self.check_command_exists("dnf"):
                cmd = "dnf" if self.check_command_exists("dnf") else "yum"

                stdout, stderr, returncode = self.run_command(
                    [cmd, "check-update"],
                    timeout=60
                )

                # yum check-update returns 100 if updates are available
                if returncode in [0, 100] and stdout:
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 3:
                                pkg_name = parts[0]
                                is_security = 'security' in line.lower()
                                pending_updates.append({
                                    "title": f"{pkg_name} update",
                                    "is_security": is_security,
                                    "severity": "High" if is_security else "Unknown"
                                })
                                if is_security:
                                    security_count += 1

            # Try pacman (Arch Linux)
            elif self.check_command_exists("pacman"):
                stdout, stderr, returncode = self.run_command(
                    ["pacman", "-Qu"],
                    timeout=30
                )

                if returncode == 0 and stdout:
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 1:
                                pkg_name = parts[0]
                                pending_updates.append({
                                    "title": f"{pkg_name} update",
                                    "is_security": False,
                                    "severity": "Unknown"
                                })
            else:
                warnings.append("Could not detect package manager (apt/yum/dnf/pacman)")

            result["pending_updates"] = pending_updates
            result["security_updates"] = security_count
            result["last_update_check"] = "Unknown (run package manager update)"

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check Linux updates: {str(e)}",
                "warnings": warnings
            }

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on pending updates.

        Risk levels:
            - CRITICAL: 5+ security updates pending
            - HIGH: 1-4 security updates pending
            - MEDIUM: 10+ non-security updates pending
            - LOW: 1-9 non-security updates pending
            - NONE: No updates pending or can't determine

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        security_updates = result.get("security_updates", 0)
        update_count = result.get("update_count", 0)

        # Security updates are critical
        if security_updates >= 5:
            return RiskLevel.CRITICAL
        elif security_updates > 0:
            return RiskLevel.HIGH

        # Non-security updates
        if update_count >= 10:
            return RiskLevel.MEDIUM
        elif update_count > 0:
            return RiskLevel.LOW

        # No updates or can't determine
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
        security_updates = result.get("security_updates", 0)
        update_count = result.get("update_count", 0)

        if risk_level == "critical":
            return (
                f"{security_updates} security updates pending. "
                "Install IMMEDIATELY—these patch known vulnerabilities. "
                "HOW TO FIX: Settings → Windows Update → Check for updates → Install all."
            )
        elif risk_level == "high":
            return (
                f"{security_updates} security update(s) pending. "
                "Install as soon as possible. "
                "HOW TO FIX: Settings → Windows Update → Check for updates."
            )
        elif risk_level == "medium":
            return (
                f"{update_count} updates pending. "
                "Install during next maintenance window. "
                "HOW TO FIX: Settings → Windows Update → Check for updates."
            )
        elif risk_level == "low":
            return (
                f"{update_count} update(s) pending. "
                "Install when convenient. "
                "HOW TO FIX: Settings → Windows Update → Check for updates."
            )
        else:
            return "System is up to date or update status could not be determined."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about OS updates.

        Returns:
            Dict with educational content from docs/concepts/os-updates.md
        """
        return get_educational_content("os-updates")

    def requires_elevation(self) -> bool:
        """
        Check if OS update auditor requires admin/root.

        Returns:
            True - Most update checks require elevated privileges
        """
        # Windows Update COM requires admin
        # apt-get update requires root
        # yum check-update can run as user but may have limited info
        # macOS softwareupdate can run as user
        return False  # We'll try without elevation and warn if needed
