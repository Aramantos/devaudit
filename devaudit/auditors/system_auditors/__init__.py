"""
System-level auditors for v0.3.0+

This package contains auditors for system-wide security monitoring:
    - BIOS/UEFI auditor
    - OS update auditor
    - Antivirus status auditor
    - Driver update auditor
    - Disk health auditor
    - Backup status auditor
    - Encryption auditor
    - Firewall auditor

All system auditors inherit from BaseAuditor and provide:
    - Educational content for findings
    - Risk assessment (none/low/medium/high/critical)
    - Cross-platform support (Windows/macOS/Linux)
    - Graceful degradation without admin privileges
"""

# System auditors
from .bios_audit import BIOSAuditor

# Placeholders for future auditors (v0.3.0)
# from .os_audit import OSAuditor
# from .antivirus_audit import AntivirusAuditor
# from .driver_audit import DriverAuditor
# from .disk_audit import DiskAuditor
# from .backup_audit import BackupAuditor
# from .encryption_audit import EncryptionAuditor
# from .firewall_audit import FirewallAuditor

__all__ = [
    "BIOSAuditor",
    # Will be populated as more auditors are implemented
]
