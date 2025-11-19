# Contributing to DevAudit

Thank you for your interest in contributing to DevAudit! We're building a privacy-first personal security assistant, and we need your help to make it accessible, educational, and empowering for everyone.

---

## 🎯 Our Mission

**Empower people to understand and protect their digital life through education and transparency.**

Before contributing, please read our [Vision & Philosophy](VISION.md) to understand what we're building and why.

---

## 📋 Table of Contents

1. [Ways to Contribute](#ways-to-contribute)
2. [Code Contributions](#code-contributions)
3. [Documentation Contributions](#documentation-contributions)
4. [Bug Reports](#bug-reports)
5. [Feature Requests](#feature-requests)
6. [Community Support](#community-support)
7. [Development Setup](#development-setup)
8. [Code Style Guide](#code-style-guide)
9. [Testing Guidelines](#testing-guidelines)
10. [Pull Request Process](#pull-request-process)

---

## 🤝 Ways to Contribute

You don't need to be a developer to contribute! Here are all the ways you can help:

### 1. 💻 Code Contributions
- Implement new auditors (BIOS, drivers, OS updates, disk health)
- Fix bugs and improve performance
- Enhance dashboard UI/UX
- Write automated tests
- Optimize scan performance

### 2. 📚 Documentation
- Write educational content ("What is X?" guides)
- Create how-to tutorials
- Improve existing documentation
- Translate content (future)
- Record video tutorials

### 3. 🎨 Design
- Design new dashboard components
- Create diagrams and infographics
- Improve accessibility (WCAG compliance)
- Design educational visual aids
- Create marketing materials

### 4. 🧪 Testing
- Test beta features
- Report bugs with detailed reproduction steps
- Test on different platforms (Windows, macOS, Linux)
- Validate documentation accuracy
- Performance testing

### 5. 💬 Community
- Answer questions on GitHub Discussions
- Share your use case and setup
- Write blog posts about DevAudit
- Spread the word on social media
- Help onboard new users

### 6. 🔍 Research
- Research security best practices
- Investigate new auditor possibilities
- Benchmark against competitors
- Survey user needs
- Analyze security trends

---

## 💻 Code Contributions

### What We're Looking For

**High Priority:**
- System auditors (BIOS, OS updates, antivirus, drivers, disk health, backups)
- Educational content integration
- Remediation engine features
- Performance optimizations
- Cross-platform compatibility fixes

**Always Welcome:**
- Bug fixes (especially with tests)
- Documentation improvements
- Accessibility enhancements
- Code cleanup and refactoring
- Test coverage increases

**Please Discuss First:**
- Major architectural changes
- New dependencies
- Breaking changes
- UI redesigns
- Feature additions (check roadmap)

### Before You Start

1. **Check existing issues** - Someone might already be working on it
2. **Read the roadmap** - Ensure it aligns with our direction
3. **Open a discussion** - For large features, get feedback first
4. **Review our principles** - Ensure your contribution aligns with our [vision](VISION.md)

### Feature Alignment Checklist

Does your contribution:
- ✅ Educate users (not just alert them)?
- ✅ Respect privacy (local-first, no telemetry)?
- ✅ Empower (not control or surveill)?
- ✅ Provide transparency (explain risks honestly)?
- ✅ Maintain simplicity (avoid feature bloat)?

**If yes to all:** Proceed with confidence!
**If no to any:** Let's discuss how to align it with our mission.

---

## 📚 Documentation Contributions

Documentation is **just as important** as code. We need:

### Educational Content

**"What is X?" Articles** - Explain concepts simply
- What is BIOS/UEFI?
- What are CVEs?
- What is SMART disk monitoring?
- What is encryption (BitLocker/FileVault)?
- What are package dependencies?

**"Why Does X Matter?" Context** - Real-world impact
- Why update your BIOS?
- Why patch your OS?
- Why enable encryption?
- Why backup regularly?

**"How Do I Fix X?" Guides** - Step-by-step instructions
- How to update BIOS safely
- How to enable Windows Defender
- How to set up automated backups
- How to clean up Docker
- How to update packages safely

### Documentation Guidelines

1. **Write for beginners** - Assume no technical knowledge
2. **Avoid jargon** - Or explain it immediately
3. **Use examples** - Concrete beats abstract
4. **Be concise** - Respect readers' time
5. **Include visuals** - Screenshots, diagrams, videos
6. **Provide context** - Why it matters, when to do it
7. **Honest trade-offs** - Sometimes "skip it" is valid advice

### Documentation Structure

```
docs/
├── concepts/          # "What is X?"
├── guides/            # "How to do X"
├── platforms/         # Platform-specific (Windows/macOS/Linux)
└── advanced/          # CI/CD, automation, plugins
```

---

## 🐛 Bug Reports

Good bug reports help us fix issues quickly. Please include:

### Required Information

1. **DevAudit version** - `devaudit --version`
2. **Platform** - Windows 10, macOS 14, Ubuntu 22.04, etc.
3. **Python version** - `python --version`
4. **Installation method** - pip, source, etc.

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what happened.

**To Reproduce**
Steps to reproduce:
1. Run `devaudit scan`
2. Click on "Tools Detected"
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- DevAudit version: [e.g., 0.2.4]
- Platform: [e.g., Windows 11]
- Python version: [e.g., 3.11.5]
- Installation: [e.g., pip install devaudit[server]]

**Additional context**
Any other relevant information.
```

### Before Submitting

- [ ] Search existing issues to avoid duplicates
- [ ] Try with the latest version
- [ ] Include reproduction steps
- [ ] Provide error messages/logs
- [ ] Add screenshots if UI-related

---

## 💡 Feature Requests

We love hearing your ideas! Before requesting:

1. **Check the [roadmap](ROADMAP.md)** - It might already be planned
2. **Search existing requests** - Add your voice to existing discussions
3. **Consider our mission** - Does it align with education/privacy/empowerment?

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem. Ex: "I'm frustrated when..."

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Use case**
How would you use this feature? Who else would benefit?

**Alignment with mission**
How does this empower/educate/respect privacy?

**Additional context**
Mockups, examples, or related projects.
```

---

## 👥 Community Support

Help us build a welcoming community:

### Answering Questions

- Be patient and kind
- Link to relevant documentation
- Share your own experience
- Don't make assumptions about knowledge level
- Encourage learning, not just solutions

### Sharing Your Setup

Share how you use DevAudit:
- Raspberry Pi configurations
- CI/CD integrations
- Automation scripts
- Monitoring dashboards
- Educational use cases

**Where to share:**
- GitHub Discussions
- Blog posts (tag us!)
- Social media (we'll retweet/share)
- Video tutorials (we'll feature them)

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Node.js 18+ (for dashboard development)
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/aramantos/devaudit.git
cd devaudit

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[server]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Dashboard Development

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=devaudit

# Run specific test file
pytest tests/test_python_audit.py

# Run dashboard tests
cd dashboard && npm test
```

### Project Structure

```
devaudit/
├── devaudit/              # Python package
│   ├── auditors/          # Auditor implementations
│   ├── reporters/         # Output formatters
│   ├── server/            # FastAPI server
│   └── cli.py             # CLI entry point
├── dashboard/             # Next.js dashboard
│   ├── src/
│   │   ├── app/           # Pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities
│   └── public/            # Static assets
├── tests/                 # Python tests
├── docs/                  # Documentation
└── README.md              # Main documentation
```

---

## 🎨 Code Style Guide

### Python

**We follow PEP 8** with some flexibility:
- Line length: 100 characters (not 79)
- Use type hints for function signatures
- Docstrings for public methods (Google style)
- Descriptive variable names (clarity > brevity)

**Example:**

```python
def audit_python_environment(target_dir: Optional[str] = None) -> dict:
    """
    Audit Python installation and packages.

    Args:
        target_dir: Optional directory to scan for project-specific info

    Returns:
        Dictionary containing Python audit results

    Raises:
        RuntimeError: If Python is not installed
    """
    result = {
        "installed": True,
        "version": get_python_version(),
        "packages": list_packages()
    }
    return result
```

**Tools:**
- Formatter: `black` (run before committing)
- Linter: `pylint` or `flake8`
- Type checker: `mypy` (optional but encouraged)

### TypeScript/React

**Dashboard follows:**
- ESLint configuration (Next.js defaults)
- Functional components with hooks
- TypeScript strict mode
- Tailwind CSS for styling

**Example:**

```typescript
interface AuditData {
  installed: boolean;
  version: string;
  packages: Package[];
}

export function PythonDetails({ data }: { data: AuditData }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold">Python</h2>
      {/* Component content */}
    </div>
  );
}
```

### General Principles

1. **Readability over cleverness** - Code is read more than written
2. **Explicit over implicit** - Be clear about intent
3. **Simple over complex** - Prefer straightforward solutions
4. **Tested over assumed** - Write tests for new features
5. **Documented over guessed** - Comment non-obvious logic

---

## 🧪 Testing Guidelines

### What to Test

**Required:**
- New auditors (unit tests)
- Bug fixes (regression tests)
- API endpoints (integration tests)
- Critical user paths (E2E tests)

**Nice to Have:**
- Edge cases
- Error handling
- Performance benchmarks
- Cross-platform behavior

### Test Structure

```python
import pytest
from devaudit.auditors import PythonAuditor

def test_python_auditor_detects_installation():
    """Test that Python auditor correctly detects Python installation."""
    auditor = PythonAuditor()
    result = auditor.audit()

    assert result["installed"] is True
    assert "version" in result
    assert result["version"].startswith("3.")

def test_python_auditor_finds_outdated_packages():
    """Test that outdated packages are correctly identified."""
    auditor = PythonAuditor()
    result = auditor.audit()

    assert "outdated_packages" in result
    assert isinstance(result["outdated_packages"], list)
```

### Running Tests Locally

```bash
# All tests
pytest

# With coverage report
pytest --cov=devaudit --cov-report=html

# Specific test
pytest tests/test_python_audit.py::test_python_auditor_detects_installation

# Verbose output
pytest -v
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guide
- [ ] Tests pass locally (`pytest`)
- [ ] New features have tests
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with main

### PR Title Format

```
[Type] Brief description

Examples:
[Feature] Add BIOS auditor for Windows
[Fix] Correct cleanup items count calculation
[Docs] Add guide for enabling BitLocker
[Refactor] Simplify package counting logic
[Test] Add tests for Docker auditor
```

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Automated checks** - CI runs tests, linters
2. **Code review** - Maintainer reviews code
3. **Discussion** - Address feedback, make changes
4. **Approval** - Maintainer approves
5. **Merge** - Squash and merge to main

**Timeline:** We aim to review PRs within 3-5 days.

---

## 🏆 Recognition

Contributors are recognized in:
- README.md acknowledgments
- CHANGELOG.md release notes
- GitHub contributor graph
- Social media shoutouts (with permission)

**Special recognition for:**
- First-time contributors
- Major feature implementations
- Comprehensive documentation
- Consistent community support

---

## 📜 Code of Conduct

### Our Standards

**We are committed to:**
- Being welcoming and inclusive
- Respecting differing viewpoints
- Accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Unprofessional conduct

### Enforcement

Violations can be reported to: john.doyle.mail@icloud.com

Maintainers will:
1. Investigate all complaints
2. Take appropriate action
3. Maintain confidentiality
4. Provide transparency in decisions

---

## ❓ Questions?

**Not sure where to start?**
- Check [good first issue](https://github.com/aramantos/devaudit/labels/good%20first%20issue) label
- Ask in [GitHub Discussions](https://github.com/aramantos/devaudit/discussions)
- Read the [roadmap](ROADMAP.md) for inspiration

**Need help with setup?**
- Open a discussion thread
- We're here to help!

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make DevAudit better for everyone. Whether you're fixing a typo, writing documentation, or implementing a major feature—**thank you** for being part of this mission to empower digital security through education and transparency.

Let's build something great together! 🚀

---

*Contributing guidelines last updated: January 2025 (v0.2.4)*
