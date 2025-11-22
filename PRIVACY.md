# Privacy Policy

**Last Updated: January 22, 2025**

DevAudit is committed to protecting your privacy. This policy explains what data we collect, how we use it, and your rights.

## TL;DR (Summary)

- ✅ **Core scanning is 100% local** - no data leaves your machine
- ✅ **No telemetry, tracking, or analytics**
- ⚠️ **AI features send data to Google Cloud** (optional, opt-in only)
- ✅ **You control your data** - it's your Google Cloud project
- ✅ **No third-party sharing** (except Google Cloud for AI features)

---

## 1. Data Collection

### 1.1 Core Scanning Features (100% Local)

**What DevAudit Scans:**
- Installed packages (Python, Node.js, Docker, Go)
- System security settings (BIOS, OS updates, antivirus, firewall, etc.)
- Disk health and backup status
- Driver versions
- Vulnerabilities (CVEs)

**Where This Data Goes:**
- **Nowhere.** All scanning happens on your local machine.
- Scan results are saved locally in `~/.devaudit/history/` (or `%APPDATA%/devaudit/history/` on Windows)
- No data is transmitted to external servers
- No telemetry, tracking, or usage analytics

**You are in complete control.** Delete the history folder anytime to remove all scan data.

---

### 1.2 AI-Powered Insights (Optional - Sends Data to Google Cloud)

**What Happens When You Use AI Features:**

When you click "Analyze with AI" or use the voice assistant:

1. **Your scan results** are sent to **Google Cloud Vertex AI** (Gemini)
2. This includes:
   - Package names and versions
   - Vulnerability information (CVEs)
   - System security status
   - Risk levels and recommendations
3. Google's Gemini AI analyzes this data and returns security recommendations
4. The conversation is processed through **your own Google Cloud project**

**Important Privacy Notes:**

- ✅ **Opt-in only** - AI features require explicit installation (`pip install 'devaudit[ai]'`) and configuration
- ✅ **Your Google Cloud project** - Data goes to YOUR GCP account, not ours
- ✅ **You control the data** - Review Google Cloud's [Data Processing Terms](https://cloud.google.com/terms/data-processing-addendum)
- ⚠️ **Not 100% local** - Data leaves your machine when using AI features
- ✅ **Can be disabled** - Uninstall AI dependencies or don't use the feature

**Google Cloud Privacy:**
- Google processes the data according to their [Privacy Policy](https://policies.google.com/privacy)
- Data is processed in the region you configure (default: `us-central1`)
- Google does not use your data to train their models without permission
- Vertex AI API calls are logged in your GCP project (you control retention)

---

### 1.3 Voice Assistant (Optional - Sends Audio to Google Cloud)

**What Happens When You Use Voice Input:**

When you click the microphone icon and speak:

1. **Your voice audio** is captured by your browser
2. Audio is transcribed using:
   - Browser's built-in Web Speech API (preferred, stays local), OR
   - Google Cloud Speech-to-Text (if browser API unavailable)
3. **The transcript + your scan data** is sent to Vertex AI for conversational responses

**Privacy for Voice Features:**

- ✅ **Browser Web Speech API** - Processes audio locally when available (Chrome, Edge)
- ⚠️ **Fallback to Google Cloud** - If browser API unavailable, audio sent to Google
- ✅ **No audio storage** - Audio is transcribed and immediately discarded
- ✅ **Opt-in** - Only works when you explicitly click the microphone button

---

## 2. Data Storage

### 2.1 Local Storage

**Where DevAudit stores data on your machine:**

- **Scan history:** `~/.devaudit/history/` (Linux/Mac) or `%APPDATA%\devaudit\history\` (Windows)
- **AI preferences:** Browser localStorage (e.g., ignored auditors)
- **Dashboard settings:** Browser localStorage (theme, keyboard shortcuts)

**You can delete any of this data at any time.**

### 2.2 Google Cloud Storage

**If you use AI features:**

- Vertex AI API calls are logged in your Google Cloud project
- You can configure log retention in Google Cloud Console
- Google may temporarily cache API responses (per their terms)

**We do not store any of your data.** All AI processing happens in your GCP account.

---

## 3. Data Sharing

### 3.1 Who We Share Data With

**Core DevAudit:**
- **No one.** Your data never leaves your machine.

**AI Features (if enabled):**
- **Google Cloud (Vertex AI)** - To provide AI-powered recommendations
- **Your Google Cloud Project** - You control access and permissions
- **No other third parties**

### 3.2 What We Do NOT Share

- ❌ We do not sell your data
- ❌ We do not share data with advertisers
- ❌ We do not use your data for marketing
- ❌ We do not send data to Anthropic, OpenAI, or other AI providers
- ❌ We do not track your usage

---

## 4. Your Rights

You have the following rights regarding your data:

- ✅ **Right to Access** - All your data is stored locally; you can view it anytime
- ✅ **Right to Delete** - Delete scan history folder or browser localStorage
- ✅ **Right to Export** - Scan results are in JSON format; export anytime
- ✅ **Right to Opt-Out** - Don't install AI features or don't use them
- ✅ **Right to Control** - Use AI preferences to filter what's sent to Google

---

## 5. Security

### 5.1 How We Protect Your Data

- **Local-first design** - Most data never leaves your machine
- **No authentication required** - No passwords, no accounts, no breaches
- **Open source** - Code is auditable on GitHub
- **Minimal dependencies** - Reduces attack surface

### 5.2 Google Cloud Security

If you use AI features:
- Data transmitted over HTTPS (encrypted in transit)
- Google Cloud's enterprise-grade security
- You control access with Google Cloud IAM

---

## 6. Children's Privacy

DevAudit is not intended for children under 13. We do not knowingly collect data from children.

---

## 7. Changes to This Policy

We may update this privacy policy as we add new features. Changes will be:

- Documented in `CHANGELOG.md`
- Announced in GitHub releases
- Effective immediately upon posting

**Last updated:** January 22, 2025

---

## 8. Contact

Questions about privacy?

- **GitHub Issues:** https://github.com/aramantos/devaudit/issues
- **Email:** john.doyle.mail@icloud.com

---

## 9. Legal

DevAudit is provided "as is" without warranty. See [LICENSE](LICENSE) and [TERMS.md](TERMS.md) for full legal terms.

---

**Privacy Promise:**

We built DevAudit because we were tired of security tools that spy on users. Core DevAudit will always be 100% local. AI features are optional and transparent. You control your data.

If we ever change this fundamental privacy promise, we will:
1. Announce it prominently
2. Provide 90 days notice
3. Allow you to export your data
4. Keep the old version available

We respect your privacy. Period.
