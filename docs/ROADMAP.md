# DevAudit Roadmap

This roadmap tracks DevAudit's evolution from a developer environment auditor into a personal security assistant. All features align with our core principles: **Privacy, Education, and Empowerment**.

---

## Vision Evolution

### From: Developer-Focused Auditor
- Package dependency scanning (Python, Node.js, Docker, Go)
- Security vulnerability detection (CVEs)
- Docker cleanup optimization

### To: Personal Security Assistant
- **System-wide security monitoring** (BIOS, OS, drivers, antivirus, disk health, backups, encryption, firewall)
- **Hardware diagnostics** (reading the fault signals your hardware already emits, and teaching you how to isolate them)
- **Educational security platform** (teaching, not just alerting)
- **Privacy-first multi-device orchestration** (Raspberry Pi hub)
- **Honest risk assessment** (no fear tactics or inflated scores)

---

## Where Things Actually Stand

This section exists because an earlier version of this roadmap listed calendar dates and "Released" status for versions that were never published. Corrected here.

- **PyPI (`pip install devaudit`) has only v0.1.0**, published November 2025. It is the original CLI-only package/dependency auditor. No dashboard, no system auditors, no education library, no tags beyond it exist in this repo's history.
- **This source tree is at v0.3.x** and includes the dashboard, 14 auditors (6 package, 8 system), scan history/comparison/trends, the educational content library, and optional AI insights, all working, none of it released to PyPI yet.
- **v0.4.0 will be the first full release**: hardware diagnostics plus shipping everything above.
- **Everything after v0.4.0 is evidence-gated, not date-gated.** A stage ships when the one before it has proven useful in real, ongoing use, not on a calendar. The version numbers below are a sequence, not a schedule.

| Version | Theme | Status |
|---------|-------|--------|
| v0.1.0 | Developer Environment Auditing | ✅ Released (PyPI, Nov 2025) |
| v0.2.x – v0.3.x | Dashboard, System-Wide Scanning, Educational Library | ✅ Built, unreleased (this source tree) |
| **v0.4.0** | **Hardware Diagnostics + first full release** | 🚧 In development |
| v0.5+ | Remediation Engine, Multi-Device Support, Automation & Scheduling, Notifications & Alerts, Polish/i18n/Accessibility | 📋 Planned, evidence-gated |
| v1.0.0 | Cloud Tiers (Optional) | 📋 Planned, evidence-gated |
| Beyond v1.0 | Community plugins, network/IoT scanning, password manager audit, local-only ML | 💭 Ideas, not committed |

---

## Built, Unreleased: Dashboard & System-Wide Scanning

**Theme:** Beyond packages, audit the entire system

This is all real and working in the source tree today. It has not shipped to PyPI.

### System Auditors (8, all built)

#### 1. BIOS/UEFI Auditor
- Detects current BIOS version, checks for known updates, flags security patches
- Educational layer: what BIOS is, why (and when not) to update, per-manufacturer instructions

#### 2. Operating System Auditor
- Windows Update, macOS Software Update, Linux package manager status
- Pending security patches, deferred updates, end-of-life OS detection

#### 3. Antivirus/Security Software Auditor
- Windows Defender status, definition age, real-time protection status

#### 4. Driver Auditor
- Identifies outdated graphics/network/chipset drivers, flags critical security drivers

#### 5. Disk Health Auditor
- SMART status for HDDs/SSDs, warning signs (reallocated sectors, etc.), backup urgency

#### 6. Backup Auditor
- Detects backup software, last backup timestamp, destination, verification status

#### 7. Encryption Auditor
- BitLocker (Windows), FileVault (macOS), LUKS (Linux) status, TPM detection

#### 8. Firewall Auditor
- Windows/macOS firewall status, UFW/iptables (Linux), open port detection

Every auditor above returns a risk level (Low/Medium/High) plus educational content, never an inflated score.

### Dashboard (built)
- Scan history with a timeline view, side-by-side comparison, trend indicators
- One-click package upgrades, CVE severity ratings
- Real-time WebSocket updates during a scan
- Keyboard shortcuts, dark mode, export to JSON/CSV

### Educational Library (built)
- A `docs/concepts/` guide per topic (BIOS, CVEs, backups, disk health, encryption, firewall, driver updates, OS updates, docker cleanup, dependencies, antivirus): what it is, why it matters, how to fix it
- Inline "what is this?" panels in the dashboard for every finding

