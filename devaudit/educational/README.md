# Educational Content System

**Version:** v0.3.0+
**Purpose:** Provide educational content to users explaining security findings

---

## Overview

The educational content system helps DevAudit explain security findings in plain language. Instead of just reporting "CVE-2023-1234 found", DevAudit explains:

- **What is this?** - Simple explanation of the issue
- **Why does it matter?** - Real-world impact and risks
- **When should I act?** - Urgency guidance
- **When can I skip?** - Safe-to-ignore scenarios
- **How do I fix it?** - Step-by-step instructions
- **What are the risks?** - Risks of taking action
- **Where can I learn more?** - Link to comprehensive docs

---

## Architecture

### Content Sources

Educational content comes from two sources:

**1. Markdown Files** (`docs/concepts/*.md`)
- Comprehensive guides (3,000+ words each)
- Covers topics like CVEs, dependencies, Docker cleanup, BIOS updates
- Parsed automatically by `EducationalContentLoader`

**2. Inline Content** (in auditor code)
- Quick summaries for specific findings
- Fallback when markdown file doesn't exist
- Defined in auditor's `get_educational_content()` method

### Content Loader

**Module:** `devaudit/educational/content_loader.py`

**Features:**
- Auto-detects `docs/concepts/` directory
- Parses markdown files into structured content
- Caches content for performance
- Provides fallback content if files missing
- Simple API: `get_educational_content(topic)`

---

## Usage

### For Auditors

**Basic usage:**

```python
from devaudit.educational import get_educational_content

class MyAuditor(BaseAuditor):
    def get_educational_content(self) -> dict:
        """Get educational content from markdown file."""
        return get_educational_content("my-topic")
```

**With fallback:**

```python
from devaudit.educational import get_educational_content

class MyAuditor(BaseAuditor):
    def get_educational_content(self) -> dict:
        """Get educational content with inline fallback."""
        fallback = {
            "what_is_it": "Brief explanation of my auditor",
            "why_it_matters": "Why this matters for security",
            "when_to_update": "Update when...",
            "when_to_skip": "Skip if...",
            "how_to_fix": "Run this command...",
            "risks": "Be careful of...",
            "learn_more_url": "https://..."
        }
        return get_educational_content("my-topic", fallback=fallback)
```

**Override with custom content:**

```python
class MyAuditor(BaseAuditor):
    def get_educational_content(self) -> dict:
        """Custom educational content."""
        return {
            "what_is_it": "Custom explanation",
            "why_it_matters": "Custom importance",
            "when_to_update": "Custom urgency",
            "when_to_skip": "Custom skip conditions",
            "how_to_fix": "Custom fix instructions",
            "risks": "Custom risks",
            "learn_more_url": "https://custom-url.com"
        }
```

### For Content Writers

**1. Create markdown file in `docs/concepts/`**

**Example:** `docs/concepts/my-topic.md`

```markdown
# Understanding My Topic

Brief introduction explaining what this topic is about.

This is the first paragraph after the title—it becomes "what_is_it".

---

## Why It Matters

This section explains the real-world impact.

Can include multiple paragraphs. The entire section becomes "why_it_matters".

---

## When to Update

Explain when users should take action.

This becomes "when_to_update".

---

## When to Skip

Explain when it's safe to ignore.

This becomes "when_to_skip".

---

## How to Fix It

Step-by-step instructions.

This becomes "how_to_fix".

---

## Risks

Explain risks of taking action.

This becomes "risks".
```

