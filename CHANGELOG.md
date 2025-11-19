# Changelog

All notable changes to DevAudit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned (v0.3.0 - System-Wide Scanning)
- 7 additional system auditors (OS Updates, Antivirus, Drivers, Disk Health, Backup, Encryption, Firewall)
- Comprehensive risk scoring system

### In Progress
- ✅ BIOS/UEFI auditor - Implemented and integrated
- ✅ Dashboard integration for system security - Live with SystemSecurityCard component

### Planned (v0.4.0+)
- Cloud-based scanning (Ephemeral and Encrypted tiers)
- Project-specific scans with directory targeting
- Scan scheduling (auto-run daily/weekly)
- Desktop notifications when scan completes

---

## [0.3.0-foundation.2] - 2025-11-18

### Added
- **BIOS Auditor Integration** - First system auditor is now LIVE! 🎉
  - Integrated `BIOSAuditor` into `RealtimeScanner`
  - Scans run automatically with every scan
  - Detects BIOS version, vendor, age, and motherboard model
  - Risk assessment: CRITICAL (>3 years), HIGH (2-3 years), MEDIUM (1-2 years), LOW (<1 year)
  - Works on Windows (wmic), macOS (system_profiler), Linux (dmidecode + sysfs fallback)

- **SystemSecurityCard Component** - New dashboard card for system security
  - Color-coded risk levels (red/orange/yellow/green/gray)
  - Click any auditor to see detailed information
  - Educational modal with full content from `bios-uefi.md`
  - Shows BIOS vendor, version, release date, age
  - Displays risk-based recommendations
  - "Beta Preview" badge to indicate early feature
  - "Coming soon" hint for remaining 7 system auditors

- **Educational Content Display** - Complete educational flow
  - Modal shows "What is it?", "Why it matters", "When to update", "When to skip"
  - Link to full documentation guide
  - Contextual help for every finding
  - Empowers users to make informed decisions

### Technical
- Enhanced: `devaudit/server/scanner.py`
  - Added `from ..auditors.system_auditors import BIOSAuditor`
  - Added `BIOSAuditor()` to auditors list
  - Scanner now runs 6 auditors (5 package + 1 system)
- Created: `dashboard/src/components/SystemSecurityCard.tsx` (240 lines)
  - TypeScript component with full type safety
  - Responsive design (mobile-friendly)
  - Dark mode support
  - Accessibility features (ARIA labels, keyboard navigation)
- Enhanced: `dashboard/src/app/page.tsx`
  - Imported and rendered `SystemSecurityCard`
  - Positioned after VulnerabilityCard, before ScanHistory
- Bundle size: 18.8 kB (+1.2 kB from v0.3.0-foundation.1)
  - Increase due to new SystemSecurityCard component
  - Educational content loaded from backend (not in bundle)

### How to See It
```bash
# Start DevAudit dashboard
devaudit serve

# Visit: http://localhost:8888
# Click "Run Scan"
# Scroll down to see "System Security" card with BIOS info
# Click the BIOS card to see full educational content
```

---

## [0.3.0-foundation.1] - 2025-01-18

### Added
- **Enhanced Security Scan Card** - Now shows what was scanned when "All Clear"
  - Displays scanned items (Python: X packages, Docker: Y containers, etc.)
  - Better use of card space with 2-column layout
  - "Coming soon" hint for system-wide scanning features
  - Provides transparency about what DevAudit checked

- **Antivirus Warning Section** - Added to README.md
  - Explains why antivirus may flag DevAudit (normal behavior)
  - Step-by-step instructions for allowing DevAudit
  - Privacy reassurance (100% local, no external servers)
  - Links to Privacy Policy and Terms of Service

- **NEXT_STEPS.md** - Comprehensive development roadmap
  - Complete v0.3.0 implementation plan (7 remaining auditors)
  - Phase-by-phase breakdown (Core Security → System Health → Advanced)
  - Code templates for each auditor type
  - v0.4.0 through v1.0.0 feature roadmap
  - Technical debt and improvement checklist
  - Success metrics and contribution guide

