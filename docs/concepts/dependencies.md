# Understanding Package Dependencies

When you install a single package, you're often getting dozens—or hundreds—of additional packages automatically. These are **dependencies**, and understanding them is crucial for security and maintainability.

This guide explains what dependencies are, why they matter, and how to manage them effectively.

---

## What Are Dependencies?

A **dependency** is a package that another package needs to function.

### Simple Example

You want to build a web API:

```bash
pip install flask
```

But Flask can't work alone. It needs:
- **Werkzeug** (HTTP server)
- **Jinja2** (templating)
- **Click** (command-line tools)
- **MarkupSafe** (string escaping)
- **itsdangerous** (session signing)

So installing Flask actually installs 6 packages.

### Real-World Example

Install a popular Python web framework:

```bash
pip install django
```

**Actual result:**
- Django itself
- asgiref (async support)
- sqlparse (SQL parsing)
- tzdata (timezone data)

Install a data science library:

```bash
pip install pandas
```

**Actual result:** 10+ packages
- pandas itself
- numpy (numerical computing)
- python-dateutil (date handling)
- pytz (timezones)
- six (Python 2/3 compatibility)
- And more...

### The Dependency Tree

Dependencies can have their own dependencies, creating a tree:

```
Your Project
├── requests (you installed this)
│   ├── urllib3
│   │   └── ... (urllib3's dependencies)
│   ├── certifi
│   ├── charset-normalizer
│   └── idna
├── flask (you installed this)
│   ├── werkzeug
│   │   └── ... (werkzeug's dependencies)
│   ├── jinja2
│   │   └── markupsafe
│   ├── click
│   └── itsdangerous
└── ... (hundreds more)
```

**You installed 2 packages. You got 50+.**

---

## Why Dependencies Matter for Security

### 1. Attack Surface

Every dependency is a potential vulnerability.

**The Math:**
- You: 1 package (your code)
- Direct dependencies: 10 packages
- Transitive dependencies: 100+ packages

**Your attack surface: 110+ packages**, not 1.

### 2. Supply Chain Attacks

Attackers know you don't audit dependencies closely.

**Real Attack Example: event-stream (2018)**
- Popular npm package (2 million downloads/week)
- Maintainer gave access to malicious contributor
- Attacker injected code to steal Bitcoin wallets
- Affected thousands of projects

**Real Attack Example: ua-parser-js (2021)**
- npm package with 7 million weekly downloads
- Attacker compromised maintainer account
- Published malicious version with crypto miner and credential stealer
- Ran on thousands of servers for hours

### 3. Unmaintained Dependencies

Dependencies can become abandoned:

```bash
pip install some-old-package
  └── ancient-dependency (last update: 2015)
      └── vulnerable-lib (known CVEs, no maintainer)
```

**Problem:** Even if `some-old-package` is secure, its dependencies might not be.

### 4. Dependency Confusion Attacks

Attackers create malicious packages with names similar to internal dependencies:

**Attack scenario:**
1. Company uses internal package `acme-auth`
2. Attacker publishes public package `acme-auth` to PyPI
3. Misconfigured build system installs public (malicious) version
4. Attacker gains access to company systems

---

## Types of Dependencies

### Direct Dependencies

Packages **you explicitly install**:

```python
# requirements.txt
flask==2.3.0
requests==2.31.0
psycopg2==2.9.5
```

**You control these.** You decide when to install and update them.

### Transitive (Indirect) Dependencies

Packages **your dependencies install**:

```python
# You installed flask
# Flask installed these (you didn't ask for them):
werkzeug==3.0.1
jinja2==3.1.2
click==8.1.7
```

**You don't directly control these.** They update when your direct dependencies update.

### Development Dependencies

Packages needed **only for development**, not production:

```python
# requirements-dev.txt
pytest==7.4.0        # Testing
black==23.10.0       # Code formatting
mypy==1.6.1          # Type checking
```

**Lower security risk** - not deployed, not exposed to attackers.

### Optional Dependencies

Packages that add **extra features** but aren't required:

```bash
# Basic install
pip install requests

# With optional features
pip install requests[security,socks]
  # Adds: cryptography, PySocks, pyOpenSSL
```

---

## How Package Managers Handle Dependencies

### Python (pip)

**Loose by default:**

```bash
pip install flask
# Installs: flask + all dependencies (latest compatible versions)
```

**Locked with requirements.txt:**

```python
# requirements.txt (generated with pip freeze)
flask==2.3.0
werkzeug==3.0.1
jinja2==3.1.2
click==8.1.7
markupsafe==2.1.3
itsdangerous==2.1.2
```

**Every version locked** - reproducible but needs manual updates.

### Node.js (npm)

**Automatically locks:**

```bash
npm install express
# Creates package-lock.json with exact versions of ALL dependencies
```

