# System Auditors

**Version:** v0.3.0+
**Category:** System-level security monitoring

This directory contains auditors that check system-wide security posture beyond package management.

---

## Auditors (Planned for v0.3.0)

### 1. BIOS/UEFI Auditor (`bios_audit.py`)
- **Purpose:** Check BIOS version and detect updates
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** Yes
- **Risk Factors:** BIOS age, known vulnerabilities

### 2. OS Update Auditor (`os_audit.py`)
- **Purpose:** Check for pending OS updates and security patches
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** No (read-only)
- **Risk Factors:** Security patches pending, update count

### 3. Antivirus Status Auditor (`antivirus_audit.py`)
- **Purpose:** Verify antivirus installation and status
- **Platforms:** Windows (primary), macOS, Linux
- **Requires Admin:** No
- **Risk Factors:** No AV, disabled protection, outdated definitions

### 4. Driver Update Auditor (`driver_audit.py`)
- **Purpose:** Check for outdated device drivers
- **Platforms:** Windows (primary)
- **Requires Admin:** No
- **Risk Factors:** Critical driver age, unsigned drivers

### 5. Disk Health Auditor (`disk_audit.py`)
- **Purpose:** Monitor SMART status and predict failures
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** No (with smartmontools)
- **Risk Factors:** Reallocated sectors, temperature, predicted failure

### 6. Backup Status Auditor (`backup_audit.py`)
- **Purpose:** Verify backup configuration and freshness
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** No
- **Risk Factors:** Days since last backup, no backup configured

### 7. Encryption Auditor (`encryption_audit.py`)
- **Purpose:** Check disk encryption status
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** No
- **Risk Factors:** Unencrypted system drive, sensitive data exposed

### 8. Firewall Auditor (`firewall_audit.py`)
- **Purpose:** Check firewall status and open ports
- **Platforms:** Windows, macOS, Linux
- **Requires Admin:** No
- **Risk Factors:** Firewall disabled, suspicious open ports

---

## Architecture

All system auditors follow this pattern:

```python
from devaudit.auditors.base import BaseAuditor, RiskLevel, AuditorCategory

class ExampleAuditor(BaseAuditor):
    """Example system auditor."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Example"
        self.category = AuditorCategory.SYSTEM
        self.supported_platforms = ["Windows", "Darwin", "Linux"]

    def is_installed(self) -> bool:
        """Check if this auditor can run."""
        return self.can_run()

    def get_version(self) -> Optional[str]:
        """Get version if applicable."""
        return None  # System auditors may not have versions

    def audit(self) -> dict:
        """Perform the audit."""
        if not self.can_run():
            return {
                "installed": False,
                "reason": "Insufficient permissions or unsupported platform"
            }

        result = {
            "installed": True,
            "status": self._check_status(),
            "issues": self._find_issues(),
            "educational_content": self.get_educational_content(),
        }

        result["risk_level"] = self.assess_risk(result).value
        return result

    def get_educational_content(self) -> dict:
        """Return educational content."""
        return {
            "what_is_it": "Explanation of what this auditor checks",
            "why_it_matters": "Real-world security impact",
            "when_to_update": "Guidance on urgency",
            "when_to_skip": "When it's safe to ignore",
            "how_to_fix": "Step-by-step remediation",
            "risks": "Risks of taking action",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/example.md"
        }

    def assess_risk(self, result: dict) -> RiskLevel:
        """Assess risk based on findings."""
        # Custom risk logic here
        return RiskLevel.LOW

    def requires_elevation(self) -> bool:
        """Check if admin/root needed."""
        return False  # or True if needed
```

---

## Educational Content

Each auditor provides inline educational content explaining:
- **What it is** - Simple explanation
- **Why it matters** - Real-world impact
- **When to act** - Urgency guidance
- **When to skip** - Safe to ignore scenarios
- **How to fix** - Step-by-step instructions
- **Risks** - Potential issues from fixing
- **Learn more** - Link to comprehensive docs

Educational content lives in `docs/concepts/`:
- `docs/concepts/bios.md`
- `docs/concepts/os_updates.md`
- `docs/concepts/antivirus.md`
- etc.

---

## Risk Assessment

Risk levels:
- **NONE** - Nothing to report or not installed
- **LOW** - Minor issues, low urgency
- **MEDIUM** - Notable issues, moderate urgency
- **HIGH** - Significant issues, high urgency
- **CRITICAL** - Severe issues, immediate action required

Risk assessment considers:
- Age of outdated components
- Severity of vulnerabilities
- Impact of missing protections
- Likelihood of exploitation

---

## Testing

Each auditor requires:
- Unit tests for core logic
- Platform-specific tests (Windows/macOS/Linux)
- Permission tests (with/without admin)
- Error handling tests
- Educational content validation

---

## Implementation Priority (v0.3.0)

**Phase 1 (Core):**
1. BIOS auditor
2. OS update auditor
3. Antivirus auditor

**Phase 2 (Secondary):**
4. Disk health auditor
5. Backup auditor
6. Encryption auditor
7. Firewall auditor

**Phase 3 (Optional):**
8. Driver auditor (Windows-specific complexity)

---

## See Also

- [v0.3.0 Architecture Plan](../../../docs/V0.3.0_ARCHITECTURE.md)
- [Base Auditor Documentation](../base.py)
- [Educational Content Guidelines](../../../CONTRIBUTING.md)