### Fixed
- **Cleanup Items Count** - Fixed double-counting bug
  - Was counting both `cleanup_candidates` and `outdated_packages` separately
  - Now correctly sums the `count` field from cleanup_candidates
  - Python with 2 outdated packages now shows "2" instead of "3"
  - Fallback logic for tools without cleanup_candidates structure

### Changed
- **Default Port: 8080 → 8888** - Avoid Prometheus conflicts
  - Updated `devaudit serve` default from 8080 to 8888
  - Updated all documentation (README, RASPBERRY_PI, USE_CASES)
  - Reduces port conflicts with common monitoring tools
  - Users can still override: `devaudit serve --port XXXX`

### Technical
- Enhanced: `dashboard/src/components/VulnerabilityCard.tsx`
  - Added "What we scanned" section showing scanned tools and counts
  - Grid layout (All Clear status + Scanned items summary)
  - TypeScript-safe scannedItems type annotation
- Enhanced: `dashboard/src/components/Overview.tsx`
  - Fixed `countCleanupCandidates()` to use candidate.count field
  - Prevents double-counting of outdated packages
- Enhanced: `devaudit/cli.py`
  - Changed default port from 8080 to 8888
- Bundle size: 17.6 kB (+0.4 kB from v0.3.0-foundation)

---

## [0.3.0-foundation] - 2025-01-18

### Added - Educational Content System
- **Educational Content Loader** - Dynamic content loading system
  - `devaudit/educational/content_loader.py` - Markdown file parser with caching
  - `devaudit/educational/__init__.py` - Package initialization with `get_educational_content()` API
  - Auto-detects and loads content from `docs/concepts/*.md`
  - Provides fallback content when markdown files unavailable
  - Caches parsed content for performance

- **Educational Content Library** - 14,700+ words of educational documentation
  - **docs/concepts/cves.md** - Understanding Security Vulnerabilities (3,000 words)
    - What CVEs are and why they matter
    - Real-world examples (Log4Shell, Heartbleed)
    - Severity levels explained (CRITICAL → LOW)
    - Step-by-step remediation workflow
    - When to skip updates and when never to skip
    - False positives handling

  - **docs/concepts/dependencies.md** - Understanding Package Dependencies (3,500 words)
    - Dependency trees and transitive dependencies
    - Supply chain attacks (event-stream, ua-parser-js)
    - Attack surface mathematics
    - Dependency risks and mitigation
    - Best practices (minimize, pin, audit, automate)
    - Version specifiers (Python PEP 440, Node.js semver)

  - **docs/concepts/docker-cleanup.md** - Docker Cleanup Guide (3,700 words)
    - Why Docker accumulates waste
    - Understanding Docker storage (containers, images, volumes, networks)
    - Safe vs risky cleanup commands
    - Step-by-step cleanup workflow
    - Automation and scheduling
    - Troubleshooting common issues

  - **docs/concepts/bios-uefi.md** - Understanding BIOS/UEFI (4,500 words)
    - What BIOS/UEFI is (simple explanation for non-technical users)
    - Real-world vulnerabilities (LoJax, ThinkPwn)
    - When to update vs when to skip
    - Platform-specific update instructions (Windows, macOS, Linux)
    - BIOS recovery procedures
    - Safety checklist and best practices

### Added - First System Auditor (BIOS)
- **BIOS/UEFI Auditor** - `devaudit/auditors/system_auditors/bios_audit.py`
  - Cross-platform BIOS detection (Windows, macOS, Linux)
  - Extracts vendor, version, release date, motherboard model
  - Calculates BIOS age and assesses risk (CRITICAL >3 years, HIGH 2-3 years, MEDIUM 1-2 years, LOW <1 year)
  - Provides educational content from bios-uefi.md
  - Works without admin privileges (graceful degradation)
  - Platform-specific implementations:
    - Windows: wmic bios/baseboard queries
    - macOS: system_profiler SPHardwareDataType
    - Linux: dmidecode + /sys/class/dmi/id fallback

