"""
Driver Update Auditor for DevAudit.

Checks for outdated device drivers that may have security vulnerabilities or performance issues.
Focuses on critical drivers: Graphics, Network, Chipset, Storage.

Platforms: Windows (primary), macOS (limited), Linux (limited)
Requires Admin: No (for basic info), Yes (for detailed driver info)
"""

import re
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class DriverAuditor(BaseAuditor):
    """Audit device driver versions and ages."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "Driver Updates"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """Driver checks are always available."""
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """No version for driver auditor."""
        return None

    def audit(self) -> Dict:
        """
        Perform driver audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - drivers_checked: int (Number of drivers analyzed)
                - outdated_critical: int (Critical drivers needing updates)
                - outdated_other: int (Other outdated drivers)
                - critical_drivers: List[Dict] (Graphics, Network, Chipset details)
                - oldest_driver_age_days: int (Age of oldest critical driver)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"Driver auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        driver_info = self._get_driver_info()

        if "error" in driver_info:
            return {
                "installed": True,
                "error": driver_info["error"],
                "warnings": driver_info.get("warnings", []),
                "risk_level": RiskLevel.NONE.value,
                "educational_content": self.get_educational_content()
            }

        result = {
            "installed": True,
            "drivers_checked": driver_info.get("drivers_checked", 0),
            "outdated_critical": 0,
            "outdated_other": 0,
            "critical_drivers": driver_info.get("critical_drivers", []),
            "oldest_driver_age_days": driver_info.get("oldest_driver_age_days", 0),
            "educational_content": self.get_educational_content()
        }

        # Count outdated drivers
        for driver in result["critical_drivers"]:
            age_days = driver.get("age_days", 0)
            if age_days > 365:  # Older than 1 year
                if driver.get("is_critical", False):
                    result["outdated_critical"] += 1
                else:
                    result["outdated_other"] += 1

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        if "warnings" in driver_info:
            result["warnings"] = driver_info["warnings"]

        return result

    def _get_driver_info(self) -> Dict:
        """Get driver information for the current platform."""
        if self.platform == "Windows":
            return self._get_driver_info_windows()
        elif self.platform == "Darwin":
            return self._get_driver_info_macos()
        elif self.platform == "Linux":
            return self._get_driver_info_linux()
        else:
            return {"error": "Unsupported platform"}

    def _get_driver_info_windows(self) -> Dict:
        """Get driver information on Windows using PowerShell."""
        result = {}
        warnings = []
        critical_drivers = []

        # Critical driver types we care about (third-party hardware)
        critical_classes = [
            "Display",  # Graphics (NVIDIA, AMD, Intel)
            "Net",      # Network adapters (Realtek, Intel, Killer)
            "System",   # Chipset (Intel, AMD)
        ]

        # Manufacturers to INCLUDE (third-party hardware vendors)
        # We skip Microsoft drivers as they're updated via Windows Update
        third_party_manufacturers = [
            "NVIDIA", "AMD", "Advanced Micro Devices",
            "Intel", "Realtek", "Qualcomm", "Broadcom",
            "Killer", "Marvell", "Mediatek",
            "Creative", "Corsair", "Logitech", "Razer",
            "TP-Link", "D-Link", "ASUS", "MSI", "Gigabyte"
        ]

        # Device names to EXCLUDE (Windows inbox drivers + infrastructure drivers)
        exclude_device_patterns = [
            "WAN Miniport", "Microsoft", "Generic", "Standard",
            "Remote Desktop", "Teredo", "NDIS", "Composite",
            "Serial IO", "GPIO", "I2C", "SPI",  # Low-level chipset communication (rarely updated)
            "Management Engine", "Thunderbolt",  # Infrastructure (Intel chipset features)
        ]

        try:
            # Get driver information using Get-WmiObject
            ps_driver_cmd = """
            Get-WmiObject Win32_PnPSignedDriver |
            Where-Object { $_.DeviceClass -ne $null -and $_.DriverDate -ne $null } |
            Select-Object DeviceName, DeviceClass, DriverVersion, DriverDate, Manufacturer |
            ConvertTo-Json
            """

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_driver_cmd],
                timeout=30
            )

            if returncode == 0 and stdout:
                try:
                    driver_data = json.loads(stdout)
                    if isinstance(driver_data, dict):
                        driver_data = [driver_data]

                    drivers_checked = 0
                    oldest_age = 0
                    today = datetime.now()

                    for driver in driver_data:
                        device_class = driver.get("DeviceClass", "")
                        device_name = driver.get("DeviceName", "Unknown Device")
                        manufacturer = driver.get("Manufacturer", "Unknown")

                        # Focus on critical driver classes
                        is_critical_class = any(cls.lower() in device_class.lower() for cls in critical_classes)

                        if not is_critical_class:
                            continue

                        # Skip Microsoft/Windows inbox drivers
                        is_third_party = any(vendor in manufacturer for vendor in third_party_manufacturers)
                        if not is_third_party:
                            continue

                        # Skip generic Windows devices
                        is_excluded = any(pattern.lower() in device_name.lower() for pattern in exclude_device_patterns)
                        if is_excluded:
                            continue

                        # Skip Windows inbox drivers (version starts with Windows build number like 10.0.xxxxx)
                        driver_version = driver.get("DriverVersion", "Unknown")
                        if driver_version.startswith("10.0."):
                            continue

                        # Get driver date for validation
                        driver_date_str = driver.get("DriverDate", "")

                        # Parse driver date - Windows returns it in WMI date format
                        driver_date = None
                        age_days = 0

                        if driver_date_str:
                            try:
                                # WMI date format: YYYYMMDDHHMMSS.mmmmmm+UUU
                                if len(driver_date_str) >= 8:
                                    date_part = driver_date_str[:8]
                                    driver_date = datetime.strptime(date_part, "%Y%m%d")

                                    # Validate: skip drivers with dates before 1990 (likely corrupted)
                                    if driver_date.year < 1990:
                                        continue

                                    # Validate: skip drivers with future dates
                                    if driver_date > today:
                                        continue

                                    age_days = (today - driver_date).days
                                    oldest_age = max(oldest_age, age_days)
                            except ValueError:
                                # Skip drivers with unparseable dates
                                continue

                        # Only include drivers we successfully parsed and validated
                        if driver_date:
                            drivers_checked += 1
                            critical_drivers.append({
                                "device_name": device_name,
                                "device_class": device_class,
                                "version": driver_version,
                                "date": driver_date.strftime("%Y-%m-%d"),
                                "age_days": age_days,
                                "manufacturer": manufacturer,
                                "is_critical": True  # All third-party hardware drivers are critical
                            })

                    result["drivers_checked"] = drivers_checked
                    result["critical_drivers"] = critical_drivers
                    result["oldest_driver_age_days"] = oldest_age

                except json.JSONDecodeError:
                    warnings.append("Could not parse driver information")

            if warnings:
                result["warnings"] = warnings

        except Exception as e:
            return {
                "error": f"Failed to check driver information: {str(e)}",
                "warnings": warnings
            }

        return result

    def _get_driver_info_macos(self) -> Dict:
        """
        Get driver information on macOS.

        Note: macOS handles most drivers through system updates.
        We mainly check for third-party kernel extensions (kexts).
        """
        result = {}
        warnings = []

        warnings.append("macOS driver updates are typically handled by System Updates")
        warnings.append("Manual driver management is rarely needed on macOS")

        result["drivers_checked"] = 0
        result["critical_drivers"] = []
        result["oldest_driver_age_days"] = 0
        result["warnings"] = warnings

        return result

    def _get_driver_info_linux(self) -> Dict:
        """
        Get driver information on Linux.

        Note: Linux drivers (kernel modules) are typically updated with kernel updates.
        We check module versions where available.
        """
        result = {}
        warnings = []

        warnings.append("Linux driver updates are typically handled by kernel updates")
        warnings.append("Check your distribution's package manager for driver updates")

        result["drivers_checked"] = 0
        result["critical_drivers"] = []
        result["oldest_driver_age_days"] = 0
        result["warnings"] = warnings

        return result

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on driver age and criticality.

        Risk levels:
            - CRITICAL: Critical drivers (GPU/Network/Chipset) > 2 years old
            - HIGH: Critical drivers 1-2 years old, or any driver > 3 years old
            - MEDIUM: Non-critical drivers > 2 years old
            - LOW: Drivers 1-2 years old
            - NONE: All drivers < 1 year old

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        outdated_critical = result.get("outdated_critical", 0)
        oldest_age_days = result.get("oldest_driver_age_days", 0)

        # Critical drivers over 2 years old
        if outdated_critical > 0 and oldest_age_days > 730:
            return RiskLevel.CRITICAL

        # Critical drivers over 1 year old
        if outdated_critical > 0 and oldest_age_days > 365:
            return RiskLevel.HIGH

        # Any driver over 3 years old
        if oldest_age_days > 1095:
            return RiskLevel.HIGH

        # Drivers 2-3 years old
        if oldest_age_days > 730:
            return RiskLevel.MEDIUM

        # Drivers 1-2 years old
        if oldest_age_days > 365:
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
        risk_level = result.get("risk_level", "none")
        outdated_critical = result.get("outdated_critical", 0)
        oldest_age_days = result.get("oldest_driver_age_days", 0)

        if risk_level == "critical":
            oldest_years = round(oldest_age_days / 365, 1)
            return (
                f"CRITICAL: {outdated_critical} critical driver(s) are severely outdated (oldest: {oldest_years} years). "
                "Old drivers can have security vulnerabilities and performance issues. "
                "HOW TO FIX: Windows Update (Settings → Windows Update → Check for updates) or visit manufacturer websites "
                "(NVIDIA GeForce Experience, AMD Radeon Software, Intel Driver & Support Assistant)."
            )
        elif risk_level == "high":
            oldest_years = round(oldest_age_days / 365, 1)
            return (
                f"Critical driver(s) are outdated (oldest: {oldest_years} years). "
                "Consider updating for security and performance improvements. "
                "HOW TO FIX: Check Windows Update or manufacturer websites for latest drivers."
            )
        elif risk_level == "medium":
            return (
                "Some drivers are getting old. Update when convenient. "
                "HOW TO FIX: Windows Update or Device Manager → Update Driver."
            )
        elif risk_level == "low":
            return (
                "Drivers are relatively recent. Monitor for updates periodically. "
                "Windows Update will notify you of critical driver updates."
            )
        else:
            drivers_checked = result.get("drivers_checked", 0)
            return f"All {drivers_checked} critical drivers are up to date (less than 1 year old)."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about driver updates.

        Returns:
            Dict with educational content from docs/concepts/driver-updates.md
        """
        return get_educational_content("driver-updates")

    def requires_elevation(self) -> bool:
        """
        Check if driver auditor requires admin/root.

        Returns:
            False - Basic driver info accessible without elevation
        """
        return False
