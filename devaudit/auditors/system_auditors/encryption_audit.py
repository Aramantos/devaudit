"""
Disk Encryption Auditor for DevAudit.

Checks if disk encryption is enabled (BitLocker, FileVault, LUKS).

Platforms: Windows, macOS, Linux
Requires Admin: Yes (for detailed encryption status)
"""

import re
import json
from typing import Dict, Optional, List
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class EncryptionAuditor(BaseAuditor):
    """Audit disk encryption status."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Disk Encryption"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """Encryption checks are always available."""
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """No version for encryption status."""
        return None

    def audit(self) -> Dict:
        """
        Perform disk encryption audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - encryption_enabled: bool (If disk encryption is active)
                - encryption_type: str (BitLocker, FileVault, LUKS, etc.)
                - encrypted_volumes: List[Dict] (Encrypted volumes/drives)
                - unencrypted_volumes: int (Count of unencrypted drives)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Encryption auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        encryption_info = self._get_encryption_info()

        if "error" in encryption_info:
            return {
                "installed": True,
                "error": encryption_info["error"],
                "warnings": encryption_info.get("warnings", []),
                "encryption_enabled": False,
                "risk_level": RiskLevel.CRITICAL.value,
                "recommendation": "Could not determine encryption status. Enable disk encryption to protect data if device is lost/stolen.",
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "encryption_enabled": encryption_info.get("encryption_enabled", False),
            "encryption_type": encryption_info.get("encryption_type", "None"),
            "encrypted_volumes": encryption_info.get("encrypted_volumes", []),
            "unencrypted_volumes": encryption_info.get("unencrypted_volumes", 0),
            "status_unknown": encryption_info.get("status_unknown", False),
            "educational_content": self.get_educational_content()
        }

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        if "warnings" in encryption_info:
            result["warnings"] = encryption_info["warnings"]

        return result

    def _get_encryption_info(self) -> Dict:
        """Get encryption information for the current platform."""
        if self.platform == "Windows":
            return self._get_encryption_info_windows()
        elif self.platform == "Darwin":
            return self._get_encryption_info_macos()
        elif self.platform == "Linux":
            return self._get_encryption_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_encryption_info_windows(self) -> Dict:
        """Get BitLocker encryption information on Windows."""
        result = {}
        warnings = []

        try:
            # Check BitLocker status using manage-bde
            ps_bitlocker_cmd = """
            try {
                $Volumes = Get-BitLockerVolume -ErrorAction SilentlyContinue
                $Data = @()
                foreach ($Vol in $Volumes) {
                    $Data += @{
                        MountPoint = $Vol.MountPoint
                        EncryptionMethod = $Vol.EncryptionMethod
                        VolumeStatus = $Vol.VolumeStatus
                        ProtectionStatus = $Vol.ProtectionStatus
                        EncryptionPercentage = $Vol.EncryptionPercentage
                    }
                }
                $Data | ConvertTo-Json
            } catch {
                Write-Output "ERROR: $($_.Exception.Message)"
            }
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_bitlocker_cmd],
                timeout=20
            )

            encryption_enabled = False
            encrypted_volumes = []
            unencrypted_count = 0
            access_denied = False

            if returncode == 0:
                if not stdout or not stdout.strip():
                    # Empty output likely means no volumes found (may need admin)
                    warnings.append("Administrator privileges may be required for detailed BitLocker information")
                    access_denied = True
                elif "ERROR:" in stdout or "Access is denied" in stdout or "not recognized" in stdout or "NO_DATA" in stdout:
                    warnings.append("Administrator privileges required for detailed BitLocker information")
                    access_denied = True
                else:
                    try:
                        volume_data = json.loads(stdout)
                        if isinstance(volume_data, dict):
                            volume_data = [volume_data]

                        # If no volumes returned on Windows, likely need admin
                        if not volume_data or len(volume_data) == 0:
                            warnings.append("Administrator privileges may be required for detailed BitLocker information")
                            access_denied = True

                        for volume in volume_data:
                            mount = volume.get("MountPoint", "Unknown")
                            status = volume.get("VolumeStatus", "Unknown")
                            protection = volume.get("ProtectionStatus", "Unknown")
                            method = volume.get("EncryptionMethod", "None")
                            percent = volume.get("EncryptionPercentage", 0)

                            is_encrypted = (
                                status == "FullyEncrypted" or
                                protection == "On" or
                                percent == 100
                            )

                            if is_encrypted:
                                encryption_enabled = True
                                encrypted_volumes.append({
                                    "volume": mount,
                                    "method": method,
                                    "status": status,
                                    "percentage": percent
                                })
                            else:
                                if mount and mount != "Unknown":
                                    unencrypted_count += 1

                    except json.JSONDecodeError:
                        warnings.append("Could not parse BitLocker information")

            result["encryption_enabled"] = encryption_enabled
            result["encryption_type"] = "BitLocker" if encryption_enabled else "None"
            result["encrypted_volumes"] = encrypted_volumes
            result["unencrypted_volumes"] = unencrypted_count
            result["status_unknown"] = access_denied  # Flag when we couldn't check due to permissions

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check BitLocker status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_encryption_info_macos(self) -> Dict:
        """Get FileVault encryption information on macOS."""
        result = {}
        warnings = []

        try:
            # Check FileVault status using fdesetup
            stdout, stderr, returncode = self.run_command(
                ["fdesetup", "status"],
                timeout=10
            )

            encryption_enabled = False
            encrypted_volumes = []
            encryption_status = "Unknown"
            access_denied = False

            if returncode == 0 and stdout:
                if "FileVault is On" in stdout:
                    encryption_enabled = True
                    encryption_status = "On"
                    encrypted_volumes.append({
                        "volume": "Main System Volume",
                        "method": "FileVault",
                        "status": "Encrypted"
                    })
                elif "FileVault is Off" in stdout:
                    encryption_enabled = False
                    encryption_status = "Off"
                else:
                    encryption_status = "Unknown"
                    warnings.append("Could not determine FileVault status")

            elif "not permitted" in stderr or "permission denied" in stderr.lower():
                warnings.append("Administrator privileges required for FileVault status")
                access_denied = True

            result["encryption_enabled"] = encryption_enabled
            result["encryption_type"] = "FileVault" if encryption_enabled else "None"
            result["encrypted_volumes"] = encrypted_volumes
            result["unencrypted_volumes"] = 0 if encryption_enabled else 1
            result["status_unknown"] = access_denied  # Flag when we couldn't check due to permissions

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check FileVault status: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_encryption_info_linux(self) -> Dict:
        """Get LUKS/dm-crypt encryption information on Linux."""
        result = {}
        warnings = []

        try:
            # Check for LUKS encrypted volumes using lsblk
            stdout, stderr, returncode = self.run_command(
                ["lsblk", "-f"],
                timeout=10
            )

            encryption_enabled = False
            encrypted_volumes = []
            unencrypted_count = 0

            if returncode == 0 and stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if 'crypto_LUKS' in line or 'LUKS' in line:
                        encryption_enabled = True
                        # Extract device name
                        parts = line.split()
                        if parts:
                            device = parts[0]
                            encrypted_volumes.append({
                                "volume": device,
                                "method": "LUKS",
                                "status": "Encrypted"
                            })

            # Alternative: check with dmsetup (requires root usually)
            stdout2, stderr2, returncode2 = self.run_command(
                ["dmsetup", "ls", "--target", "crypt"],
                timeout=10
            )

            if returncode2 == 0 and stdout2.strip():
                # If we get output, there are encrypted volumes
                if not encryption_enabled:
                    encryption_enabled = True
                    warnings.append("Encrypted volumes detected via dmsetup")

            result["encryption_enabled"] = encryption_enabled
            result["encryption_type"] = "LUKS" if encryption_enabled else "None"
            result["encrypted_volumes"] = encrypted_volumes
            result["unencrypted_volumes"] = unencrypted_count
            result["status_unknown"] = False  # Linux commands generally don't require root to list encrypted volumes

            if not encryption_enabled:
                warnings.append("No LUKS encrypted volumes detected. Consider enabling disk encryption.")

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check encryption status: {str(e)}",
                "warnings": warnings
            }

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on encryption status.

        Risk levels:
            - CRITICAL: No encryption enabled (confirmed)
            - MEDIUM: Status unknown (need admin privileges to check)
            - HIGH: Encryption partially enabled (some volumes unencrypted)
            - NONE: Full encryption enabled

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        encryption_enabled = result.get("encryption_enabled", False)
        unencrypted_volumes = result.get("unencrypted_volumes", 0)
        status_unknown = result.get("status_unknown", False)

        # If we couldn't check due to permissions, use MEDIUM risk (not CRITICAL)
        if status_unknown and not encryption_enabled:
            return RiskLevel.MEDIUM

        if not encryption_enabled:
            return RiskLevel.CRITICAL

        if unencrypted_volumes > 0:
            return RiskLevel.HIGH

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
        encryption_type = result.get("encryption_type", "None")
        unencrypted_volumes = result.get("unencrypted_volumes", 0)
        status_unknown = result.get("status_unknown", False)

        # Special case: Status unknown due to insufficient permissions
        if status_unknown and risk_level == "medium":
            return (
                "Could not determine encryption status - Administrator privileges required. "
                "Disk encryption protects your data if device is lost/stolen. "
                "HOW TO FIX: Run DevAudit as Administrator to check encryption status, or manually verify: "
                "Settings → Update & Security → Device encryption (or Settings → Privacy & security → Device encryption)."
            )

        if risk_level == "critical":
            if self.platform == "Windows":
                return (
                    "CRITICAL: Disk encryption is NOT enabled! If your device is lost/stolen, data is vulnerable. "
                    "HOW TO FIX: Settings → Update & Security → Device encryption → Turn on (or Settings → Privacy & security → Device encryption). "
                    "Note: BitLocker requires Windows Pro/Enterprise."
                )
            elif self.platform == "Darwin":
                return (
                    "CRITICAL: FileVault is NOT enabled! If your Mac is lost/stolen, data is vulnerable. "
                    "HOW TO FIX: System Preferences → Security & Privacy → FileVault → Turn On FileVault."
                )
            else:
                return (
                    "CRITICAL: Disk encryption is NOT enabled! If your device is lost/stolen, data is vulnerable. "
                    "HOW TO FIX: Install and configure LUKS encryption or consider full-disk encryption on reinstall."
                )

        elif risk_level == "high":
            return (
                f"Encryption is partially enabled ({encryption_type}), but {unencrypted_volumes} volume(s) remain unencrypted. "
                "Encrypt all drives for full protection. "
                "HOW TO FIX: Enable encryption on remaining volumes."
            )

        else:
            encrypted_count = len(result.get("encrypted_volumes", []))
            return f"Disk encryption is enabled ({encryption_type}). {encrypted_count} volume(s) protected."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about disk encryption.

        Returns:
            Dict with educational content from docs/concepts/disk-encryption.md
        """
        return get_educational_content("disk-encryption")

    def requires_elevation(self) -> bool:
        """
        Check if encryption auditor requires admin/root.

        Returns:
            False - We'll try without admin and warn if needed for detailed info
        """
        return False  # Try without elevation and add warnings if we need admin