**package.json** = Your direct dependencies (with version ranges)
**package-lock.json** = Exact versions of everything (locked)

### Docker

**Layers dependencies:**

```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Dependencies baked into image - **updating requires rebuilding**.

---

## Finding Your Dependencies

### Python

```bash
# List all installed packages
pip list

# Show dependency tree
pip install pipdeptree
pipdeptree

# Example output:
# flask==2.3.0
#   - click [required: >=8.1.3, installed: 8.1.7]
#   - itsdangerous [required: >=2.1.2, installed: 2.1.2]
#   - jinja2 [required: >=3.1.2, installed: 3.1.2]
#     - markupsafe [required: >=2.0, installed: 2.1.3]
#   - werkzeug [required: >=3.0.0, installed: 3.0.1]
```

### Node.js

```bash
# List all packages (including transitive)
npm list

# List only direct dependencies
npm list --depth=0

# Show why a package is installed
npm why package-name
```

### With DevAudit

```bash
# See all packages organized by source
devaudit scan

# Export for analysis
devaudit scan --format json > packages.json
```

---

## Dependency Risks and How to Mitigate

### Risk 1: Outdated Dependencies

**Problem:** Dependencies with known vulnerabilities

**Detection:**
```bash
# Python
pip list --outdated

# Node.js
npm outdated

# DevAudit (checks vulnerabilities too!)
devaudit scan
```

**Mitigation:**
```bash
# Update specific package
pip install --upgrade package-name
npm update package-name

# Update all (careful!)
pip list --outdated | cut -d' ' -f1 | xargs pip install --upgrade
npm update
```

### Risk 2: Too Many Dependencies

**Problem:** Large attack surface, slow installs, bloated apps

**Detection:**
```bash
# Python: Count total packages
pip list | wc -l

# Node.js: Check node_modules size
du -sh node_modules/
# 300MB+ is concerning
```

**Mitigation:**
- **Choose lightweight alternatives**
  - Instead of: `pandas` (10+ dependencies)
  - Consider: Native Python data structures

- **Use optional dependencies sparingly**
  ```bash
  # Don't install everything
  pip install package[feature1,feature2]  # Only what you need
  ```

- **Audit before adding**
  ```bash
  # Check what you're getting
  pipdeptree -p package-name
  ```

### Risk 3: Malicious Packages

**Problem:** Typosquatting, compromised maintainers

**Detection:**
- Check package names carefully (reqeusts vs requests)
- Verify publisher reputation
- Check download counts (popular = more eyes = safer)
- Review recent version history (sudden changes = suspicious)

**Mitigation:**
```python
# requirements.txt - Use hashes to prevent tampering
flask==2.3.0 --hash=sha256:1234567890abcdef...
requests==2.31.0 --hash=sha256:abcdef1234567890...
```

Generate hashes:
```bash
pip hash package-name==version
```

### Risk 4: Unmaintained Dependencies

**Problem:** No security updates, accumulating vulnerabilities

**Detection:**
```bash
# Check last update date
pip show package-name | grep Updated

# Or on PyPI: https://pypi.org/project/package-name/
```

**Mitigation:**
- **Switch to maintained fork**
  ```bash
  # Old: pip install abandoned-package
  # New: pip install maintained-fork
  ```

- **Vendor the code** (copy into your project)
  - Pro: Full control, can patch yourself
  - Con: You're now the maintainer

- **Find alternative package**
  - Search for actively maintained alternatives
  - Check GitHub stars, last commit date, open issues

---

## Best Practices for Managing Dependencies

### 1. Minimize Dependencies

**Ask before adding:**
- Do I really need this?
- Can I implement it myself in <50 lines?
- Does this package do too much? (red flag)

**Example:**

```python
# Instead of installing entire library for one function:
# pip install huge-library  # 50+ dependencies

# Consider copying the specific function (check license!)
def only_function_i_need():
    # Implementation here
    pass
```

### 2. Pin Your Versions

**Bad (vague):**
```python
# requirements.txt
flask
requests
```

**Better (pinned major versions):**
```python
flask>=2.3,<3.0  # Get patches, avoid breaking changes
requests>=2.31,<3.0
```

**Best (fully locked):**
```python
flask==2.3.0
requests==2.31.0
# (Generate with pip freeze)
```

### 3. Separate Dev and Production Dependencies

```python
# requirements.txt (production)
flask==2.3.0
psycopg2==2.9.5

# requirements-dev.txt (development only)
pytest==7.4.0
black==23.10.0
ipdb==0.13.13
```

**Why?** Fewer dependencies in production = smaller attack surface.

### 4. Regular Audits

```bash
# Weekly automated scan
devaudit scan --format json > audit-$(date +%Y-%m-%d).json

# Monthly manual review
pipdeptree
npm list
```

### 5. Use Virtual Environments

**Python:**
```bash
# Isolate project dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Node.js:**
```bash
# package.json automatically isolates in node_modules/
npm install
```

