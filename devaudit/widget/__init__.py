"""
DevAudit Widget Module

System tray/menu bar widget for real-time security status monitoring.
"""

from .icons import generate_shield_icon, get_icon_for_status
from .tray import SystemTrayWidget, run_widget

__all__ = ["generate_shield_icon", "get_icon_for_status", "SystemTrayWidget", "run_widget"]