### Enhanced - Base Auditor Infrastructure
- **Enhanced BaseAuditor class** - `devaudit/auditors/base.py`
  - Added `RiskLevel` enum (NONE, LOW, MEDIUM, HIGH, CRITICAL)
  - Added `AuditorCategory` enum (PACKAGE, SYSTEM)
  - Added `get_educational_content()` method (returns structured educational content)
  - Added `assess_risk()` method (evaluates findings and returns RiskLevel)
  - Added `can_run()` method (checks platform compatibility and permissions)
  - Added `requires_elevation()` method (declares if admin/root needed)
  - Added `has_elevation()` method (detects current privilege level)
  - Added `get_platform_name()` method (friendly platform names)
  - All auditors now support educational content out of the box

### Enhanced - Existing Package Auditors
- **Python Auditor** - Added educational content from dependencies.md
- **Node.js Auditor** - Added educational content from dependencies.md
- **Docker Auditor** - Added educational content from docker-cleanup.md
- **Go Auditor** - Added educational content from dependencies.md
- **System Auditor** - Added custom educational content for development tools

All auditors now return educational content in audit results:
```json
{
  "educational_content": {
    "what_is_it": "Brief explanation",
    "why_it_matters": "Real-world impact",
    "when_to_update": "Urgency guidance",
    "when_to_skip": "Safe-to-ignore scenarios",
    "how_to_fix": "Step-by-step instructions",
    "risks": "Risks of taking action",
    "learn_more_url": "Link to full docs"
  }
}
```

### Technical Architecture
- Created `devaudit/educational/` package for educational content system
- Created `devaudit/auditors/system_auditors/` package for system-level auditors
- Updated `devaudit/auditors/system_auditors/__init__.py` to export BIOSAuditor
- Educational content structure supports i18n for future translations
- Content loader caches parsed markdown for performance
- All educational content follows standardized 7-field structure

