# Planning Documentation

This folder contains active development documentation for DevAudit contributors.

## 📚 File Guide

### Start Here
- **[STATUS.md](STATUS.md)** - Current project state, completed features, and immediate priorities
  - Check this first to understand where we are
  - Updated after each milestone release

### Implementation Guides
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - Detailed implementation tasks with code templates
  - Step-by-step instructions for v0.3.0 system auditors
  - Follow the BIOS auditor template pattern
  - Includes educational content guidelines

### Design & Architecture
- **[DESIGN_SYSTEM_MASTER.md](DESIGN_SYSTEM_MASTER.md)** - UI/UX guidelines
  - Color palette (emerald green, electric blue)
  - Component patterns and typography
  - Consistent visual language

- **[COMPETITIVE_ANALYSIS.md](COMPETITIVE_ANALYSIS.md)** - Market positioning
  - How DevAudit differs from competitors
  - Unique value propositions

## 🎯 Current Focus (v0.3.0)

**Milestone:** System-Wide Security Scanning
**Goal:** Implement 7 additional system auditors (OS Update, Antivirus, Firewall, Disk Health, Backup, Encryption, Driver)

**Template to Follow:**
- See `devaudit/auditors/system_auditors/bios_audit.py`
- Inherit from `BaseAuditor`
- Return educational content from `docs/concepts/`

## 🚀 Quick Start for Contributors

1. Read [STATUS.md](STATUS.md) for current state
2. Check [NEXT_STEPS.md](NEXT_STEPS.md) for available tasks
3. Review [CONTRIBUTING.md](../CONTRIBUTING.md) for code standards
4. Fork the repo and create a feature branch
5. Follow the auditor template pattern
6. Write educational content in `docs/concepts/`
7. Submit a PR with tests

## 📖 Related Documentation

### User-Facing (docs/)
- User guides and tutorials
- Educational security content
- Architecture overviews

### Public (root)
- README.md - Project overview
- ROADMAP.md - Long-term vision
- CHANGELOG.md - Version history
- CONTRIBUTING.md - Contribution guidelines

### Private (gitignored)
- Internal notes and vision documents
- Personal development records

## 💡 Need Help?

- Create a GitHub issue for questions
- Check the [ROADMAP](../ROADMAP.md) for long-term direction
- See [.claude/SUGGESTIONS.md](../.claude/SUGGESTIONS.md) for improvement ideas

---

**Maintained by:** DevAudit Contributors
**Last Updated:** 2025-01-20
**License:** MIT