**Why?** Prevents dependency conflicts between projects.

### 6. Automate Dependency Updates

**Dependabot (GitHub):**
- Automatically opens PRs for dependency updates
- Runs your tests
- Safe, reviewable updates

**Renovate:**
- More configurable than Dependabot
- Supports more package managers

**Manual with CI:**
```yaml
# .github/workflows/dependencies.yml
name: Check Dependencies
on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for updates
        run: |
          pip list --outdated
          npm outdated
      - name: Security audit
        run: |
          pip install devaudit
          devaudit scan
```

---

## Understanding Version Specifiers

### Python (PEP 440)

```python
# Exact version
package==1.2.3

# Minimum version
package>=1.2.3

# Compatible version (same major version)
package~=1.2.3  # Equivalent to >=1.2.3,<2.0.0

# Version range
package>=1.2.0,<2.0.0

# Exclude specific version
package>=1.2.0,!=1.2.5,<2.0.0
```

### Node.js (semver)

```json
{
  "dependencies": {
    "express": "4.18.2",      // Exact
    "lodash": "^4.17.21",     // Compatible (4.x.x)
    "react": "~18.2.0",       // Patch only (18.2.x)
    "typescript": ">=5.0.0"   // Minimum
  }
}
```

**Caret (^):** Allow minor and patch updates
**Tilde (~):** Allow only patch updates

---

## Troubleshooting Dependency Issues

### Conflict: Incompatible Versions

**Problem:**
```
ERROR: package-a requires package-b>=2.0
       package-c requires package-b<2.0
```

**Solution:**
1. Check if updates available for package-a or package-c
2. If not, choose which to keep (or find alternatives)
3. Consider using Docker to isolate conflicting apps

### Broken After Update

**Problem:** Updated dependencies, app breaks

**Solution:**
```bash
# Rollback to previous versions
pip install package-name==old-version

# Or restore from requirements.txt backup
pip install -r requirements.txt.backup

# Fix the issue, then update incrementally
pip install package-name==next-version
# Test
# Repeat
```

### Huge Dependency Tree

**Problem:** `npm install` downloads 500 packages for simple app

**Solution:**
```bash
# Analyze what's pulling in dependencies
npm ls package-name

# Look for alternatives
# Check: https://bundlephobia.com/ (shows package sizes)

# Consider: Can you implement it yourself?
```

---

## Tools for Dependency Management

### Analysis Tools

**Python:**
- `pipdeptree` - Visualize dependency tree
- `pip-audit` - Find vulnerabilities (built into DevAudit)
- `safety` - Alternative vulnerability scanner

**Node.js:**
- `npm ls` - Built-in dependency tree
- `npm audit` - Built-in vulnerability scanner (built into DevAudit)
- `depcheck` - Find unused dependencies

### Update Tools

**Cross-platform:**
- **Dependabot** (GitHub) - Automated PRs
- **Renovate** - Configurable updates
- **DevAudit** - Scan + identify outdated packages

### Security Tools

- **Snyk** - Commercial security scanner
- **WhiteSource Bolt** - Open source security
- **DevAudit** - Free, privacy-first, local scanning

---

## Quick Reference

### Checking Dependencies

| Task | Python | Node.js |
|------|--------|---------|
| List all | `pip list` | `npm list` |
| Show tree | `pipdeptree` | `npm ls` |
| Check outdated | `pip list --outdated` | `npm outdated` |
| Find vulnerabilities | `pip-audit` | `npm audit` |
| Why installed? | `pipdeptree -r -p pkg` | `npm why pkg` |

### Updating Dependencies

| Task | Python | Node.js |
|------|--------|---------|
| Update one | `pip install -U pkg` | `npm update pkg` |
| Update all | `pip list --outdated` | `npm update` |
| Major updates | Manual | `npm install pkg@latest` |
| Fix vulnerabilities | Manual | `npm audit fix` |

### Best Practices Checklist

- [ ] Use virtual environments (Python) / package.json (Node)
- [ ] Pin versions in production
- [ ] Separate dev and production dependencies
- [ ] Run security audits weekly (`devaudit scan`)
- [ ] Keep dependencies minimal
- [ ] Review new dependencies before adding
- [ ] Automate updates with Dependabot/Renovate
- [ ] Test updates in staging before production
- [ ] Document why each dependency is needed

---

## Related Documentation

- [Understanding Security Vulnerabilities (CVEs)](cves.md)
- [Docker Security Best Practices](../guides/docker-security.md) *(coming soon)*
- [Setting Up Automated Scans](../guides/automated-scanning.md) *(coming soon)*

---

*Last updated: January 2025 (v0.2.x)*

*Found an error or have a suggestion? [Open an issue](https://github.com/aramantos/devaudit/issues) or [contribute](../../CONTRIBUTING.md)!*