### Documentation
- **docs/concepts/** - 4 comprehensive educational guides (14,700+ words)
- **devaudit/educational/README.md** - Educational system documentation
  - Usage guide for auditors
  - Content writing guidelines
  - Testing instructions
  - Future enhancements roadmap
- **devaudit/auditors/system_auditors/README.md** - System auditor implementation guide
  - Architecture patterns
  - Risk assessment guidelines
  - Testing requirements
  - Implementation priorities

### Foundation for v0.3.0
This release lays the complete foundation for v0.3.0's system-wide scanning:
- ✅ Educational content system (infrastructure complete)
- ✅ Enhanced BaseAuditor with risk assessment (ready for all auditors)
- ✅ First system auditor implemented (BIOS) as template
- ✅ All existing auditors integrated with educational content
- ⏳ Remaining system auditors (OS, Antivirus, Drivers, Disk, Backup, Encryption, Firewall)
- ⏳ Dashboard integration for system security monitoring

**Next:** Implement remaining 7 system auditors following BIOSAuditor pattern

---

## [0.2.4] - 2025-01-18

### Added
- **Comprehensive Documentation** - Complete documentation overhaul with 15,000+ words
  - **VISION.md** - Core philosophy, mission, and principles (Privacy, Education, Empowerment)
  - **USE_CASES.md** - 8 detailed deployment scenarios with code examples
  - **RASPBERRY_PI.md** - Complete step-by-step Raspberry Pi setup guide (4,000+ words)
  - **ROADMAP.md** - Detailed feature roadmap from v0.3 through v1.0+ (5,000+ words)
  - **docs/README.md** - Documentation index and navigation structure

- **Tools Detected Modal** - Click "Tools Detected" to see all discovered tools
  - Shows all tools with installation status
  - Displays versions and locations
  - Green highlight for installed tools
  - Solves "Where are the 5 tools?" confusion

- **Footer Documentation Links** - Quick access to key resources
  - Vision - Philosophy and mission
  - Use Cases - Deployment scenarios
  - Roadmap - What's coming next
  - Docs - Educational library
  - All links open in new tab, point to GitHub

### Fixed
- **Run Scan Button Width** - Added min-width to prevent layout shift when toggling between "Run Scan" and "Scanning..."
- **Cleanup Items Count** - Now correctly counts ALL categories (outdated packages + vulnerabilities + Docker cleanup)
  - Previously only counted Docker cleanup candidates
  - Now shows accurate total across all cleanup types
- **Tools Detected Clarity** - Made card clickable to reveal which tools were detected
  - Previously showed "5 tools detected" with no way to see details
  - Now displays System auditor alongside Python, Node.js, Docker, Go

### Changed
- **README.md** - Complete rewrite as "Your Personal Security Assistant"
  - New tagline emphasizing education and empowerment
  - Reorganized sections for clarity
  - Added links to all new documentation
  - Enhanced use case descriptions
  - Added privacy commitment section
  - Updated roadmap table

- **Mission Evolution** - Documented transition from developer tool to personal security assistant
  - Beyond packages: BIOS, drivers, OS updates, disk health, backups
  - Education-first approach with "What is X?" explanations
  - Privacy-by-default with local-first architecture
  - Raspberry Pi home lab vision

### Technical
- Enhanced: `dashboard/src/components/Overview.tsx`
  - Fixed `countCleanupCandidates()` to sum all categories
  - Added "Tools Detected" modal with detailed tool information
  - Made "Tools Detected" card clickable
- Enhanced: `dashboard/src/app/page.tsx`
  - Added min-width to "Run Scan" button (140px)
  - Updated footer with documentation links
  - All links use `target="_blank"` and `rel="noopener noreferrer"`
- Bundle size: 17.2 kB (+0.5 kB from v0.2.3)
- Created: 5 new documentation files (15,000+ words)

---

## [0.2.3] - 2025-01-18

### Added
- **Keyboard Shortcuts System** - Navigate faster with keyboard shortcuts
  - Custom React hook: `useKeyboardShortcuts` for global shortcuts
  - Platform-aware modifier keys (⌘ for Mac, Ctrl for Windows)
  - Input detection prevents shortcuts when typing in text fields
  - Escape key always works (close modals, cancel editing)

- **Navigation Shortcuts**
  - `/` or `Ctrl+K` (`⌘K` on Mac) - Focus search in scan history
  - `Esc` - Clear search / Close modals / Cancel editing

- **Export Shortcuts**
  - `Ctrl+E` (`⌘E` on Mac) - Export scan history as JSON
  - `Ctrl+Shift+E` (`⌘⇧E` on Mac) - Export scan history as CSV
  - Visual keyboard hint badges on export buttons

- **Help System**
  - `Shift+?` - Show keyboard shortcuts help modal
  - Categorized shortcuts display (Navigation, Actions, Notes)
  - Icons for each shortcut with descriptions
  - "Shortcuts" link in footer for discoverability

### Changed
- **Search Input** - Now has ref for keyboard focus management
- **Export Buttons** - Display keyboard shortcut hints (⌘E, ⌘⇧E)
- **User Experience** - Faster navigation with keyboard-first workflow

### Technical
- New file: `dashboard/src/lib/useKeyboardShortcuts.ts` - Keyboard shortcut hook
- New component: `dashboard/src/components/KeyboardShortcutsHelp.tsx` - Help modal
- Enhanced: `ScanHistory.tsx` - Integrated keyboard shortcuts
- Enhanced: `page.tsx` - Global shortcuts and help modal
- Bundle size: 16.7 kB (+1.1 kB from v0.2.2)

---

## [0.2.2] - 2025-01-18

### Added
- **Export Scan History** - Download scan history as JSON or CSV
  - JSON export with full scan data
  - CSV export with summary statistics
  - Timestamped filenames for organization
  - Export buttons in scan history header

- **Search & Filter** - Search through scan history
  - Real-time search across dates, IDs, metrics, and notes
  - Filter by packages, vulnerabilities, outdated count
  - Shows "Found X of Y scans" counter
  - Clear button (X) to reset search

- **Scan Notes & Tags** - Annotate scans with custom notes
  - Add notes to any scan ("before upgrade", "production audit", etc.)
  - Inline editing with keyboard shortcuts (Enter to save, Esc to cancel)
  - Notes display with tag icon
  - Search includes notes content
  - Backend storage in scan metadata
  - API endpoint: `PATCH /api/history/{scan_id}/notes`

- **Skeleton Loading States** - Professional loading animations
  - Skeleton placeholders for scan history
  - Skeleton placeholders for comparison view
  - Matches actual content layout
  - Smooth fade-in when data loads

### Changed
- **Search Functionality** - Now includes notes in search results
- **Scan Count Display** - Shows total number of scans in header
- **Export Buttons** - Conditionally shown only when scans exist
- **Loading Experience** - Replaced spinners with skeleton screens

### Technical
- New backend method: `ScanHistory.update_scan_notes()`
- Updated scan interface to include `metadata.notes` field
- Enhanced search algorithm to include notes
- Export functions use Blob API for downloads
- Skeleton components use Tailwind animate-pulse

---

## [0.2.1] - 2025-01-18

### Added
- **Scan History System** - Track all scans over time
  - Local file-based storage in `~/.devaudit/history/`
  - Automatic save after each scan
  - Timeline view showing chronological scan history
  - Keeps last 50 scans, auto-prunes older entries
  - Summary statistics for each scan (packages, vulnerabilities, outdated, tools)
  - Delete individual scan records
  - "Current" badge highlighting the latest scan

- **Scan Comparison Engine** - Compare any two historical scans
  - Side-by-side comparison modal with timeline
  - Overall trend indicator (Improved/Degraded/No Change)
  - Detailed change tracking:
    - Fixed vulnerabilities (green/positive)
    - New vulnerabilities (red/negative)
    - Updated packages (green/positive)
    - Newly outdated packages (yellow/warning)
    - Added/removed packages (neutral)
  - Summary statistics showing improvements vs. regressions
  - Smart diff algorithm tracking packages by name and CVE ID

- **Cleanup Items Breakdown** - Detailed explainer for cleanup items
  - Info icon tooltip explaining what counts as cleanup items
  - Clickable card opening detailed modal
  - Categorized breakdown:
    - Outdated packages (yellow) with version comparison
    - Security vulnerabilities (red) with CVE details
    - Docker cleanup candidates (orange) - containers, images
  - Shows up to 10 items per category with "+N more" indicator
  - "All Clear" empty state when no cleanup needed

- **Enhanced Color Palette** - Electric blue accents for tech/action elements
  - Electric blue (#3b82f6) for action buttons and interactive elements
  - Run Scan button: emerald green → electric blue
  - WebSocket connection status: electric blue indicator
  - Scan progress bar: electric blue
  - Footer links hover: electric blue
  - Total Packages stat card: electric blue theme
  - Ready state icon: electric blue
  - Maintains emerald green for success states and healthy metrics

### Changed
- **Timeline UI** - Relative time formatting ("2h ago", "3d ago", "Just now")
- **Trend Indicators** - Visual trend arrows (improving ↓ / worsening ↑) between scans
- **Two-click Comparison** - Select two scans to compare with visual feedback
- **Scan History Integration** - Automatically tracks scan_id for current scan
- **Color Scheme Balance** - Emerald green (health) + Electric blue (action) + Yellow (warning) + Orange (cleanup) + Red (error)

### Technical
- New backend: `devaudit/server/history.py` - Scan history management
- New component: `dashboard/src/components/ScanHistory.tsx` - Timeline UI
- New component: `dashboard/src/components/ComparisonView.tsx` - Comparison modal
- History API endpoints: `/api/history`, `/api/history/{scan_id}`, `/api/history/compare/{id1}/{id2}`, `DELETE /api/history/{scan_id}`
- Scanner integration: Auto-save scans with metadata tracking
- Comparison algorithm: Smart package/vulnerability diffing by name and ID

---

## [0.2.0] - 2025-01-18

### Added

#### Interactive Features
- **Clickable Stat Cards** - Click "Total Packages" or "Outdated Packages" to see full details
  - Modal overlays with searchable, sortable tables
  - Filter and search functionality
  - Source attribution (Python, Node.js, etc.)
- **Interactive Package Upgrade** - One-click package management
  - Checkbox selection for individual packages
  - "Select All" / "Deselect All" batch operations
  - "Upgrade Selected" button with live count
  - Real-time progress indicators
  - Success/failure feedback with visual confirmation
  - Works for both Python and Node.js packages
- **Vulnerability Scanning Integration**
  - Python: pip-audit (primary) and safety (fallback)
  - Node.js: npm audit integration
  - Severity-based color coding (Critical→Low)
  - CVE links to National Vulnerability Database
  - Fix version recommendations
  - Severity summary dashboard
  - "All Clear" state when no vulnerabilities found

#### New Components
- **Modal.tsx** - Reusable modal system with keyboard shortcuts (ESC to close)
- **PackageTable.tsx** - Sortable, filterable table with search
  - Click column headers to sort
  - Real-time search filtering
  - Shows X of Y packages count
- **VulnerabilityCard.tsx** - Security vulnerability display
  - Grouped by severity with count badges
  - Detailed vulnerability items with descriptions
  - Links to CVE databases
  - Actionable fix recommendations
- **ActionablePackageList.tsx** - Interactive cleanup interface
  - Checkbox-based selection
  - Batch upgrade operations
  - Loading states and error handling

#### API Endpoints
- `POST /api/cleanup/python/upgrade` - Upgrade Python packages
- `POST /api/cleanup/node/upgrade` - Upgrade Node.js packages
- `POST /api/cleanup/docker/remove-containers` - Remove Docker containers
- `POST /api/cleanup/docker/remove-images` - Remove Docker images

#### Web Dashboard
- **Real-time Web Dashboard** - Beautiful, privacy-first web UI for environment monitoring
  - Dark mode by default with light mode toggle
  - WebSocket-powered live audit streaming
  - Progressive results display as each auditor completes
  - Clean, modern interface with interactive stat cards
  - Green/emerald brand color scheme
  - Fully responsive design with Tailwind CSS
- **Three Operating Modes** (Local mode active, cloud modes planned):
  - 🟢 **Local Mode (FREE)** - 100% private, runs on localhost, no data leaves machine
  - 🔵 **Ephemeral Cloud Mode (Planned)** - Remote access, WebSocket streaming, no data storage
  - 🟣 **Encrypted Cloud Mode (Planned)** - E2E encryption, historical data, user-controlled keys
- **Dashboard Components**:
  - Overview stats: Tools detected, total packages, outdated packages, cleanup items
  - Python details card with frameworks, outdated packages, and project info
  - Node.js details card with global packages, frameworks, and dependencies
  - Docker details card with container/image stats, cleanup candidates, and large images
  - Real-time connection status indicator with scan progress bar
  - Theme toggle for light/dark mode switching

#### JSON Output
- **JSON Reporter** - Machine-readable JSON output format
- New `--format` CLI option with choices: `text`, `json`, or `both`
- JSON output includes:
  - Metadata (timestamp, version, platform)
  - Complete audit results for all tools
  - Summary statistics (total packages, outdated count, cleanup candidates)
- Perfect for programmatic integration and automation

#### Server Infrastructure
- **FastAPI Server** - Local server for dashboard hosting
- **WebSocket Support** - Real-time bidirectional communication
- **Static Export Pattern** - Dashboard built as static Next.js export, served by FastAPI
- New `devaudit serve` command with options:
  - `--host` - Custom host binding (default: `127.0.0.1`)
  - `--port` - Custom port (default: `8080`)
- CORS configured for localhost only (security-first)
- Health check endpoint at `/api/health`
- Scan trigger endpoint at `/api/scan`

### Changed

- **CLI Enhancement** - Added `--format` option to `devaudit scan` command
- **Package Structure** - Added optional `[server]` extras for dashboard dependencies
- **Installation Options**:
  - Standard: `pip install devaudit` (CLI only)
  - With Dashboard: `pip install devaudit[server]` (includes FastAPI, uvicorn, websockets)

### Technical Details

#### New Dependencies (optional - server extras)
- FastAPI >= 0.104.0 - Modern web framework for Python
- uvicorn >= 0.24.0 - ASGI server for FastAPI
- websockets >= 12.0 - WebSocket protocol implementation

#### New Files
- `devaudit/reporters/json_reporter.py` - JSON output formatter
- `devaudit/server/app.py` - FastAPI application and routes
- `devaudit/server/scanner.py` - Real-time scanner with WebSocket broadcasting
- `dashboard/` - Complete Next.js 14 dashboard application
  - TypeScript + React frontend
  - Tailwind CSS styling with custom dark theme
  - Lucide React icons
  - WebSocket hooks for real-time updates
  - Theme management with localStorage persistence

#### Design System
- Created comprehensive design system documentation (DESIGN_SYSTEM_MASTER.md)
- Established DevAudit brand identity:
  - Primary color: Green/Emerald (#10b981)
  - Dark mode as default
  - Glass morphism effects
  - Consistent spacing and typography
- Cross-app design consistency with ProveChain and SignaSeal

### Privacy & Security

- **100% Local by Default** - All data stays on your machine
- **No Telemetry** - Zero usage data collection
- **Localhost-Only Server** - Dashboard binds to 127.0.0.1 by default
- **No External Dependencies** - All processing happens locally
- **Future-Proofed** - E2E encryption architecture planned for cloud modes

### Documentation

- Updated README.md with comprehensive dashboard documentation
- Added dashboard installation instructions
- Added `devaudit serve` command documentation
- Added JSON output examples
- Added new use cases (dashboard monitoring, programmatic integration)
- Updated privacy section with multi-mode details
- Added requirements section for dashboard dependencies

### Developer Experience

- Dashboard served as static files (no Node.js runtime needed in production)
- Virtual environment (.venv) recommended for development
- Clean separation of concerns (CLI, server, dashboard)
- Type-safe TypeScript frontend
- Comprehensive error handling and logging

---

## [0.1.0] - 2025-01-15

### Added

- Initial release of DevAudit
- **Python Auditing** - List packages, detect frameworks, find outdated packages
- **Node.js/npm Auditing** - Track global packages, detect frameworks, identify outdated
- **Docker Auditing** - List containers, images, identify large images, find dangling resources
- **Go Auditing** - List modules, show cache location
- **System Auditing** - Detect Git, kubectl, Terraform, cloud CLIs
- **Project-Specific Scanning** - Target individual projects with `--target` flag
- **Beautiful Reports** - Console output with Rich tables + timestamped text reports
- **Cleanup Suggestions** - Automatically identify outdated packages and large Docker images
- **Docker Desktop Fix** - Fix common Docker Desktop UI issues (Windows)
- **Cross-Platform** - Support for Windows, macOS, and Linux
- Published to PyPI as `devaudit`

---

## Release URLs

- [0.2.0](https://github.com/aramantos/devaudit/releases/tag/v0.2.0)
- [0.1.0](https://github.com/aramantos/devaudit/releases/tag/v0.1.0)
