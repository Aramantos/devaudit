"""
System tray widget for DevAudit.

Cross-platform system tray icon that shows security status at a glance.
"""

import threading
import time
import webbrowser
from typing import Optional
import requests

try:
    import pystray
    from pystray import MenuItem as Item
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

from .icons import get_icon_for_status


class SystemTrayWidget:
    """
    Cross-platform system tray widget for DevAudit.

    Shows security status as a color-coded shield icon in the system tray.
    """

    def __init__(self, api_url: str = "http://127.0.0.1:8888", update_interval: int = 300):
        """
        Initialize system tray widget.

        Args:
            api_url: Base URL for DevAudit API
            update_interval: Status update interval in seconds (default: 5 minutes)
        """
        if not PYSTRAY_AVAILABLE:
            raise ImportError(
                "pystray is required for system tray widget. "
                "Install it with: pip install pystray pillow"
            )

        self.api_url = api_url.rstrip("/")
        self.update_interval = update_interval
        self.icon: Optional[pystray.Icon] = None
        self.current_status = {
            "status": "unknown",
            "summary": "Connecting...",
            "color": "gray"
        }
        self.running = False
        self.update_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the system tray widget."""
        self.running = True

        # Create icon
        icon_image = get_icon_for_status(self.current_status["status"])

        self.icon = pystray.Icon(
            "DevAudit",
            icon_image,
            "DevAudit - " + self.current_status["summary"],
            menu=self._create_menu()
        )

        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

        # Run icon (blocks until quit)
        self.icon.run()

    def stop(self):
        """Stop the system tray widget."""
        self.running = False
        if self.icon:
            self.icon.stop()

    def _create_menu(self):
        """Create the context menu for the tray icon."""
        return pystray.Menu(
            Item("Open Dashboard", self._open_dashboard, default=True),
            Item("Run Scan Now", self._run_scan),
            Item("Refresh Status", self._refresh_status),
            pystray.Menu.SEPARATOR,
            Item("About DevAudit", self._show_about),
            Item("Quit", self._quit)
        )

    def _update_loop(self):
        """Background thread that updates status periodically."""
        # Initial update
        self._fetch_and_update_status()

        while self.running:
            time.sleep(self.update_interval)
            if not self.running:
                break
            self._fetch_and_update_status()

    def _fetch_and_update_status(self):
        """Fetch status from API and update icon."""
        try:
            response = requests.get(
                f"{self.api_url}/api/status/quick",
                timeout=10
            )
            response.raise_for_status()

            status_data = response.json()

            # Update current status
            self.current_status = {
                "status": status_data.get("status", "unknown"),
                "summary": status_data.get("summary", "Unknown status"),
                "color": status_data.get("color", "gray"),
                "counts": status_data.get("counts", {}),
            }

            # Update icon if still running
            if self.running and self.icon:
                self._update_icon()

        except requests.exceptions.ConnectionError:
            self.current_status = {
                "status": "error",
                "summary": "Cannot connect to DevAudit",
                "color": "gray"
            }
            if self.running and self.icon:
                self._update_icon()

        except Exception as e:
            self.current_status = {
                "status": "error",
                "summary": f"Error: {str(e)[:30]}...",
                "color": "gray"
            }
            if self.running and self.icon:
                self._update_icon()

    def _update_icon(self):
        """Update the tray icon image and tooltip."""
        if not self.icon:
            return

        # Generate new icon image
        new_image = get_icon_for_status(self.current_status["status"])

        # Update icon
        self.icon.icon = new_image

        # Update tooltip
        tooltip_text = f"DevAudit - {self.current_status['summary']}"

        # Add counts if available
        counts = self.current_status.get("counts", {})
        if counts:
            details = []
            if counts.get("critical", 0) > 0:
                details.append(f"Critical: {counts['critical']}")
            if counts.get("high", 0) > 0:
                details.append(f"High: {counts['high']}")
            if counts.get("medium", 0) > 0:
                details.append(f"Medium: {counts['medium']}")

            if details:
                tooltip_text += "\n" + " | ".join(details)

        self.icon.title = tooltip_text

    def _open_dashboard(self, icon=None, item=None):
        """Open DevAudit dashboard in browser."""
        webbrowser.open(self.api_url)

    def _run_scan(self, icon=None, item=None):
        """Trigger a new scan."""
        try:
            # Open dashboard and trigger scan via WebSocket
            # For now, just open dashboard (user can click scan button)
            self._open_dashboard()
        except Exception as e:
            print(f"Error triggering scan: {e}")

    def _refresh_status(self, icon=None, item=None):
        """Manually refresh status."""
        # Run update in background thread
        threading.Thread(target=self._fetch_and_update_status, daemon=True).start()

    def _show_about(self, icon=None, item=None):
        """Show about information."""
        # Open DevAudit GitHub page
        webbrowser.open("https://github.com/Aramantos/devaudit")

    def _quit(self, icon=None, item=None):
        """Quit the widget."""
        self.stop()


def run_widget(api_url: str = "http://127.0.0.1:8888", update_interval: int = 300):
    """
    Run the system tray widget.

    Args:
        api_url: Base URL for DevAudit API
        update_interval: Status update interval in seconds (default: 5 minutes)
    """
    if not PYSTRAY_AVAILABLE:
        print("Error: pystray is not installed.")
        print("Install it with: pip install devaudit[widget]")
        print("Or: pip install pystray pillow")
        return 1

    try:
        widget = SystemTrayWidget(api_url=api_url, update_interval=update_interval)
        print(f"Starting DevAudit widget (polling every {update_interval}s)...")
        print(f"API: {api_url}")
        print("Right-click the system tray icon for options.")
        widget.start()
        return 0
    except KeyboardInterrupt:
        print("\nWidget stopped by user.")
        return 0
    except Exception as e:
        print(f"Error starting widget: {e}")
        import traceback
        traceback.print_exc()
        return 1
