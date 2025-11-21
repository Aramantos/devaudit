"""
Antivirus Auditor for DevAudit.

Checks if antivirus software is installed, active, and up-to-date.

Platforms: Windows (primary), macOS (limited), Linux (limited)
Requires Admin: No (but limited info without admin on some platforms)
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class AntivirusAuditor(BaseAuditor):
    """Audit antivirus software status."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Antivirus"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """
        Check if antivirus auditor can run.

        Returns True if we can check AV status on this platform.
        """
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """Get antivirus software version."""
        av_info = self._get_av_info()
        products = av_info.get("products", [])
        if products:
            return products[0].get("version", "Unknown")
        return None

    def audit(self) -> Dict:
        """
        Perform antivirus audit.

        Returns:
            Dict containing:
                - installed: bool (AV software detected)
                - products: List[Dict] (Detected AV products)
                - enabled: bool (AV actively protecting)
                - updated: bool (Definitions up-to-date)
                - real_time_protection: bool (Real-time scanning active)
                - last_scan: str (Last full scan date)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Antivirus auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        av_info = self._get_av_info()

        if "error" in av_info:
            return {
                "installed": False,
                "error": av_info["error"],
                "warnings": av_info.get("warnings", []),
                "risk_level": RiskLevel.CRITICAL.value,
                "recommendation": "Could not detect antivirus software. Install and enable antivirus protection.",
                "educational_content": self.get_educational_content()
            }

        products = av_info.get("products", [])
        if not products:
            return {
                "installed": False,
                "reason": "No antivirus software detected",
                "risk_level": RiskLevel.CRITICAL.value,
                "recommendation": "Install antivirus software immediately. Windows Defender is built-in and free.",
                "educational_content": self.get_educational_content()
            }

        # Analyze first (primary) AV product
        primary_av = products[0]

        result = {
            "installed": True,
            "products": products,
            "enabled": primary_av.get("enabled", False),
            "updated": primary_av.get("updated", False),
            "real_time_protection": primary_av.get("real_time_protection", False),
            "last_scan": primary_av.get("last_scan", "Unknown"),
            "warnings": av_info.get("warnings", []),
            "educational_content": self.get_educational_content()
        }

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        return result

    def _get_av_info(self) -> Dict:
        """
        Get antivirus information for the current platform.

        Returns:
            Dict with products, status, etc.
        """
        if self.platform == "Windows":
            return self._get_av_info_windows()
        elif self.platform == "Darwin":
            return self._get_av_info_macos()
        elif self.platform == "Linux":
            return self._get_av_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_av_info_windows(self) -> Dict:
        """Get antivirus information on Windows using Security Center."""
        result = {}
        warnings = []
        products = []

        try:
            # Query Windows Security Center for AV products
            # This works on Windows Vista+ without admin privileges
            ps_av_cmd = """
            Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct |
            Select-Object displayName, productState, timestamp |
            ConvertTo-Json
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_av_cmd],
                timeout=20
            )

            if returncode == 0 and stdout:
                try:
                    av_data = json.loads(stdout)

                    # Handle single product (returned as dict) or multiple (array)
                    if isinstance(av_data, dict):
                        av_data = [av_data]

                    for av in av_data:
                        display_name = av.get("displayName", "Unknown AV")
                        product_state = av.get("productState", 0)

                        # Decode product state (hex value encodes multiple flags)
                        # Bit 12: Enabled (0x1000)
                        # Bits 8-11: Real-time protection status
                        # Note: "updated" flag from product_state is unreliable,
                        # we'll check actual signature date for Windows Defender
                        enabled = bool(product_state & 0x1000)
                        updated = True  # Will be checked more accurately via Get-MpComputerStatus
                        real_time_protection = bool(product_state & 0x1000) and not bool(product_state & 0x0100)

                        products.append({
                            "name": display_name,
                            "enabled": enabled,
                            "updated": updated,
                            "real_time_protection": real_time_protection,
                            "product_state": hex(product_state),
                            "version": "Unknown",
                            "last_scan": "Unknown"
                        })

                except json.JSONDecodeError:
                    warnings.append("Could not parse antivirus information")

            # Always check Windows Defender specifically for accurate signature date
            # (Security Center product_state is unreliable for "updated" status)
            ps_defender_cmd = """
            Get-MpComputerStatus |
            Select-Object AntivirusEnabled, RealTimeProtectionEnabled,
                         AntivirusSignatureLastUpdated, QuickScanEndTime |
            ConvertTo-Json
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_defender_cmd],
                timeout=15
            )

            if returncode == 0 and stdout:
                try:
                    defender_data = json.loads(stdout)

                    enabled = defender_data.get("AntivirusEnabled", False)
                    real_time = defender_data.get("RealTimeProtectionEnabled", False)

                    # Parse signature update date
                    sig_update = defender_data.get("AntivirusSignatureLastUpdated", "")
                    updated = False
                    if sig_update:
                        try:
                            # Parse date and check if within last 3 days
                            if isinstance(sig_update, dict) and "DateTime" in sig_update:
                                update_date_str = sig_update["DateTime"]
                            else:
                                update_date_str = str(sig_update)

                            # Handle .NET JSON date format: /Date(milliseconds)/
                            if "/Date(" in update_date_str:
                                match = re.search(r'/Date\((\d+)\)/', update_date_str)
                                if match:
                                    ms_since_epoch = int(match.group(1))
                                    update_date = datetime.fromtimestamp(ms_since_epoch / 1000.0)
                                else:
                                    raise ValueError("Could not parse .NET date format")
                            else:
                                # Try ISO format
                                update_date = datetime.fromisoformat(update_date_str.split('.')[0].replace('T', ' '))

                            days_old = (datetime.now() - update_date).days
                            # Consider updated if within last 3 days (more lenient)
                            updated = days_old <= 3
                        except Exception:
                            pass

                    # Parse last scan date
                    last_scan = defender_data.get("QuickScanEndTime", "Unknown")
                    if isinstance(last_scan, dict) and "DateTime" in last_scan:
                        last_scan = last_scan["DateTime"]

                    # If we already found Defender from Security Center, update it
                    # Otherwise, add it as new entry
                    defender_found = False
                    for product in products:
                        if "Defender" in product.get("name", ""):
                            product["updated"] = updated
                            product["enabled"] = enabled
                            product["real_time_protection"] = real_time
                            product["last_scan"] = str(last_scan) if last_scan else "Unknown"
                            defender_found = True
                            break

                    if not defender_found:
                        products.append({
                            "name": "Windows Defender",
                            "enabled": enabled,
                            "updated": updated,
                            "real_time_protection": real_time,
                            "version": "Built-in",
                            "last_scan": str(last_scan) if last_scan else "Unknown"
                        })

                except json.JSONDecodeError:
                    warnings.append("Could not check Windows Defender status")

            if not products and not warnings:
                return {
                    "error": "No antivirus software detected",
                    "warnings": ["Consider enabling Windows Defender or installing third-party AV"]
                }

            result["products"] = products
            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check antivirus status: {str(e)}",
                "warnings": ["May require administrator privileges for detailed information"]
            }

        return result

    def _get_av_info_macos(self) -> Dict:
        """Get antivirus information on macOS."""
        result = {}
        warnings = []
        products = []

        # macOS doesn't have built-in traditional AV like Windows Defender
        # It has XProtect (signature-based) and Gatekeeper (code signing)
        # We can check for common third-party AV products

        try:
            # Check for common AV products by looking for running processes
            common_av_processes = {
                "Norton": "Norton",
                "com.symantec": "Norton",
                "Avast": "Avast",
                "AVG": "AVG",
                "McAfee": "McAfee",
                "Sophos": "Sophos",
                "Kaspersky": "Kaspersky",
                "Bitdefender": "Bitdefender",
                "ESET": "ESET",
                "Malwarebytes": "Malwarebytes"
            }

            stdout, stderr, returncode = self.run_command(
                ["ps", "aux"],
                timeout=10
            )

            if returncode == 0 and stdout:
                for process_name, av_name in common_av_processes.items():
                    if process_name.lower() in stdout.lower():
                        products.append({
                            "name": av_name,
                            "enabled": True,  # Running = enabled
                            "updated": "Unknown",
                            "real_time_protection": True,
                            "version": "Unknown",
                            "last_scan": "Unknown"
                        })
                        break  # Found one, that's enough

            # Check for XProtect (built-in macOS malware scanning)
            xprotect_path = Path("/System/Library/CoreServices/XProtect.bundle")
            if xprotect_path.exists():
                products.append({
                    "name": "XProtect (Built-in)",
                    "enabled": True,
                    "updated": "Unknown",
                    "real_time_protection": True,
                    "version": "Built-in",
                    "last_scan": "Automatic"
                })

            if not products:
                warnings.append("No third-party antivirus detected. macOS has built-in XProtect.")
                # XProtect is always there, even if we can't detect it
                products.append({
                    "name": "XProtect (Built-in)",
                    "enabled": True,
                    "updated": "Unknown",
                    "real_time_protection": True,
                    "version": "Built-in",
                    "last_scan": "Automatic"
                })

            result["products"] = products
            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check antivirus status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_av_info_linux(self) -> Dict:
        """Get antivirus information on Linux."""
        result = {}
        warnings = []
        products = []

        # Linux typically doesn't use traditional AV
        # But we can check for ClamAV and common enterprise AV

        try:
            # Check for ClamAV
            if self.check_command_exists("clamscan"):
                stdout, stderr, returncode = self.run_command(
                    ["clamscan", "--version"],
                    timeout=5
                )

                if returncode == 0 and stdout:
                    version = stdout.strip().split()[1] if len(stdout.split()) > 1 else "Unknown"

                    # Check if clamd (daemon) is running
                    ps_stdout, ps_stderr, ps_returncode = self.run_command(
                        ["pgrep", "-x", "clamd"],
                        timeout=5
                    )
                    enabled = ps_returncode == 0

                    # Check freshclam (definition updates)
                    freshclam_log = Path("/var/log/clamav/freshclam.log")
                    updated = False
                    if freshclam_log.exists():
                        try:
                            # Check if definitions updated in last 7 days
                            import os
                            mtime = os.path.getmtime(str(freshclam_log))
                            days_old = (datetime.now().timestamp() - mtime) / 86400
                            updated = days_old <= 7
                        except Exception:
                            pass

                    products.append({
                        "name": "ClamAV",
                        "enabled": enabled,
                        "updated": updated,
                        "real_time_protection": enabled,
                        "version": version,
                        "last_scan": "Unknown"
                    })

            # Check for other enterprise AV products
            enterprise_av = {
                "sophosspl": "Sophos",
                "mcafee": "McAfee",
                "bdagent": "Bitdefender",
                "esets_daemon": "ESET"
            }

            stdout, stderr, returncode = self.run_command(
                ["ps", "aux"],
                timeout=10
            )

            if returncode == 0 and stdout:
                for process_name, av_name in enterprise_av.items():
                    if process_name in stdout.lower():
                        products.append({
                            "name": av_name,
                            "enabled": True,
                            "updated": "Unknown",
                            "real_time_protection": True,
                            "version": "Unknown",
                            "last_scan": "Unknown"
                        })
                        break

            if not products:
                warnings.append("No antivirus software detected. Linux typically relies on built-in security and careful package management.")
                # Return info about Linux security model
                products.append({
                    "name": "Built-in Security (AppArmor/SELinux)",
                    "enabled": True,
                    "updated": True,
                    "real_time_protection": True,
                    "version": "System",
                    "last_scan": "N/A"
                })

            result["products"] = products
            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check antivirus status: {str(e)}",
                "warnings": warnings
            }

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on antivirus status.

        Risk levels:
            - CRITICAL: No AV installed or AV disabled
            - HIGH: AV enabled but definitions outdated (>7 days)
            - MEDIUM: AV enabled, updated, but real-time protection off
            - LOW: AV enabled, updated, real-time protection on
            - NONE: Can't determine (macOS/Linux with built-in security)

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        if not result.get("installed"):
            return RiskLevel.CRITICAL

        enabled = result.get("enabled", False)
        updated = result.get("updated", False)
        real_time = result.get("real_time_protection", False)

        if not enabled:
            return RiskLevel.CRITICAL

        if enabled and not updated:
            return RiskLevel.HIGH

        if enabled and updated and not real_time:
            return RiskLevel.MEDIUM

        # Check if it's built-in security (macOS/Linux)
        products = result.get("products", [])
        if products:
            primary_name = products[0].get("name", "")
            if "XProtect" in primary_name or "Built-in" in primary_name or "AppArmor" in primary_name:
                return RiskLevel.NONE  # Built-in security, different risk model

        return RiskLevel.LOW

    def _get_recommendation(self, result: Dict) -> str:
        """
        Get recommendation based on risk level.

        Args:
            result: Audit result dict

        Returns:
            Recommendation string
        """
        risk_level = result.get("risk_level", "none")
        products = result.get("products", [])
        product_name = products[0].get("name", "antivirus") if products else "antivirus"

        if risk_level == "critical":
            if not result.get("installed"):
                return "No antivirus detected. HOW TO FIX: Settings → Privacy & Security → Windows Security → Turn on Defender. Or install third-party AV."
            else:
                return f"{product_name} is disabled. HOW TO FIX: Settings → Privacy & Security → Windows Security → Virus & threat protection → Turn on."

        elif risk_level == "high":
            return f"{product_name} definitions are outdated. Update immediately—new malware appears daily. HOW TO FIX: Settings → Windows Update → Check for updates (includes Defender definitions)."

        elif risk_level == "medium":
            return f"{product_name} real-time protection is off. HOW TO FIX: Windows Security → Virus & threat protection → Manage settings → Real-time protection ON."

        elif risk_level == "low":
            return f"{product_name} is active and up-to-date. Continue regular scans."

        else:
            # macOS/Linux built-in security
            return "Built-in system security is active. Keep OS updated for latest protections."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about antivirus software.

        Returns:
            Dict with educational content from docs/concepts/antivirus.md
        """
        return get_educational_content("antivirus")

    def requires_elevation(self) -> bool:
        """
        Check if antivirus auditor requires admin/root.

        Returns:
            False - Can check AV status without admin on most platforms
        """
        return False