**Not yet built** (see v0.5+ below): beginner/intermediate/advanced content tiers, interactive walkthroughs, curated external resource links.

---

## v0.4.0: Hardware Diagnostics + First Full Release

**Theme:** Read the fault signals your hardware already emits, and teach fault isolation

This is the next thing being built. Two parts: the harvest-only diagnostics, and actually shipping a real PyPI release of everything above.

### Hardware Diagnostics (harvest-only auditors)

- **SMART / storage health** - the drive's own reliability counters (reallocated sectors, pending sectors, uncorrectable errors)
- **Windows hardware error log (WHEA)** - CPU, memory, and PCIe error events
- **Disk/controller I/O event log** - interface and transport-level errors (the signal a failing cable or enclosure produces, distinct from a failing drive)
- **RAM diagnostic results** - Windows Memory Diagnostic / memtest output, surfaced and explained
- **Device problem states** - Device Manager error codes and what they mean

**Education-first framing, not a verdict engine (yet).** Phase 1 harvests and explains: it shows you the raw signal and teaches you what it means. Example: rising interface/CRC errors alongside a flat reallocated-sector count points at the cable or enclosure, not the drive itself, and the auditor explains that distinction rather than just flagging "disk problem."

A **later phase** adds:
- A fault-isolation synthesis verdict that reasons across signals (not just reporting them individually)
- Periodic scheduled scans, so a slow-building fault gets caught before it becomes a failure

### First Full Release
- Fix packaging so `pip install devaudit` actually installs the current feature set
- CI for the test suite
- Tag the release, publish to PyPI
- Everything under "Built, Unreleased" above ships as part of this

---

## v0.5+: The Original Plan (evidence-gated, no dates)

These are the features from the earlier roadmap that haven't been built yet. They're still the plan. What's changed is how they ship: each one is built when the stage before it has proven useful in real use, not on a fixed monthly cadence.

### Educational Library Expansion
- Beginner/Intermediate/Advanced content depth per topic
- Interactive tutorials ("Your First Scan", "Understanding Your Risk Score", "Setting Up a Raspberry Pi Hub")
- Curated external resources (vendor docs, security advisories)
- In-dashboard "Learn More" expandable sections beyond the current inline panels

### Remediation Engine
**Theme:** From detection to action

- One-click remediations (apply Windows Updates, update packages, enable Defender/firewall)
- Guided remediations (BIOS update walkthrough per manufacturer, driver update wizard, encryption enablement)
- Remediation safety: pre-change checkpoint, rollback instructions, dry-run/test mode
- Batch operations ("Fix All Low-Risk Items")
- Remediation history: what was fixed, when, before/after comparison

### Multi-Device Support
**Theme:** One dashboard for every device you own

- **Hub:** central dashboard (Raspberry Pi or main computer)
- **Agents:** lightweight scanners on other devices, reporting to the hub over the local network only, no cloud
- Aggregate view across devices, per-device drill-down, weakest-link identification
- Explicit device enrollment (no stealth), visible status indicator on agents, easy unenrollment
- Pre-configured Raspberry Pi hub image with a setup wizard

### Automation & Scheduling
- Scheduled scans (daily/weekly/custom cron), smart scheduling (scan when idle)
- Automated remediation for low-risk fixes, approval required for medium/high-risk
- Continuous background health monitoring with trend analysis
- Periodic backup verification (test restores, staleness alerts)

### Notifications & Alerts
- Desktop notifications for scan completion, critical vulnerabilities, hardware failure predictions
- Optional email alerts (weekly health reports, critical summaries)
- Severity-based filtering and deduplication (no alert spam)

### Polish, Accessibility, and Internationalization
- Faster scans (caching, parallelization), reduced memory footprint
- Onboarding flow, contextual help
- Screen reader support, high contrast mode, keyboard-only navigation, WCAG 2.1 AA compliance
- Multi-language support for the dashboard and educational content
- Automated test suite, integration tests, third-party security audit

---

## v1.0.0: Cloud Tiers (Optional, evidence-gated)

**Theme:** Remote access without sacrificing privacy

### Local Mode (Free, Forever)
✅ Everything above
✅ Runs entirely on your machine(s)
✅ No cloud dependencies, no data leaves your network
✅ No subscription required

### Ephemeral Cloud Mode (Paid, Optional)
**Target price:** ~$5/month

