# DevAudit Widget Architecture

**Created:** 2025-01-20
**Status:** Design Phase
**Target Version:** v0.4.0 - v0.5.0
**Purpose:** Persistent system status monitoring via desktop/mobile widgets

---

## Vision

A **lightweight, always-visible security status indicator** that shows your system's health at a glance:

- 🖥️ **Desktop**: System tray icon (Windows), menu bar (macOS), system tray (Linux)
- 📱 **Mobile**: Home screen widgets (Android, iOS)
- 🎨 **Visual**: Color-coded status (Green = Secure, Yellow = Warnings, Red = Critical)
- ⚡ **Performance**: Minimal resource usage (<1% CPU, <20MB RAM)
- 🔒 **Privacy**: 100% local, no cloud dependencies

### User Experience

**At a Glance:**
- Green shield icon: "All systems secure"
- Yellow shield icon: "3 warnings"
- Red shield icon: "Critical issues detected"

**Click/Tap:**
- Opens full DevAudit dashboard
- Shows quick summary of findings
- One-click actions (update, scan, fix)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DevAudit Core                            │
│  (Python Backend - FastAPI + Background Scanner)            │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Auditors  │  │   Scan     │  │  History   │            │
│  │            │→ │  Engine    │→ │  Manager   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         ↓                                                    │
│  ┌─────────────────────────────────────────┐                │
│  │      Widget Status API (REST + SSE)     │                │
│  │  /api/status/quick  (lightweight poll)  │                │
│  │  /api/status/stream (Server-Sent Events)│                │
│  └─────────────────────────────────────────┘                │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴────────────┐
        │                       │
┌───────▼────────┐    ┌─────────▼──────────┐
│ Desktop Widgets │    │  Mobile Widgets    │
│                 │    │                    │
│ • System Tray   │    │ • Android Widget   │
│ • Menu Bar      │    │ • iOS Widget       │
│ • Notification  │    │ • Lock Screen      │
└─────────────────┘    └────────────────────┘
```

---

## Desktop Implementation

### 1. Windows System Tray Icon

**Technology:**
- **Python**: `pystray` (cross-platform system tray library)
- **Alternative**: `PyQt6` QSystemTrayIcon (more features, heavier)

**Features:**
- Icon changes based on status (green/yellow/red shield)
- Tooltip shows brief summary: "DevAudit: 3 warnings, 1 critical"
- Right-click menu:
  - "Open Dashboard"
  - "Run Scan Now"
  - "View Findings"
  - "Settings"
  - "Quit"
- Notification toasts for new findings
- Auto-starts with Windows (optional)

**Implementation:**
```python
# devaudit/widget/desktop_tray.py
import pystray
from PIL import Image
from devaudit.server.app import get_status_summary

def create_tray_icon():
    status = get_status_summary()  # API call to backend
    icon_color = get_icon_color(status)

    image = generate_shield_icon(icon_color)

    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard", open_dashboard),
        pystray.MenuItem("Run Scan", run_scan),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)
    )

    icon = pystray.Icon(
        "DevAudit",
        image,
        "DevAudit - Security Assistant",
        menu
    )

    return icon
```

**Auto-Start (Windows):**
```python
import winreg

def add_to_startup():
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "DevAudit", 0, winreg.REG_SZ, sys.executable + " -m devaudit.widget")
    winreg.CloseKey(key)
```

### 2. macOS Menu Bar

**Technology:**
- **Python**: `rumps` (Ridiculously Uncomplicated macOS Python Statusbar apps)
- **Alternative**: `PyQt6` (cross-platform)

**Features:**
- Icon in menu bar (system tray at top-right)
- Dropdown menu on click
- Native macOS notifications
- Integrates with Notification Center
- Dark mode support

**Implementation:**
```python
# devaudit/widget/macos_menubar.py
import rumps
from devaudit.server.app import get_status_summary

