"""
Firewall Auditor for DevAudit.

Checks if system firewall is enabled and properly configured.

Platforms: Windows, macOS, Linux
Requires Admin: Partial (some info available without admin)
"""

import re
import json
import logging
from typing import Dict, Optional, List, Tuple
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content

logger = logging.getLogger(__name__)


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

        # Honest-degradation flags (Linux): a firewall we could not read, and
        # the command a person runs to read it, or no firewall tool at all.
        for key in ("status_unknown", "check_command", "no_firewall_found"):
            if key in fw_info:
                result[key] = fw_info[key]

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
        """Get firewall information on Linux.

        Front-ends own the rules when present (ufw, then firewalld), then
        native nftables, then legacy iptables. Every tool is looked up in sbin
        as well as PATH (base.find_command) and run by its full path. A tool
        that is there but whose status needs root reads as status_unknown,
        never as "disabled".
        """
        try:
            ufw = self.find_command("ufw")
            if ufw:
                return self._read_ufw(ufw)
            firewalld = self.find_command("firewall-cmd")
            if firewalld:
                return self._read_firewalld(firewalld)
            nft = self.find_command("nft")
            if nft:
                return self._read_nftables(nft)
            iptables = self.find_command("iptables")
            if iptables:
                return self._read_iptables(iptables)

            logger.info("no firewall tool found on PATH or in sbin")
            return {
                "firewall_type": "None detected",
                "enabled": False,
                "no_firewall_found": True,
                "profiles": [],
                "inbound_default": "Allow",
                "outbound_default": "Allow",
                "warnings": [
                    "No firewall tool found (looked for ufw, firewall-cmd, nft and "
                    "iptables on PATH and in /usr/local/sbin, /usr/sbin and /sbin)"
                ],
            }
        except Exception as e:
            logger.warning("firewall check failed: %s", e)
            return {
                "error": f"Failed to check firewall status: {str(e)}",
                "warnings": []
            }

    def _read_status(self, cmd: List[str]) -> Tuple[str, str, int]:
        """Run a read-only status command, with passwordless sudo if the user has it.

        `sudo -n` never prompts: it either runs at once or fails, and then the
        command runs as the user.
        """
        stdout, stderr, returncode = self.run_command(["sudo", "-n", *cmd], timeout=10)
        if returncode == 0:
            return stdout, stderr, returncode
        return self.run_command(cmd, timeout=10)

    def _status_unknown(self, firewall_type: str, check_command: str, detail: str) -> Dict:
        """The firewall is installed but we could not read whether it is filtering."""
        detail = (detail or "").strip() or "permission denied"
        logger.info("%s is installed but its status could not be read: %s", firewall_type, detail)
        return {
            "firewall_type": firewall_type,
            "enabled": False,
            "status_unknown": True,
            "check_command": check_command,
            "profiles": [],
            "inbound_default": "Unknown",
            "outbound_default": "Unknown",
            "warnings": [f"{firewall_type} is installed but reading its status needs root ({detail})"],
        }

    @staticmethod
    def _single_profile(name: str, enabled: bool, inbound: str, outbound: str = "Allow") -> Dict:
        return {
            "profiles": [
                {"name": name, "enabled": enabled, "inbound_default": inbound, "outbound_default": outbound}
            ],
            "inbound_default": inbound,
            "outbound_default": outbound,
        }

    def _read_ufw(self, ufw: str) -> Dict:
        stdout, stderr, returncode = self._read_status([ufw, "status"])
        if returncode != 0 or "Status:" not in stdout:
            return self._status_unknown("UFW (Uncomplicated Firewall)", "sudo ufw status", stderr)
        enabled = "Status: active" in stdout
        result = {"firewall_type": "UFW (Uncomplicated Firewall)", "enabled": enabled}
        result.update(self._single_profile("UFW", enabled, "Deny" if enabled else "Allow"))
        return result

    def _read_firewalld(self, firewalld: str) -> Dict:
        # `firewall-cmd --state` prints "running" (rc 0) or "not running" (rc 252).
        stdout, stderr, returncode = self._read_status([firewalld, "--state"])
        state = stdout.strip().lower()
        if state not in ("running", "not running"):
            return self._status_unknown("firewalld", "sudo firewall-cmd --state", stderr)
        enabled = state == "running"
        result = {"firewall_type": "firewalld", "enabled": enabled}
        result.update(self._single_profile("firewalld", enabled, "Reject" if enabled else "Allow"))
        return result

    def _read_nftables(self, nft: str) -> Dict:
        stdout, stderr, returncode = self._read_status([nft, "list", "ruleset"])
        if returncode != 0:
            return self._status_unknown("nftables", "sudo nft list ruleset", stderr)

        # Filtering is on when any rule or chain policy drops or rejects. The
        # inbound default is the policy of the base chains on the input hook:
        # a drop in any of them is final for the packet.
        filters = re.search(r"\b(drop|reject)\b", stdout) is not None
        input_policies = re.findall(r"hook input priority [^;]*;\s*policy (\w+);", stdout)
        inbound = "Drop" if "drop" in input_policies else "Allow"
        result = {"firewall_type": "nftables", "enabled": filters}
        result.update(self._single_profile("nftables", filters, inbound))
        if not filters:
            result["warnings"] = ["nftables is installed but no rule drops or rejects anything"]
        return result

    def _read_iptables(self, iptables: str) -> Dict:
        stdout, stderr, returncode = self._read_status([iptables, "-L", "-n"])
        if returncode != 0 or not stdout:
            return self._status_unknown("iptables", "sudo iptables -L -n", stderr)

        # Any rule beyond the default ACCEPT counts as configured.
        enabled = "DROP" in stdout or "REJECT" in stdout or len(stdout.split('\n')) > 10
        result = {"firewall_type": "iptables", "enabled": enabled}
        result.update(self._single_profile("iptables", enabled, "Unknown (check rules)"))
        if not enabled:
            result["warnings"] = ["iptables exists but appears unconfigured"]
        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on firewall status.

        Risk levels:
            - CRITICAL: Firewall completely disabled
            - HIGH: Firewall partially disabled (some profiles off)
            - MEDIUM: Firewall enabled but permissive defaults, or installed
              but its status needs root to read (status_unknown)
            - LOW: Firewall enabled with proper defaults

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        enabled = result.get("enabled", False)
        profiles = result.get("profiles", [])
        inbound_default = result.get("inbound_default", "Unknown")

        # Installed but unreadable without root: we do not know, so MEDIUM,
        # never CRITICAL (honest degradation, context.md Decision 4).
        if result.get("status_unknown"):
            return RiskLevel.MEDIUM

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

        if result.get("status_unknown"):
            return (
                f"{firewall_type} is installed, but reading its status needs root, so DevAudit "
                "cannot tell whether it is filtering traffic. "
                f"HOW TO CHECK: run `{result.get('check_command', '')}`."
            )

        if result.get("no_firewall_found"):
            return (
                "No host firewall found (looked for ufw, firewalld, nftables and iptables). "
                "Without one, every service listening on this machine can be reached from your network. "
                "HOW TO FIX: on Debian, Ubuntu or Raspberry Pi OS, `sudo apt install ufw`, allow what "
                "you use first (for example `sudo ufw allow ssh`), then `sudo ufw enable`."
            )

        if risk_level == "critical":
            if firewall_type == "nftables":
                return (
                    "nftables is installed but no rule drops or rejects anything, so nothing is "
                    "being filtered. Add an input policy that drops what you have not allowed."
                )
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