**2. The content loader automatically:**
- Extracts the first paragraph as "what_is_it"
- Finds sections by headers (## Why..., ## When to..., etc.)
- Cleans markdown formatting
- Truncates to 500 characters for inline display
- Generates "learn_more_url" automatically

**3. Test your content:**

```python
from devaudit.educational import get_educational_content

content = get_educational_content("my-topic")
print(content)
```

---

## Available Topics

### Current (v0.2.x)

| Topic | File | Description |
|-------|------|-------------|
| `cves` | `docs/concepts/cves.md` | Understanding CVEs and vulnerabilities |
| `dependencies` | `docs/concepts/dependencies.md` | Package dependencies and supply chain |
| `docker-cleanup` | `docs/concepts/docker-cleanup.md` | Docker disk cleanup |

### Planned (v0.3.0)

| Topic | File | Description |
|-------|------|-------------|
| `bios-uefi` | `docs/concepts/bios-uefi.md` | BIOS/UEFI updates |
| `os-updates` | `docs/concepts/os-updates.md` | Operating system updates |
| `antivirus` | `docs/concepts/antivirus.md` | Antivirus status |
| `disk-health` | `docs/concepts/disk-health.md` | Disk health monitoring |
| `backup` | `docs/concepts/backup.md` | Backup status |
| `encryption` | `docs/concepts/encryption.md` | Disk encryption |
| `firewall` | `docs/concepts/firewall.md` | Firewall status |

---

## Content Structure

All educational content follows this structure:

```python
{
    "what_is_it": str,         # Brief explanation (1-3 sentences)
    "why_it_matters": str,     # Real-world impact (1-2 paragraphs)
    "when_to_update": str,     # Urgency guidance (1-2 paragraphs)
    "when_to_skip": str,       # Safe-to-ignore scenarios (1-2 paragraphs)
    "how_to_fix": str,         # Step-by-step fix (1-3 paragraphs)
    "risks": str,              # Risks of action (1-2 paragraphs)
    "learn_more_url": str      # Link to full docs (URL)
}
```

**Guidelines:**
- **what_is_it:** Simple explanation, no jargon, <200 characters
- **why_it_matters:** Real-world examples, attack scenarios
- **when_to_update:** Clear urgency indicators (critical, high, medium, low)
- **when_to_skip:** Honest about when it's safe to ignore
- **how_to_fix:** Platform-specific if needed, code examples
- **risks:** Acknowledge risks of taking action (updates can break things)
- **learn_more_url:** Always provide link to comprehensive docs

---

## Testing

### Manual Testing

```python
from devaudit.educational import get_educational_content

# Test loading from markdown
content = get_educational_content("cves")
assert "CVE" in content["what_is_it"]

# Test fallback
content = get_educational_content("nonexistent-topic", fallback={"what_is_it": "Fallback"})
assert content["what_is_it"] == "Fallback"

# Test cache clearing
from devaudit.educational import clear_educational_cache
clear_educational_cache()
```

### Unit Tests

**File:** `tests/test_educational_content.py`

```python
import pytest
from devaudit.educational import get_educational_content, clear_educational_cache

def test_load_cves_content():
    """Test loading CVE educational content."""
    content = get_educational_content("cves")
    assert "CVE" in content["what_is_it"]
    assert "learn_more_url" in content

def test_fallback_content():
    """Test fallback when topic doesn't exist."""
    fallback = {"what_is_it": "Custom fallback"}
    content = get_educational_content("nonexistent", fallback=fallback)
    assert content["what_is_it"] == "Custom fallback"

def test_cache_clearing():
    """Test cache clearing."""
    content1 = get_educational_content("cves")
    clear_educational_cache()
    content2 = get_educational_content("cves")
    assert content1 == content2  # Content should be same after reload
```

---

## Integration with Auditors

### BaseAuditor Integration

**File:** `devaudit/auditors/base.py`

```python
from devaudit.educational import get_educational_content

class BaseAuditor(ABC):
    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about this auditor's findings.

        Override this in subclasses to provide specific educational content.

        Returns:
            Dict with educational content keys
        """
        # Default implementation - subclasses should override
        return {
            "what_is_it": f"{self.name} helps manage your development environment.",
            "why_it_matters": "Keeping tools updated improves security and stability.",
            "when_to_update": "Update when you see outdated packages or vulnerabilities.",
            "when_to_skip": "If everything is working well, updates can wait.",
            "how_to_fix": f"Use {self.name}'s built-in update commands.",
            "risks": "Updates may rarely introduce breaking changes.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/README.md"
        }
```

### Example: BIOS Auditor

**File:** `devaudit/auditors/system_auditors/bios_audit.py`

```python
from devaudit.auditors.base import BaseAuditor
from devaudit.educational import get_educational_content

class BIOSAuditor(BaseAuditor):
    def get_educational_content(self) -> dict:
        """Get educational content about BIOS updates."""
        return get_educational_content("bios-uefi")
```

### Example: Python Auditor

**File:** `devaudit/auditors/package_auditors/python_audit.py`

```python
from devaudit.educational import get_educational_content

class PythonAuditor(BaseAuditor):
    def get_educational_content(self) -> dict:
        """Get educational content about Python packages."""
        # Use multiple topics
        base = get_educational_content("dependencies")
        cves = get_educational_content("cves")

        # Combine or use one
        return base  # or create custom mix
```

---

## Future Enhancements

### v0.4.0: Enhanced Content Loader
- Support for internationalization (i18n)
- Multiple languages (Spanish, French, German, etc.)
- Content versioning
- Dynamic content updates

### v0.5.0: Interactive Educational Mode
- Step-by-step tutorials
- Interactive fix verification
- Progress tracking ("You've learned about CVEs!")

### v0.6.0: Personalized Content
- Content adapted to user's skill level
- Remember what users have learned
- Reduce repetition for experienced users

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for:
- Writing educational content
- Content style guide
- Review process
- Educational content best practices

---

## Related Documentation

- [Educational Content Writing Guide](../../docs/guides/writing-educational-content.md) *(coming soon)*
- [V0.3.0 Architecture](../../docs/V0.3.0_ARCHITECTURE.md)
- [Content Concepts Index](../../docs/concepts/README.md) *(coming soon)*

---

*Last updated: January 2025 (v0.3.x planning)*
