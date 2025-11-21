"""
Firewall Auditor for DevAudit.

Checks if system firewall is enabled and properly configured.

Platforms: Windows, macOS, Linux
Requires Admin: Partial (some info available without admin)
"""

import re
import json
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class FirewallAuditor(BaseAuditor):
    """Audit firewall status and configuration."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Firewall"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """
        Check if firewall auditor can run.

        Returns True if we can check firewall status on this platform.
        """
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """Get firewall version/type."""
        fw_info = self._get_firewall_info()
        return fw_info.get("firewall_type", "System Firewall")

    def audit(self) -> Dict:
        """
        Perform firewall audit.

        Returns:
            Dict containing:
                - installed: bool (Firewall capability exists)
                - enabled: bool (Firewall is active)
                - firewall_type: str (Windows Firewall, iptables, pf, etc.)
                - profiles: List[Dict] (Network profiles and their status)
                - inbound_default: str (Block/Allow)
                - outbound_default: str (Block/Allow)
                - open_ports: List[int] (Listening ports, optional)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Firewall auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        fw_info = self._get_firewall_info()

        if "error" in fw_info:
            return {
                "installed": True,
                "error": fw_info["error"],
                "warnings": fw_info.get("warnings", []),
                "risk_level": RiskLevel.HIGH.value,
                "recommendation": "Could not check firewall status. Verify firewall is enabled.",
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "enabled": fw_info.get("enabled", False),
            "firewall_type": fw_info.get("firewall_type", "Unknown"),
            "profiles": fw_info.get("profiles", []),
            "inbound_default": fw_info.get("inbound_default", "Unknown"),
            "outbound_default": fw_info.get("outbound_default", "Unknown"),
            "warnings": fw_info.get("warnings", []),
            "educational_content": self.get_educational_content()
        }

        # Optionally add open ports (if detected)
        if "open_ports" in fw_info:
            result["open_ports"] = fw_info["open_ports"]

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        return result

    def _get_firewall_info(self) -> Dict:
        """
        Get firewall information for the current platform.

        Returns:
            Dict with enabled status, profiles, rules, etc.
        """
        if self.platform == "Windows":
            return self._get_firewall_info_windows()
        elif self.platform == "Darwin":
            return self._get_firewall_info_macos()
        elif self.platform == "Linux":
            return self._get_firewall_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_firewall_info_windows(self) -> Dict:
        """Get firewall information on Windows."""
        result = {}
        warnings = []
        profiles = []

        try:
            # Query Windows Firewall status using PowerShell
            ps_fw_cmd = """
            Get-NetFirewallProfile |
            Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction |
            ConvertTo-Json
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_fw_cmd],
                timeout=15
            )

            if returncode == 0 and stdout:
                try:
                    fw_data = json.loads(stdout)

                    # Handle single profile (dict) or multiple (array)
                    if isinstance(fw_data, dict):
                        fw_data = [fw_data]

                    all_enabled = True
                    for profile in fw_data:
                        profile_name = profile.get("Name", "Unknown")
                        enabled = profile.get("Enabled", False)
                        inbound = profile.get("DefaultInboundAction", "Unknown")
                        outbound = profile.get("DefaultOutboundAction", "Unknown")

                        profiles.append({
                            "name": profile_name,
                            "enabled": enabled,
                            "inbound_default": inbound,
                            "outbound_default": outbound
                        })

                        if not enabled:
                            all_enabled = False

                    result["firewall_type"] = "Windows Defender Firewall"
                    result["enabled"] = all_enabled
                    result["profiles"] = profiles

                    # Set overall defaults (from Domain profile if available, else first)
                    domain_profile = next((p for p in profiles if p["name"] == "Domain"), profiles[0] if profiles else {})
                    result["inbound_default"] = domain_profile.get("inbound_default", "Unknown")
                    result["outbound_default"] = domain_profile.get("outbound_default", "Unknown")

                    if not all_enabled:
                        warnings.append("One or more firewall profiles are disabled")

                except json.JSONDecodeError:
                    warnings.append("Could not parse firewall information")
                    result["error"] = "Failed to parse firewall status"

            # Try alternative method using netsh if PowerShell failed
            if "error" in result or not profiles:
                stdout, stderr, returncode = self.run_command(
                    ["netsh", "advfirewall", "show", "allprofiles", "state"],
                    timeout=10
                )

                if returncode == 0 and stdout:
                    # Parse netsh output
                    # Format:
                    # Domain Profile Settings:
                    # State                                 ON
                    current_profile = None
                    profile_states = {}

                    for line in stdout.split('\n'):
                        if "Profile Settings:" in line:
                            current_profile = line.split()[0]  # Domain, Private, Public
                        elif "State" in line and current_profile:
                            state = "ON" in line.upper()
                            profile_states[current_profile] = state

                    # Convert to profiles list
                    profiles = [
                        {"name": name, "enabled": enabled, "inbound_default": "Block", "outbound_default": "Allow"}
                        for name, enabled in profile_states.items()
                    ]

                    result["profiles"] = profiles
                    result["enabled"] = all(p["enabled"] for p in profiles) if profiles else False
                    result["firewall_type"] = "Windows Defender Firewall"
                    result["inbound_default"] = "Block"  # Windows default
                    result["outbound_default"] = "Allow"

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check firewall status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_firewall_info_macos(self) -> Dict:
        """Get firewall information on macOS."""
        result = {}
        warnings = []

        try:
            # Check Application Firewall status
            stdout, stderr, returncode = self.run_command(
                ["sudo", "-n", "/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
                timeout=10
            )

            # If sudo fails (no password-less sudo), try without sudo
            if returncode != 0 or "sudo" in stderr.lower():
                stdout, stderr, returncode = self.run_command(
                    ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
                    timeout=10
                )
                if returncode != 0:
                    warnings.append("Administrator privileges required for detailed firewall information")

            enabled = False
            if returncode == 0 and stdout:
                # Output format: "Firewall is enabled. (State = 1)"
                if "enabled" in stdout.lower():
                    enabled = True
                elif "disabled" in stdout.lower():
                    enabled = False

            result["firewall_type"] = "macOS Application Firewall"
            result["enabled"] = enabled
            result["profiles"] = [
                {
                    "name": "Application Firewall",
                    "enabled": enabled,
                    "inbound_default": "Allow" if not enabled else "Block (unsigned apps)",
                    "outbound_default": "Allow"
                }
            ]
            result["inbound_default"] = "Allow" if not enabled else "Block (unsigned apps)"
            result["outbound_default"] = "Allow"

            # Check stealth mode
            stdout2, stderr2, returncode2 = self.run_command(
                ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getstealthmode"],
                timeout=10
            )

            if returncode2 == 0 and "enabled" in stdout2.lower():
                warnings.append("Stealth mode is enabled (good for security)")

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check firewall status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_firewall_info_linux(self) -> Dict:
        """Get firewall information on Linux."""
        result = {}
        warnings = []

        try:
            # Try to detect which firewall system is in use
            firewall_type = None
            enabled = False

            # Check for ufw (Ubuntu/Debian common)
            if self.check_command_exists("ufw"):
                stdout, stderr, returncode = self.run_command(
                    ["sudo", "-n", "ufw", "status"],
                    timeout=10
                )

                # Try without sudo if passwordless sudo fails
                if returncode != 0:
                    stdout, stderr, returncode = self.run_command(
                        ["ufw", "status"],
                        timeout=10
                    )

                if returncode == 0 and stdout:
                    firewall_type = "UFW (Uncomplicated Firewall)"
                    enabled = "Status: active" in stdout

                    result["firewall_type"] = firewall_type
                    result["enabled"] = enabled
                    result["profiles"] = [
                        {
                            "name": "UFW",
                            "enabled": enabled,
                            "inbound_default": "Deny" if enabled else "Allow",
                            "outbound_default": "Allow"
                        }
                    ]
                    result["inbound_default"] = "Deny" if enabled else "Allow"
                    result["outbound_default"] = "Allow"

            # Check for firewalld (RHEL/CentOS/Fedora common)
            elif self.check_command_exists("firewall-cmd"):
                stdout, stderr, returncode = self.run_command(
                    ["sudo", "-n", "firewall-cmd", "--state"],
                    timeout=10
                )

                # Try without sudo
                if returncode != 0:
                    stdout, stderr, returncode = self.run_command(
                        ["firewall-cmd", "--state"],
                        timeout=10
                    )

                if returncode == 0 and stdout:
                    firewall_type = "firewalld"
                    enabled = "running" in stdout.lower()

                    # Get active zones
                    zones_stdout, zones_stderr, zones_returncode = self.run_command(
                        ["firewall-cmd", "--get-active-zones"],
                        timeout=10
                    )

                    result["firewall_type"] = firewall_type
                    result["enabled"] = enabled
                    result["profiles"] = [
                        {
                            "name": "firewalld",
                            "enabled": enabled,
                            "inbound_default": "Reject" if enabled else "Allow",
                            "outbound_default": "Allow"
                        }
                    ]
                    result["inbound_default"] = "Reject" if enabled else "Allow"
                    result["outbound_default"] = "Allow"

            # Check for iptables (raw)
            elif self.check_command_exists("iptables"):
                stdout, stderr, returncode = self.run_command(
                    ["sudo", "-n", "iptables", "-L", "-n"],
                    timeout=10
                )

                # Try without sudo
                if returncode != 0:
                    stdout, stderr, returncode = self.run_command(
                        ["iptables", "-L", "-n"],
                        timeout=10
                    )

                if returncode == 0 and stdout:
                    firewall_type = "iptables"

                    # Check if there are any rules beyond default ACCEPT
                    # If there are rules, firewall is "configured"
                    enabled = "DROP" in stdout or "REJECT" in stdout or len(stdout.split('\n')) > 10

                    result["firewall_type"] = firewall_type
                    result["enabled"] = enabled
                    result["profiles"] = [
                        {
                            "name": "iptables",
                            "enabled": enabled,
                            "inbound_default": "Unknown (check rules)",
                            "outbound_default": "Allow"
                        }
                    ]
                    result["inbound_default"] = "Unknown (check rules)"
                    result["outbound_default"] = "Allow"

                    if not enabled:
                        warnings.append("iptables exists but appears unconfigured")

            else:
                warnings.append("Could not detect firewall system (ufw/firewalld/iptables)")
                result["firewall_type"] = "Unknown"
                result["enabled"] = False
                result["profiles"] = []
                result["inbound_default"] = "Unknown"
                result["outbound_default"] = "Unknown"

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check firewall status: {str(e)}",
                "warnings": warnings
            }

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on firewall status.

        Risk levels:
            - CRITICAL: Firewall completely disabled
            - HIGH: Firewall partially disabled (some profiles off)
            - MEDIUM: Firewall enabled but permissive defaults
            - LOW: Firewall enabled with proper defaults
            - NONE: Can't determine

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        enabled = result.get("enabled", False)
        profiles = result.get("profiles", [])
        inbound_default = result.get("inbound_default", "Unknown")

        if not enabled:
            return RiskLevel.CRITICAL

        # Check if any profiles are disabled
        disabled_profiles = [p for p in profiles if not p.get("enabled", False)]
        if disabled_profiles and len(disabled_profiles) < len(profiles):
            return RiskLevel.HIGH

        # Check inbound default policy
        if isinstance(inbound_default, str) and inbound_default.lower() in ["allow", "unknown"]:
            return RiskLevel.MEDIUM

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
        firewall_type = result.get("firewall_type", "firewall")
        profiles = result.get("profiles", [])

        if risk_level == "critical":
            return f"{firewall_type} is disabled. Enable it immediately to protect against network attacks."

        elif risk_level == "high":
            disabled = [p["name"] for p in profiles if not p.get("enabled", False)]
            return f"{firewall_type} profiles disabled: {', '.join(disabled)}. Enable all profiles for full protection."

        elif risk_level == "medium":
            return f"{firewall_type} is enabled but may have permissive rules. Review inbound rules."

        elif risk_level == "low":
            return f"{firewall_type} is active with proper defaults. Review rules periodically."

        else:
            return "Firewall status could not be determined. Verify firewall is enabled manually."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about firewalls.

        Returns:
            Dict with educational content from docs/concepts/firewall.md
        """
        return get_educational_content("firewall")

    def requires_elevation(self) -> bool:
        """
        Check if firewall auditor requires admin/root.

        Returns:
            False - Basic status can be checked without admin
        """
        return False  # We'll try without elevation and provide limited info