- Access dashboard from anywhere, WebSocket streaming over HTTPS
- Zero data storage (ephemeral only), end-to-end encrypted tunnel
- We can't see your scans; cancel anytime, full local mode restored

**Perfect for:** remote workers checking a home network, travellers monitoring their devices.

### Encrypted Cloud Mode (Paid, Optional)
**Target price:** ~$10/month

- Everything in Ephemeral, plus historical scan storage (end-to-end encrypted)
- Cross-device sync, long-term trend analysis
- You hold the encryption keys; we can't decrypt your data; lose the key, lose the data (we can't recover it)

**Perfect for:** security-conscious individuals, multi-device power users.

### Enterprise Mode (Future, On Request)
- Team dashboards, compliance reporting (SOC 2, HIPAA, etc.), SSO, custom retention, dedicated support

---

## Beyond v1.0: Future Ideas (not committed)

- **Community plugins:** extensible architecture, custom auditors, a plugin marketplace
- **Network/IoT scanning:** router vulnerabilities, IoT device security, certificate expiration monitoring
- **Password manager integration:** 2FA audit (which accounts lack it?)
- **Privacy-respecting AI/ML:** local-only anomaly detection, predictive failure modelling, smarter remediation suggestions, no cloud AI required for this class of feature
- **Integration ecosystem:** home automation (Home Assistant), IT management tools, vendor APIs

---

## Not on Roadmap (Deliberately Excluded)

We will **NOT** build:

❌ **Surveillance features** - Stealth monitoring, keylogging, spying
❌ **Parental control software** - We're an assistant, not a warden
❌ **Malware removal** - We detect, we don't remove (use proper AV)
❌ **Firewall replacement** - We monitor firewalls, we aren't one
❌ **Intrusion detection** - Out of scope, use dedicated IDS
❌ **DRM or licensing enforcement** - We respect user freedom

**Why not?** These features either enable abuse (surveillance), require different expertise (malware removal), conflict with the mission (control vs. empowerment), or create liability we can't manage. We stay focused on education, detection, and empowerment.

---

## How We Prioritize

**We say yes if:**
1. It aligns with the core mission (Privacy, Education, Empowerment)
2. It's teachable (can we explain it simply?)
3. It's privacy-respecting (local-first possible?)
4. It solves a real pain point
5. We can maintain it long-term

**We say no if:**
1. It enables abuse or surveillance
2. It requires compromising privacy
3. It's feature creep, not core mission
4. It adds unsustainable complexity
5. It requires vendor lock-in

### Community Input

Want to influence the roadmap?
- 💬 GitHub Discussions: propose features
- 🐛 GitHub Issues: report pain points
- ⭐ Star features you care about

---

## Release Philosophy

### Versioning
- **Major (v1.0, v2.0):** big architectural changes
- **Minor (v0.4, v0.5):** new features, scanners, capabilities
- **Patch (v0.1.1, v0.1.2):** bug fixes, small improvements

### Release Cadence
Evidence-gated, not calendar-gated. A version ships when it's proven useful in real, ongoing use, not on a fixed schedule. The earlier version of this roadmap promised monthly releases through 2025; none of those dates were met, which is exactly why this section no longer carries dates.

### Backwards Compatibility
- **Local mode:** never break existing workflows
- **Data format:** forward-compatible scan history
- **Config:** migration tools provided when a format changes

---

## Get Involved

**Code:** implement new auditors, fix bugs, improve performance, write tests
**Documentation:** educational content, how-to guides, translations
**Design:** UI/UX improvements, dashboard components, educational diagrams
**Community:** answer questions, share use cases, spread the word
**Testing:** beta test new features, report bugs, cross-platform validation (this project is Windows-tested; macOS and Linux validation of the system auditors is still needed)

**See:** [CONTRIBUTING.md](CONTRIBUTING.md) for details

---

## Stay Updated

- ⭐ Star the repo: [github.com/Aramantos/devaudit](https://github.com/Aramantos/devaudit)
- 📰 Watch releases for updates
- 💬 Join discussions
- 🐛 Subscribe to issues you care about

**Questions about the roadmap?** Open a [GitHub Discussion](https://github.com/Aramantos/devaudit/discussions). We're transparent about priorities, and honest when a prior version of this document wasn't.

---

*This roadmap is a living document. It previously carried Jan-Sep 2025 target dates and marked v0.1.0/v0.2.x as "Released" when only v0.1.0 ever was. Corrected here.*

*Last updated: July 2026*
