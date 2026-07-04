# AI-Powered Security Insights

DevAudit now includes optional AI-powered security recommendations using Google Vertex AI (Gemini 2.0 Flash).

## 🎯 What It Does

The AI analyzer takes your DevAudit scan results and provides:

- **Priority Action** - The most important thing to fix and why it matters most
- **Top 3 Recommendations** - Specific, actionable steps prioritized by security impact
- **Security Score** - Overall security posture rating (0-100)
- **Risk Summary** - One-sentence explanation of your biggest current risk

## 🔒 Privacy & Transparency

**100% Privacy-Respecting:**
- Only enabled if you explicitly install and configure it
- Uses **your own** Google Cloud project (you control the data)
- No telemetry or external logging
- Can be disabled anytime
- Completely optional - core DevAudit works without it

**Data Flow:**
```
Your Machine → Your GCP Project → Gemini API → Back to Your Machine
```

All analysis happens in your Google Cloud account. DevAudit doesn't see or store any of this data.

## 📦 Installation

### Step 1: Install AI Dependencies

```bash
pip install 'devaudit[ai]'
```

This installs:
- `google-cloud-aiplatform>=1.36.0`
- `google-auth>=2.0.0`
- `google-api-core>=2.0.0`

### Step 2: Configure Google Cloud Credentials

**Option A: Using gcloud CLI (Recommended)**
```bash
gcloud auth application-default login
```

**Option B: Using Service Account**
1. Create a service account in Google Cloud Console
2. Download the JSON key
3. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

**Option C: Using Environment Variables**
```bash
export DEVAUDIT_VERTEX_PROJECT="your-gcp-project-id"
export DEVAUDIT_VERTEX_LOCATION="us-central1"
export DEVAUDIT_VERTEX_MODEL="gemini-2.0-flash"
```

## 🚀 Usage

### In the Dashboard

1. Run a scan: Click "Run Scan" button
2. The AI Insights card will appear below the System Auditors Carousel
3. Click "Analyze with AI" to get intelligent recommendations
4. View your security score, priority action, and top recommendations

### Via API

**Get AI Status:**
```bash
curl http://localhost:8888/api/ai/status
```

**Analyze Latest Scan:**
```bash
curl -X POST http://localhost:8888/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Analyze Specific Scan:**
```bash
curl -X POST http://localhost:8888/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"scan_id": "scan_123"}'
```

## 💰 Cost

Gemini 2.0 Flash is extremely cost-effective:

**Pricing (as of Jan 2025):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Typical DevAudit Analysis:**
- Input: ~1,500 tokens (scan results)
- Output: ~300 tokens (recommendations)
- **Cost per analysis: ~$0.0002 (less than $0.01 for 50 scans)**

For personal use, you'll likely stay within Google Cloud's free tier.

## 🎨 Example Output

```json
{
  "priority_action": "Update Windows Defender security intelligence immediately - your definitions are 3 days old, leaving you vulnerable to recent malware variants",
  "recommendations": [
    "Run Windows Update to install 2 pending security patches addressing critical vulnerabilities",
    "Configure automatic File History backup - you currently have no backup system, risking complete data loss",
    "Update 3 Python packages with known CVEs (requests, urllib3, cryptography) to patch security vulnerabilities"
  ],
  "security_score": 62,
  "risk_summary": "Medium risk due to outdated antivirus definitions and missing backup system",
  "severity": "medium",
  "color": "yellow"
}
```

## 🛠️ Configuration

### Configuration

AI features run against YOUR own Google Cloud project. There is no default
project baked in - `DEVAUDIT_VERTEX_PROJECT` is required:

```bash
# Required: your own GCP project
export DEVAUDIT_VERTEX_PROJECT="my-project-id"

# Use a different region
export DEVAUDIT_VERTEX_LOCATION="europe-west1"

# Use a different model
export DEVAUDIT_VERTEX_MODEL="gemini-1.5-pro"
```

## 🔍 How It Works

1. **Scan Analysis** - DevAudit collects security information from 12+ auditors
2. **Data Preparation** - Scan results are summarized into a structured prompt
3. **AI Processing** - Gemini analyzes the data and generates recommendations
4. **Response Parsing** - DevAudit extracts actionable insights from AI response
5. **Dashboard Display** - Results are beautifully presented with priority ranking

## ⚠️ Troubleshooting

### "Vertex AI not available"

Install the AI package:
```bash
pip install 'devaudit[ai]'
```

### "Vertex AI SDK available but not configured"

Configure Google Cloud credentials:
```bash
gcloud auth application-default login
```

### "AI analysis failed"

Check your GCP project has Vertex AI API enabled:
```bash
gcloud services enable aiplatform.googleapis.com
```

### Authentication Errors

Verify your credentials:
```bash
gcloud auth application-default print-access-token
```

## 🎓 Technical Details

### Model Selection

**Gemini 2.0 Flash** was chosen for:
- **Speed** - Near-instant responses (<2 seconds)
- **Cost** - 95% cheaper than GPT-4
- **Quality** - Excellent at structured analysis tasks
- **Availability** - Generally available in Vertex AI

### Prompt Engineering

The AI analyzer uses a carefully crafted prompt that:
- Provides context about the scan (critical/high issues, vulnerabilities)
- Requests specific output format (priority action, recommendations, score)
- Enforces concise, educational responses
- Focuses on actionable insights over generic advice

### Fallback Behavior

If AI analysis fails:
- User sees a friendly error message
- "Try Again" button is displayed
- Core DevAudit functionality is unaffected
- Scan results remain accessible

## 🔮 Future Enhancements

Potential improvements (v0.4.0+):
- **Trend Analysis** - AI compares multiple scans to identify security trends
- **Learning Recommendations** - Links to educational content based on your risks
- **Auto-Remediation Suggestions** - AI generates specific fix commands
- **Risk Prediction** - Predict future issues based on current state
- **Multi-Language Support** - Recommendations in user's preferred language

## 📚 Learn More

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Google Cloud Pricing](https://cloud.google.com/vertex-ai/pricing)
- [DevAudit Architecture](./V0.3.0_ARCHITECTURE.md)

---

**Questions or Issues?**
- GitHub Issues: https://github.com/aramantos/devaudit/issues
- Email: john.doyle.mail@icloud.com
