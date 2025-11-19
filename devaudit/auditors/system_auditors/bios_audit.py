"""
BIOS/UEFI Auditor for DevAudit.

Checks BIOS/UEFI version and detects potential security risks from outdated firmware.

Platforms: Windows, macOS, Linux
Requires Admin: No (but limited info without admin on some platforms)
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path

from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory
from devaudit.educational import get_educational_content


class BIOSAuditor(BaseAuditor):
    """Audit BIOS/UEFI version and age."""

    def __init__(self, target_dir: Optional[str] = None):
        super().__init__(target_dir)
        self.name = "BIOS/UEFI"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """
        Check if BIOS auditor can run.

        BIOS is always "installed" (every computer has BIOS/UEFI),
        but we might not be able to read it without proper permissions.
        """
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """Get BIOS version string."""
        bios_info = self._get_bios_info()
        return bios_info.get("version")

    def audit(self) -> Dict:
        """
        Perform BIOS audit.

        Returns:
            Dict containing:
                - installed: bool (always True if can run)
                - vendor: str (BIOS manufacturer)
                - version: str (BIOS version)
                - release_date: str (BIOS release date)
                - motherboard: str (Motherboard model)
                - age_days: int (Days since BIOS release)
                - risk_level: str (none/low/medium/high/critical)
                - recommendation: str (What to do)
                - educational_content: dict (Educational content)
                - warnings: list (Any issues encountered)
        """
        if not self.can_run():
            return {
                "installed": False,
                "reason": f"BIOS auditor requires {self.get_platform_name()} platform",
                "risk_level": RiskLevel.NONE.value
            }

        bios_info = self._get_bios_info()

        if not bios_info.get("version"):
            return {
                "installed": True,
                "error": "Could not detect BIOS information",
                "warnings": [
                    "BIOS information unavailable",
                    "This may require administrator/root privileges"
                ],
                "risk_level": RiskLevel.NONE.value,
                "educational_content": self.get_educational_content()
            }

        # Calculate BIOS age
        age_days = self._calculate_age(bios_info.get("release_date"))

        result = {
            "installed": True,
            "vendor": bios_info.get("vendor", "Unknown"),
            "version": bios_info.get("version", "Unknown"),
            "release_date": bios_info.get("release_date", "Unknown"),
            "motherboard": bios_info.get("motherboard", "Unknown"),
            "age_days": age_days,
            "educational_content": self.get_educational_content()
        }

        # Assess risk and add recommendation
        result["risk_level"] = self.assess_risk(result).value
        result["recommendation"] = self._get_recommendation(result)

        return result

    def _get_bios_info(self) -> Dict[str, str]:
        """
        Get BIOS information for the current platform.

        Returns:
            Dict with vendor, version, release_date, motherboard
        """
        if self.platform == "Windows":
            return self._get_bios_info_windows()
        elif self.platform == "Darwin":
            return self._get_bios_info_macos()
        elif self.platform == "Linux":
            return self._get_bios_info_linux()
        else:
            return {}

    def _get_bios_info_windows(self) -> Dict[str, str]:
        """Get BIOS information on Windows using PowerShell (more reliable than wmic)."""
        result = {}

        try:
            # Use PowerShell to get BIOS info (more reliable than wmic)
            ps_command = "Get-CimInstance -ClassName Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Json"

            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_command],
                timeout=15
            )

            if returncode == 0 and stdout:
                import json
                try:
                    data = json.loads(stdout)
                    if data:
                        result["vendor"] = data.get("Manufacturer", "Unknown")
                        result["version"] = data.get("SMBIOSBIOSVersion", "Unknown")

                        # Parse ReleaseDate (format: /Date(1234567890000)/ or /Date(1234567890000-000)/)
                        release_date = data.get("ReleaseDate")
                        if release_date:
                            # Try to extract date from various formats
                            if isinstance(release_date, dict) and "DateTime" in release_date:
                                result["release_date"] = release_date["DateTime"].split("T")[0]
                            elif isinstance(release_date, str):
                                import re
                                from datetime import datetime

                                # Format: /Date(1732924800000)/ (Unix timestamp in milliseconds)
                                date_match = re.search(r'/Date\((\d+)', release_date)
                                if date_match:
                                    timestamp_ms = int(date_match.group(1))
                                    timestamp_s = timestamp_ms / 1000
                                    date_obj = datetime.fromtimestamp(timestamp_s)
                                    result["release_date"] = date_obj.strftime("%Y-%m-%d")
                                # Format: YYYYMMDD
                                elif re.match(r'^\d{8}$', release_date):
                                    result["release_date"] = f"{release_date[0:4]}-{release_date[4:6]}-{release_date[6:8]}"
                                # Format: YYYY-MM-DD
                                elif re.match(r'^\d{4}-\d{2}-\d{2}', release_date):
                                    result["release_date"] = release_date.split("T")[0]
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    # PowerShell JSON parsing failed, try wmic fallback
                    pass

            # If PowerShell failed, try wmic fallback
            if not result.get("version"):
                stdout, stderr, returncode = self.run_command(
                    ["wmic", "bios", "get", "manufacturer,smbiosbiosversion,releasedate"],
                    timeout=10
                )

                if returncode == 0 and stdout:
                    lines = stdout.strip().split('\n')
                    if len(lines) >= 2:
                        # Parse output (format: Manufacturer  ReleaseDate  SMBIOSBIOSVersion)
                        data_line = lines[1].strip()
                        parts = data_line.split()
                        if len(parts) >= 3:
                            result["vendor"] = parts[0]
                            result["release_date"] = self._parse_windows_date(parts[1])
                            result["version"] = parts[2]

            # Get motherboard information
            ps_board_command = "Get-CimInstance -ClassName Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json"
            stdout, stderr, returncode = self.run_command(
                ["powershell", "-Command", ps_board_command],
                timeout=15
            )

            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    if data:
                        manufacturer = data.get("Manufacturer", "")
                        product = data.get("Product", "")
                        if manufacturer and product:
                            result["motherboard"] = f"{manufacturer} {product}"
                except (json.JSONDecodeError, KeyError):
                    pass

            # Fallback to wmic for motherboard if PowerShell failed
            if not result.get("motherboard"):
                stdout, stderr, returncode = self.run_command(
                    ["wmic", "baseboard", "get", "manufacturer,product"],
                    timeout=10
                )

                if returncode == 0 and stdout:
                    lines = stdout.strip().split('\n')
                    if len(lines) >= 2:
                        data_line = lines[1].strip()
                        parts = data_line.split(maxsplit=1)
                        if len(parts) >= 2:
                            result["motherboard"] = f"{parts[0]} {parts[1]}"

        except Exception as e:
            # If all methods fail, return empty result
            pass

        return result

    def _get_bios_info_macos(self) -> Dict[str, str]:
        """Get BIOS (EFI) information on macOS."""
        result = {}

        # macOS uses EFI, get boot ROM version
        stdout, stderr, returncode = self.run_command(
            ["system_profiler", "SPHardwareDataType"],
            timeout=10
        )

        if returncode == 0 and stdout:
            # Parse output for Boot ROM Version
            match = re.search(r'Boot ROM Version:\s*(.+)', stdout)
            if match:
                result["version"] = match.group(1).strip()
                result["vendor"] = "Apple"

            # Parse for Model Identifier
            match = re.search(r'Model Identifier:\s*(.+)', stdout)
            if match:
                result["motherboard"] = match.group(1).strip()

            # macOS firmware updates are tied to OS updates
            # Use system version as proxy for firmware date
            match = re.search(r'System Firmware Version:\s*(.+)', stdout)
            if match:
                result["release_date"] = "Unknown (check macOS version)"

        return result

    def _get_bios_info_linux(self) -> Dict[str, str]:
        """Get BIOS information on Linux using dmidecode."""
        result = {}

        # Try dmidecode (requires root, but may work without for some info)
        stdout, stderr, returncode = self.run_command(
            ["dmidecode", "-t", "bios"],
            timeout=10
        )

        if returncode == 0 and stdout:
            # Parse dmidecode output
            vendor_match = re.search(r'Vendor:\s*(.+)', stdout)
            if vendor_match:
                result["vendor"] = vendor_match.group(1).strip()

            version_match = re.search(r'Version:\s*(.+)', stdout)
            if version_match:
                result["version"] = version_match.group(1).strip()

            date_match = re.search(r'Release Date:\s*(.+)', stdout)
            if date_match:
                result["release_date"] = date_match.group(1).strip()

        # Try to get motherboard info
        stdout, stderr, returncode = self.run_command(
            ["dmidecode", "-t", "baseboard"],
            timeout=10
        )

        if returncode == 0 and stdout:
            manufacturer_match = re.search(r'Manufacturer:\s*(.+)', stdout)
            product_match = re.search(r'Product Name:\s*(.+)', stdout)

            if manufacturer_match and product_match:
                manufacturer = manufacturer_match.group(1).strip()
                product = product_match.group(1).strip()
                result["motherboard"] = f"{manufacturer} {product}"

        # Fallback: Try reading from sysfs (doesn't require root)
        if not result.get("version"):
            bios_version_path = Path("/sys/class/dmi/id/bios_version")
            if bios_version_path.exists():
                try:
                    result["version"] = bios_version_path.read_text(encoding='utf-8').strip()
                except Exception:
                    pass

        if not result.get("vendor"):
            bios_vendor_path = Path("/sys/class/dmi/id/bios_vendor")
            if bios_vendor_path.exists():
                try:
                    result["vendor"] = bios_vendor_path.read_text(encoding='utf-8').strip()
                except Exception:
                    pass

        if not result.get("release_date"):
            bios_date_path = Path("/sys/class/dmi/id/bios_date")
            if bios_date_path.exists():
                try:
                    result["release_date"] = bios_date_path.read_text(encoding='utf-8').strip()
                except Exception:
                    pass

        return result

    def _parse_windows_date(self, date_str: str) -> str:
        """
        Parse Windows BIOS date format.

        Windows returns dates like: 20221215000000.000000+000
        Convert to: 2022-12-15
        """
        try:
            # Extract YYYYMMDD from the beginning
            if len(date_str) >= 8:
                year = date_str[0:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}"
        except Exception:
            pass
        return date_str

    def _calculate_age(self, release_date: Optional[str]) -> Optional[int]:
        """
        Calculate BIOS age in days.

        Args:
            release_date: Release date string (various formats)

        Returns:
            Age in days, or None if can't parse
        """
        if not release_date or release_date == "Unknown":
            return None

        try:
            # Try parsing common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    date_obj = datetime.strptime(release_date, fmt)
                    age = (datetime.now() - date_obj).days
                    return age
                except ValueError:
                    continue
        except Exception:
            pass

        return None

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk based on BIOS age.

        Risk levels:
            - CRITICAL: BIOS >3 years old (1095 days)
            - HIGH: BIOS 2-3 years old (730-1095 days)
            - MEDIUM: BIOS 1-2 years old (365-730 days)
            - LOW: BIOS <1 year old (<365 days)
            - NONE: Can't determine age

        Args:
            result: Audit result dict

        Returns:
            RiskLevel enum
        """
        age_days = result.get("age_days")

        if age_days is None:
            return RiskLevel.NONE

        if age_days > 1095:  # >3 years
            return RiskLevel.CRITICAL
        elif age_days > 730:  # 2-3 years
            return RiskLevel.HIGH
        elif age_days > 365:  # 1-2 years
            return RiskLevel.MEDIUM
        else:  # <1 year
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
        age_days = result.get("age_days")

        if risk_level == "critical":
            return (
                f"BIOS is {age_days} days old (>3 years). "
                "Strongly recommend checking for updates—outdated BIOS may have security vulnerabilities."
            )
        elif risk_level == "high":
            return (
                f"BIOS is {age_days} days old (2-3 years). "
                "Consider checking manufacturer website for BIOS updates."
            )
        elif risk_level == "medium":
            return (
                f"BIOS is {age_days} days old (1-2 years). "
                "Check for updates during next maintenance window."
            )
        elif risk_level == "low":
            return (
                f"BIOS is {age_days} days old (<1 year). "
                "No immediate action needed—BIOS is relatively recent."
            )
        else:
            return "BIOS age could not be determined. Check manufacturer website for latest version."

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about BIOS/UEFI.

        Returns:
            Dict with educational content from docs/concepts/bios-uefi.md
        """
        return get_educational_content("bios-uefi")

    def requires_elevation(self) -> bool:
        """
        Check if BIOS auditor requires admin/root.

        Returns:
            False - BIOS auditor can run without admin (may have limited info)
        """
        # We can get BIOS info without admin on most platforms
        # (Windows: wmic works without admin, Linux: sysfs works, macOS: system_profiler works)
        return False