class DevAuditMenuBar(rumps.App):
    def __init__(self):
        super(DevAuditMenuBar, self).__init__("DevAudit", icon="shield_green.png")
        self.menu = [
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            rumps.MenuItem("Run Scan", callback=self.run_scan),
            None,  # Separator
            rumps.MenuItem("Settings", callback=self.open_settings),
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

        # Update status every 5 minutes
        self.timer = rumps.Timer(self.update_status, 300)
        self.timer.start()

    def update_status(self, _):
        status = get_status_summary()
        self.icon = f"shield_{status['color']}.png"
        self.title = f"{status['critical']}⚠" if status['critical'] > 0 else ""

    @rumps.clicked("Open Dashboard")
    def open_dashboard(self, _):
        import webbrowser
        webbrowser.open("http://localhost:8888")
```

**Auto-Start (macOS):**
```xml
<!-- ~/Library/LaunchAgents/com.devaudit.widget.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devaudit.widget</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/devaudit</string>
        <string>widget</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### 3. Linux System Tray

**Technology:**
- **Python**: `pystray` (works with most DEs)
- **Alternative**: `PyQt6` (best compatibility)

**Features:**
- Works with GNOME, KDE, XFCE, i3, etc.
- StatusNotifierItem protocol (modern standard)
- DBus notifications
- Desktop file for autostart

**Implementation:**
```python
# Same as Windows (pystray is cross-platform)
# But with Linux-specific autostart
```

**Auto-Start (Linux):**
```desktop
# ~/.config/autostart/devaudit.desktop
[Desktop Entry]
Type=Application
Name=DevAudit Widget
Exec=/usr/bin/devaudit widget
Icon=devaudit
Comment=DevAudit Security Widget
Categories=System;Security;
Terminal=false
X-GNOME-Autostart-enabled=true
```

---

## Mobile Implementation

### 1. Android Widget

**Technology:**
- **Native**: Kotlin/Java (best performance, native APIs)
- **Flutter**: Cross-platform (Dart, works on iOS too)
- **React Native**: JavaScript (heavier, but familiar for web devs)

**Widget Types:**
- **Small (2x2)**: Icon + status color
- **Medium (4x2)**: Status summary + risk count
- **Large (4x4)**: Detailed findings list

**Features:**
- Home screen widget
- Lock screen widget (Android 13+)
- Background updates (WorkManager, every 15-60 minutes)
- Tap to open app
- Material 3 design

**Implementation (Kotlin):**
```kotlin
// android/app/src/main/java/com/devaudit/widget/StatusWidget.kt
class StatusWidget : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            val status = DevAuditClient.getStatusSummary()

            val views = RemoteViews(context.packageName, R.layout.widget_layout)
            views.setTextViewText(R.id.status_text, status.summary)
            views.setInt(R.id.status_icon, "setColorFilter", status.color)

            // Tap to open app
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(context, 0, intent, 0)
            views.setOnClickPendingIntent(R.id.widget_layout, pendingIntent)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
```

**Background Updates:**
```kotlin
// Use WorkManager for periodic updates
class WidgetUpdateWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val status = DevAuditClient.getStatusSummary()
        updateWidgets(status)
        return Result.success()
    }
}

// Schedule periodic work (every 30 minutes)
WorkManager.getInstance(context).enqueuePeriodicWork(
    PeriodicWorkRequestBuilder<WidgetUpdateWorker>(30, TimeUnit.MINUTES).build()
)
```

### 2. iOS Widget (WidgetKit)

**Technology:**
- **SwiftUI**: Native iOS widget framework (iOS 14+)
- **WidgetKit**: Apple's widget API

**Widget Sizes:**
- **Small**: Icon + status color
- **Medium**: Status summary + risk count
- **Large**: Detailed findings list

**Features:**
- Home screen widget
- Lock screen widget (iOS 16+)
- Smart Stack support
- Timeline updates (refreshed by iOS)
- Deep links to app

**Implementation (Swift):**
```swift
// ios/Widget/StatusWidget.swift
import WidgetKit
import SwiftUI

struct StatusWidget: Widget {
    let kind: String = "StatusWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: StatusProvider()) { entry in
            StatusWidgetView(entry: entry)
        }
        .configurationDisplayName("DevAudit")
        .description("Monitor your system security status")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

struct StatusWidgetView: View {
    var entry: StatusEntry

    var body: some View {
        VStack {
            Image(systemName: "shield.fill")
                .foregroundColor(entry.status.color)
                .font(.largeTitle)

            Text(entry.status.summary)
                .font(.headline)

            HStack {
                Text("Critical: \(entry.status.critical)")
                    .foregroundColor(.red)
                Text("Warnings: \(entry.status.warnings)")
                    .foregroundColor(.yellow)
            }
            .font(.caption)
        }
        .padding()
    }
}

struct StatusProvider: TimelineProvider {
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> ()) {
        Task {
            let status = await DevAuditClient.getStatusSummary()
            let entry = StatusEntry(date: Date(), status: status)

            // Refresh every 30 minutes
            let nextUpdate = Calendar.current.date(byAdding: .minute, value: 30, to: Date())!
            let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))

            completion(timeline)
        }
    }
}
```

---

## Widget Status API

### Lightweight Status Endpoint

**Purpose:** Provide minimal data for widgets to poll frequently

**Endpoint:** `GET /api/status/quick`

**Response:**
```json
{
  "status": "warning",
  "color": "yellow",
  "summary": "3 warnings, 1 outdated",
  "risk_level": "medium",
  "counts": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 5
  },
  "last_scan": "2025-01-20T14:30:00Z",
  "next_scan": "2025-01-20T20:30:00Z",
  "auditors": {
    "os_updates": "warning",
    "antivirus": "ok",
    "firewall": "ok",
    "python": "warning",
    "node": "ok"
  }
}
```

**Cache:** Response cached for 60 seconds to avoid excessive computation

### Real-Time Updates (Server-Sent Events)

**Purpose:** Push updates to widgets without polling

**Endpoint:** `GET /api/status/stream`

**Response (SSE):**
```
event: status
data: {"status":"warning","critical":0,"warnings":3}

event: scan_start
data: {"timestamp":"2025-01-20T15:00:00Z"}

event: scan_complete
data: {"status":"ok","critical":0,"warnings":0}
```

**Implementation:**
```python
# devaudit/server/widget_api.py
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio

@app.get("/api/status/quick")
async def get_quick_status():
    # Cached for 60 seconds
    return {
        "status": calculate_overall_status(),
        "color": get_status_color(),
        "summary": get_summary_text(),
        # ... rest of fields
    }

@app.get("/api/status/stream")
async def status_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            status = calculate_overall_status()
            yield {
                "event": "status",
                "data": json.dumps(status)
            }

            await asyncio.sleep(60)  # Update every minute

    return EventSourceResponse(event_generator())
```

---

## Implementation Phases

### Phase 1: Desktop Widget (v0.4.0)

**Priority:** High (most requested, easiest to implement)

**Tasks:**
1. ✅ Design icon set (green/yellow/red shields)
2. ✅ Implement `/api/status/quick` endpoint
3. ✅ Create `devaudit widget` CLI command
4. ✅ Implement Windows system tray (pystray)
5. ✅ Implement macOS menu bar (rumps)
6. ✅ Implement Linux system tray (pystray)
7. ✅ Add auto-start configuration
8. ✅ Test on Windows 10/11, macOS 13+, Ubuntu 22.04
9. ✅ Document widget usage

**Estimated Effort:** 2-3 weeks

### Phase 2: Mobile Widgets (v0.5.0)

**Priority:** Medium (requires mobile app foundation)

**Tasks:**
1. ✅ Choose mobile framework (Flutter recommended for cross-platform)
2. ✅ Create mobile app skeleton
3. ✅ Implement Android widget (small/medium/large)
4. ✅ Implement iOS widget (small/medium/large)
5. ✅ Background update workers
6. ✅ Test on Android 12+, iOS 15+
7. ✅ Publish to Play Store / App Store (optional)

**Estimated Effort:** 4-6 weeks

### Phase 3: Advanced Features (v0.6.0+)

**Optional Enhancements:**
- Interactive widgets (quick actions without opening app)
- Customizable widget themes
- Multiple widget instances (different projects)
- Lock screen widgets (Android 13+, iOS 16+)
- Apple Watch complication
- Wear OS tile

---

## Technical Decisions

### Desktop Widget: pystray vs. PyQt6

| Feature | pystray | PyQt6 |
|---------|---------|-------|
| **Size** | ~500 KB | ~50 MB |
| **Complexity** | Simple API | Full GUI framework |
| **Features** | Basic tray only | Full GUI capabilities |
| **Cross-platform** | ✅ Excellent | ✅ Excellent |
| **Dependencies** | Minimal | Many |
| **Recommendation** | ✅ **Use this** | For future full GUI |

**Decision: Use `pystray` for v0.4.0**
- Lightweight, fits DevAudit's minimalist approach
- Sufficient for system tray icon + menu
- Can migrate to PyQt6 later if full GUI needed

### Mobile: Native vs. Flutter vs. React Native

| Feature | Native (Kotlin/Swift) | Flutter | React Native |
|---------|------------------------|---------|--------------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Code Reuse** | ❌ None | ✅ 80-90% | ✅ 70-80% |
| **Widget Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Dev Speed** | Slow (2 codebases) | Fast (1 codebase) | Medium |
| **Size** | Small | Medium | Larger |
| **Recommendation** | Overkill | ✅ **Use this** | Not ideal for widgets |

**Decision: Use Flutter for v0.5.0**
- Cross-platform (iOS + Android from one codebase)
- Excellent widget support (WidgetKit bridge, Android Widgets)
- Dart is easy to learn
- Smaller binary than React Native
- DevAudit Python backend can be reused

---

## Security Considerations

### Widget Security

**Threats:**
- Widget displaying sensitive data in screenshots
- Unauthorized access to widget API
- Man-in-the-middle attacks on status updates

**Mitigations:**
1. **No Sensitive Data in Widgets**: Show counts, not details
   - ✅ "3 critical issues"
   - ❌ "CVE-2023-12345 in package X"

2. **Local API Only**: Widget API only on localhost
   - Bind to 127.0.0.1 (not 0.0.0.0)
   - Reject requests from non-localhost

3. **Authentication Token**: Simple token for widget API
   ```python
   WIDGET_TOKEN = secrets.token_urlsafe(32)
   # Store in ~/.devaudit/widget_token
   # Widget reads token and includes in requests
   ```

4. **HTTPS for Remote**: If future cloud tier
   - Use TLS for remote connections
   - Encrypt status data in transit

### Privacy

**Data Displayed in Widgets:**
- ✅ Risk level (critical/high/medium/low)
- ✅ Issue counts (numbers only)
- ✅ Status summary ("3 warnings")
- ❌ Package names
- ❌ CVE IDs
- ❌ File paths
- ❌ System details

**Rationale:** Widgets can appear in screenshots, screen recordings, over-shoulder views

---

## User Experience

### First-Time Setup

**Desktop:**
```bash
# Install DevAudit
pip install devaudit[server]

# Enable widget (auto-starts)
devaudit widget --enable

# Widget appears in system tray
```

**Mobile:**
1. Install DevAudit app from store
2. Open app, complete initial scan
3. Go to home screen → Add widget
4. Select DevAudit widget
5. Choose size (small/medium/large)

### Daily Usage

**Desktop:**
- Glance at system tray icon
- Green = all good, continue working
- Yellow/Red = click to open dashboard

**Mobile:**
- Glance at home screen widget
- Tap widget to open app
- View detailed findings

### Notifications

**When to Notify:**
- ⚠️ New critical vulnerability detected
- ⚠️ Firewall or antivirus disabled
- ℹ️ Scan completed (optional, user setting)

**When NOT to Notify:**
- ❌ Every warning (too noisy)
- ❌ Low-priority findings
- ❌ Scheduled scans starting

---

## Performance Requirements

### Desktop Widget

**Resource Usage:**
- **CPU**: <1% idle, <5% during status update
- **RAM**: <20 MB
- **Disk**: <2 MB (icon assets)
- **Network**: <1 KB per status update

**Update Frequency:**
- Status check: Every 5 minutes (configurable)
- Background scan: Every 6 hours (configurable)
- On-demand: Instant (user clicks "Scan Now")

### Mobile Widget

**Resource Usage:**
- **CPU**: <0.1% (updated by OS, not continuous)
- **RAM**: <10 MB
- **Battery**: <1% per day
- **Network**: <5 KB per update

**Update Frequency:**
- Android: Every 30 minutes (WorkManager)
- iOS: Timeline-based, OS-controlled (typically 15-60 minutes)
- On-demand: User can force refresh

---

## Future Enhancements

### v0.6.0+

**Interactive Widgets:**
- Quick actions (e.g., "Update Now" button in widget)
- Swipe actions (dismiss warning, snooze alert)

**Customization:**
- Multiple widget instances (home, work, project-specific)
- Custom icon themes (light/dark, color schemes)
- Widget size preferences

**Integrations:**
- Apple Watch complication (mini status indicator)
- Wear OS tile (Android smartwatch)
- Browser extension (DevAudit mini-status in toolbar)

---

## Questions for User

Before implementing, clarify:

1. **Auto-Start**: Enable by default, or ask user during install?
2. **Update Frequency**: 5 minutes default, or longer (less resource usage)?
3. **Notifications**: Enabled by default, or opt-in?
4. **Mobile Priority**: Android first, iOS first, or simultaneous?
5. **Widget Data**: Any specific metrics to prioritize in widgets?

---

## Success Metrics

**Adoption:**
- % of users who enable widget
- % of users who keep widget enabled after 1 week

**Engagement:**
- Number of widget clicks per week
- Time from critical alert to resolution

**Performance:**
- Widget resource usage (CPU/RAM)
- Widget update latency (time from scan to widget update)

**Satisfaction:**
- User feedback on widget usefulness
- Feature requests for widget improvements

---

**Status:** Design Complete, Ready for Implementation
**Next Steps:**
1. Review and approve design
2. Implement Phase 1 (Desktop Widget v0.4.0)
3. User testing and feedback
4. Implement Phase 2 (Mobile Widget v0.5.0)

**Maintainer:** DevAudit Team
**Last Updated:** 2025-01-20
