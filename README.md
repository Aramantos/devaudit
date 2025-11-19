# 🔍 DevAudit

**Your Personal Security Assistant**

*Empowering people to understand and protect their digital life through education and transparency.*

[![PyPI version](https://badge.fury.io/py/devaudit.svg)](https://pypi.org/project/devaudit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What is DevAudit?

DevAudit is evolving from a developer-focused auditing tool into a **comprehensive personal security assistant** that helps you understand and protect your entire system.

**Beyond Packages** - We're expanding to audit your BIOS, drivers, OS patches, antivirus status, disk health, backups, and more.

**Education First** - We don't just tell you "something is wrong" - we explain what it is, why it matters, how to fix it, and when it's safe to ignore.

**Privacy By Default** - 100% local-first architecture. All data stays on YOUR machine. No telemetry, no cloud dependencies, no tracking.

**Read More:**
- 📖 [Vision & Philosophy](VISION.md) - Our mission and principles
- 🎯 [Use Cases](USE_CASES.md) - How people use DevAudit
- 🗺️ [Roadmap](ROADMAP.md) - What's coming next
- 🥧 [Raspberry Pi Guide](RASPBERRY_PI.md) - Turn a Pi into a security hub

---

## ✨ Current Features

### Package & Dependency Management
- 🐍 **Python** - Packages, frameworks (Django, Flask, FastAPI), vulnerabilities (CVEs), outdated packages
- 📦 **Node.js** - Global packages, frameworks (Express, React, Vue), npm audit integration
- 🐳 **Docker** - Containers, images, cleanup candidates, dangling resources
- 🔷 **Go** - Modules, dependencies, version tracking
- 💻 **System Tools** - Git, kubectl, Terraform, cloud CLIs

### Interactive Web Dashboard
- 🌐 **Real-Time Monitoring** - WebSocket-powered live updates
- 📊 **Scan History** - Automatic tracking with timeline view
- 🔄 **Scan Comparison** - Side-by-side diff of any two scans
- 🛡️ **Security Scanning** - CVE detection with severity ratings
- ⚡ **One-Click Upgrades** - Select and upgrade outdated packages
- 🎨 **Beautiful UI** - Dark mode, responsive design, electric blue + emerald green
- ⌨️ **Keyboard Shortcuts** - `/` to search, `Ctrl+E` to export, `?` for help
- 🔒 **100% Private** - Runs on localhost, zero cloud dependencies

### Educational Content
- 📚 **Inline Explanations** - "What is this?" for every finding
- 💡 **Risk Context** - "Why does this matter?" with real examples
- 🛠️ **Fix Guidance** - Step-by-step remediation instructions
- 📖 **Documentation Library** - Comprehensive guides and tutorials

---

## 🚀 Quick Start

### Installation

**CLI Only:**
```bash
pip install devaudit
```

**With Dashboard (Recommended):**
```bash
pip install devaudit[server]
```

### Three-Command Setup

```bash
# 1. Install
pip install devaudit[server]

# 2. Start dashboard
devaudit serve

# 3. Open browser
# Visit: http://localhost:8888
```

**That's it!** Click "Run Scan" and explore your results.

### ⚠️ Antivirus Software Notice

DevAudit scans your system to check for security issues, which may trigger antivirus software warnings. This is normal behavior.

**If your antivirus flags DevAudit:**
1. **Verify the source** - Ensure you installed DevAudit from PyPI (`pip install devaudit`)
2. **Allow the process** - Click "Allow" when your antivirus asks about DevAudit
3. **Add an exception** (optional) - For smoother operation, add DevAudit to your antivirus exclusion list

**Why this happens:** DevAudit runs system commands (checking BIOS versions, scanning packages, reading system files) that antivirus software may flag as suspicious activity. This is expected for security auditing tools.

**Your privacy:** DevAudit runs 100% locally on your machine. No data is ever sent to external servers. See our [Privacy Policy](PRIVACY.md) and [Terms of Service](TERMS.md) for details.

---

## 📖 Core Commands

### `devaudit scan`

Audit your development environment.

```bash
# Full system scan
devaudit scan

# Specific tools
devaudit scan --python
devaudit scan --docker --node

# Project-specific
devaudit scan --target ~/projects/my-app

# Export as JSON
devaudit scan --format json > audit.json
```

**Options:**
- `--python`, `--node`, `--docker`, `--go`, `--system` - Audit specific tools
- `--target PATH` - Audit a specific project directory
- `--format {text,json,both}` - Output format
- `--no-reports` - Skip report files
- `--output-dir PATH` - Custom report directory

### `devaudit serve`

Launch the web dashboard.

```bash
# Default (localhost:8888)
devaudit serve

# Custom port
devaudit serve --port 3000

# Network access (Raspberry Pi, etc.)
devaudit serve --host 0.0.0.0 --port 8888
```

### `devaudit fix-docker`

Fix Docker Desktop issues (Windows only).

```bash
devaudit fix-docker
```

---

## 🌐 Web Dashboard

**Privacy-First Monitoring**

The dashboard runs 100% locally - no data ever leaves your machine.

### Key Features

#### Overview & Insights
- **Tools Detected** - Click to see all installed development tools
- **Total Packages** - Searchable, sortable table of all dependencies
- **Outdated Packages** - One-click upgrade with checkbox selection
- **Cleanup Items** - Detailed breakdown (outdated packages, vulnerabilities, Docker cleanup)
- **Security Scan** - CVE detection with severity levels and fix recommendations

#### History & Comparison
- **Automatic Tracking** - Every scan saved to `~/.devaudit/history/`
- **Timeline View** - See scans over time with relative timestamps
- **Trend Indicators** - Visual arrows showing security posture (improving ↓ or degrading ↑)
- **Side-by-Side Comparison** - Compare any two scans to see exact changes
- **Scan Notes** - Annotate scans ("before upgrade", "production baseline")

#### Productivity
- **Export Scan History** - Download as JSON or CSV
- **Search & Filter** - Real-time search across all scans
- **Keyboard Shortcuts** - Navigate faster with keyboard
  - `/` or `Ctrl+K` - Focus search
  - `Ctrl+E` - Export JSON
  - `Ctrl+Shift+E` - Export CSV
  - `?` - Show all shortcuts

#### User Experience
- **Dark Mode** - Default dark theme with toggle
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Skeleton Loading** - Professional loading states
- **Educational Tooltips** - Learn about every metric

### Dashboard Modes

**🟢 Local Mode (FREE - Current)**
- Runs on localhost (127.0.0.1)
- 100% private - data never leaves your machine
- No internet required
- Free forever

**🔵 Ephemeral Cloud Mode (Planned)**
- Remote access from anywhere
- Real-time streaming only (no storage)
- End-to-end encrypted tunnel
- ~$5/month

**🟣 Encrypted Cloud Mode (Planned)**
- Historical scan storage (E2E encrypted)
- You hold the encryption keys
- Cross-device sync
- ~$10/month

---

## 🎯 Use Cases

### 1. Personal Laptop Security
Keep your system secure without hiring an IT consultant.

```bash
pip install devaudit[server]
devaudit serve
# Click "Run Scan" → See security issues → Fix them
```

**Perfect for:** Non-technical users, privacy advocates, security-conscious individuals

### 2. Developer Environment Monitoring
Track vulnerabilities and outdated dependencies across projects.

```bash
# Audit your project
cd ~/projects/my-app
devaudit scan --format json

# Integrate with CI/CD
devaudit scan --format json | jq '.summary.vulnerabilities'
```

**Perfect for:** Full-stack developers, DevOps engineers, open source maintainers

### 3. Home Lab Multi-Device Management
Monitor all your computers from one dashboard (future feature).

```bash
# Install on Raspberry Pi
pip3 install devaudit[server]
devaudit serve --host 0.0.0.0

# Access from any device: http://raspberrypi.local:8888
```

**Perfect for:** Tech enthusiasts, home lab operators, multi-device users

### 4. Raspberry Pi Security Hub
Turn a $50 Raspberry Pi into an always-on security monitoring hub.

**See:** [Complete Raspberry Pi Setup Guide](RASPBERRY_PI.md)

**Perfect for:** DIY enthusiasts, privacy-focused families, learning projects

### 5. Family Computer Maintenance
Proactively maintain family devices (with consent).

**Perfect for:** Tech-savvy family members, adult children helping parents

⚠️ **Important:** DevAudit will NEVER build surveillance features. All monitoring requires explicit consent and transparency.

**More use cases:** See [USE_CASES.md](USE_CASES.md)

---

## 🛠️ What Gets Audited

### Current (v0.2.x)

**Development Tools:**
- Python packages, frameworks, vulnerabilities
- Node.js packages, frameworks, npm audit
- Docker containers, images, cleanup candidates
- Go modules and dependencies
- System tools (Git, kubectl, cloud CLIs)

**Dashboard Features:**
- Package dependency tracking
- Security vulnerability scanning (CVEs)
- Outdated package detection
- Scan history and comparison
- Interactive upgrades

### Coming Soon (v0.3.0+)

**System-Wide Scanning:**
- 🖥️ **BIOS/UEFI** - Version, updates, security patches
- 💿 **Operating System** - Windows Update, macOS patches, Linux updates
- 🛡️ **Antivirus** - Windows Defender status, definition age
- 🔌 **Drivers** - Graphics, network, chipset updates
- 💾 **Disk Health** - SMART status, failure predictions
- 💼 **Backup Status** - Last backup, destination, integrity
- 🔐 **Encryption** - BitLocker, FileVault, LUKS status
- 🔥 **Firewall** - Status, open ports, suspicious services

**Educational Library:**
- Comprehensive "What is X?" guides
- "Why does X matter?" explanations
- Step-by-step fix instructions
- Security best practices

**See:** [Full Roadmap](ROADMAP.md)

---

## 🔒 Privacy Commitment

**DevAudit is privacy-first by design:**

✅ **Local-First** - All scans run on YOUR machine
✅ **Zero Telemetry** - We never collect usage data
✅ **No Cloud Dependencies** - Works 100% offline
✅ **You Own Your Data** - Scan history stored locally on YOUR filesystem
✅ **Open Source** - Audit our code anytime (MIT License)

**Future Cloud Modes:**
- Opt-in only (local mode always free)
- Zero-knowledge encryption (we can't read your data)
- You hold the keys
- Cancel anytime, full local mode restored

**See:** [Privacy Philosophy](VISION.md#our-principles)

---

## 🗺️ Roadmap

| Version | Theme | Target | Status |
|---------|-------|--------|--------|
| v0.1.0 | Developer Environment Auditing | Jan 2025 | ✅ Released |
| v0.2.x | Interactive Dashboard & History | Jan 2025 | ✅ Released |
| **v0.3.0** | **System-Wide Scanning** | Feb 2025 | 🚧 In Planning |
| v0.4.0 | Educational Library | Mar 2025 | 📋 Planned |
| v0.5.0 | Remediation Engine | Apr 2025 | 📋 Planned |
| v0.6.0 | Multi-Device Support | May 2025 | 📋 Planned |
| v0.7.0 | Automation & Scheduling | Jun 2025 | 📋 Planned |
| v0.8.0 | Notifications & Alerts | Jul 2025 | 📋 Planned |
| v1.0.0 | Cloud Tiers (Optional) | Sep 2025 | 📋 Planned |

**Read More:** [Complete Roadmap](ROADMAP.md)

---

## 💡 Example Workflows

### Keep Your Laptop Secure

```bash
# Run weekly scan
devaudit serve
# Click "Run Scan" → Review findings → Apply fixes
```

### Monitor Project Dependencies

```bash
# Check for vulnerabilities before deployment
cd ~/projects/production-app
devaudit scan --format json > pre-deploy-audit.json

# Review vulnerabilities
cat pre-deploy-audit.json | jq '.vulnerabilities'
```

### Raspberry Pi Home Hub

```bash
# On Raspberry Pi
pip3 install devaudit[server]
sudo systemctl enable devaudit
sudo systemctl start devaudit

# Access from phone/tablet/laptop
# http://raspberrypi.local:8888
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Security Audit
  run: |
    pip install devaudit
    devaudit scan --format json
    # Fail if critical vulnerabilities found
    CRITICAL=$(jq '[.vulnerabilities[] | select(.severity=="CRITICAL")] | length' audit.json)
    if [ "$CRITICAL" -gt 0 ]; then exit 1; fi
```

---

## 📚 Documentation

- **📖 [Vision & Philosophy](VISION.md)** - Our mission, principles, and commitments
- **🎯 [Use Cases](USE_CASES.md)** - Detailed deployment scenarios and examples
- **🥧 [Raspberry Pi Guide](RASPBERRY_PI.md)** - Complete step-by-step Pi setup
- **🗺️ [Roadmap](ROADMAP.md)** - Detailed feature roadmap through v1.0
- **📝 [Changelog](CHANGELOG.md)** - Version history and release notes
- **🛠️ [Contributing](CONTRIBUTING.md)** - How to contribute (coming soon)

---

## 📦 Requirements

**Core CLI:**
- Python 3.8+
- Cross-platform (Windows, macOS, Linux)

**Web Dashboard (optional):**
- FastAPI 0.104.0+
- uvicorn 0.24.0+
- websockets 12.0+
- Install with: `pip install devaudit[server]`

**Tools to Audit (optional):**
- Python, Node.js, Docker, Go (only if you want to audit them)

---

## 🤝 Contributing

We welcome contributions! DevAudit is open source (MIT License) and community-driven.

**Ways to contribute:**
- 🐛 Report bugs and suggest features
- 📚 Improve documentation
- 🔧 Submit code contributions
- 💬 Answer questions and help others
- ⭐ Star the repo to show support

**See:** [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Free to use, modify, and distribute. No restrictions.

---

## 🙏 Acknowledgments

- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
- CLI framework by [Click](https://click.palletsprojects.com/)
- Dashboard built with [Next.js](https://nextjs.org/) and [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by the need for honest, educational security tools

---

## 📞 Support & Community

- **GitHub Issues:** [Report bugs or request features](https://github.com/aramantos/devaudit/issues)
- **GitHub Discussions:** [Ask questions, share ideas](https://github.com/aramantos/devaudit/discussions)
- **Email:** john.doyle.mail@icloud.com

---

## ⭐ Show Your Support

If DevAudit helps you stay secure, please:
- ⭐ **Star the repository** on GitHub
- 🐦 **Share it** with friends and colleagues
- 📝 **Write about it** on your blog or social media
- 🤝 **Contribute** code, docs, or ideas

Every star and share helps more people discover privacy-first security tools!

---

**DevAudit** - *Empowering digital security through education and transparency.* 🔍

*Because knowing your environment is the first step to protecting it.*
