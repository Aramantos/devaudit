"""
Python environment auditor.
"""

import re
from typing import Dict, List, Optional
from .base import BaseAuditor
from devaudit.educational import get_educational_content


class PythonAuditor(BaseAuditor):
    """Audits Python installations and packages."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Python"
        self.python_commands = ["python", "python3", "py"]
        self.frameworks = ["Django", "Flask", "FastAPI", "Pyramid"]

    def is_installed(self) -> bool:
        """Check if Python is installed."""
        for cmd in self.python_commands:
            if self.check_command_exists(cmd):
                self.installed = True
                return True
        self.installed = False
        return False

    def get_version(self) -> Optional[str]:
        """Get Python version."""
        if not self.is_installed():
            return None

        for cmd in self.python_commands:
            if self.check_command_exists(cmd):
                stdout, _, rc = self.run_command([cmd, "--version"])
                if rc == 0 and stdout.strip():
                    self.version = stdout.strip()
                    return self.version
        return None

    def audit(self) -> Dict:
        """Perform full Python audit."""
        result = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "interpreters": [],
            "packages": [],
            "frameworks": {},
            "outdated_packages": [],
            "vulnerabilities": [],
            "cleanup_candidates": [],
            "warnings": [],
        }

        if not result["installed"]:
            return result

        # Audit each Python interpreter found
        for cmd in self.python_commands:
            if not self.check_command_exists(cmd):
                continue

            interpreter_data = self._audit_interpreter(cmd)
            if interpreter_data:
                result["interpreters"].append(interpreter_data)

                # Merge package lists (deduplicate)
                existing_packages = {pkg["name"] for pkg in result["packages"]}
                for pkg in interpreter_data.get("packages", []):
                    if pkg["name"] not in existing_packages:
                        result["packages"].append(pkg)
                        existing_packages.add(pkg["name"])

                # Track frameworks
                for fw, installed in interpreter_data.get("frameworks", {}).items():
                    if installed and fw not in result["frameworks"]:
                        result["frameworks"][fw] = installed

                # Merge outdated packages
                for pkg in interpreter_data.get("outdated", []):
                    if pkg not in result["outdated_packages"]:
                        result["outdated_packages"].append(pkg)

        # Check for vulnerabilities (uses pip-audit if available)
        result["vulnerabilities"] = self._check_vulnerabilities()

        # Generate cleanup candidates
        if result["outdated_packages"]:
            result["cleanup_candidates"].append({
                "type": "outdated_packages",
                "count": len(result["outdated_packages"]),
                "description": f"{len(result['outdated_packages'])} outdated Python packages",
            })

        if result["vulnerabilities"]:
            result["cleanup_candidates"].append({
                "type": "vulnerabilities",
                "count": len(result["vulnerabilities"]),
                "description": f"{len(result['vulnerabilities'])} vulnerable Python packages",
                "severity": "high",
            })

        # Project-specific audit (if target directory is specified)
        if self.target_dir:
            result["project_audit"] = self._audit_project()

        return result

    def _audit_interpreter(self, cmd: str) -> Optional[Dict]:
        """Audit a specific Python interpreter."""
        data = {
            "command": cmd,
            "packages": [],
            "frameworks": {},
            "outdated": [],
        }

        # Get package list
        stdout, stderr, rc = self.run_command([cmd, "-m", "pip", "list", "--format=columns"])
        if rc == 0 and stdout:
            packages = self._parse_pip_list(stdout)
            data["packages"] = packages

        # Check for frameworks
        for framework in self.frameworks:
            stdout, _, rc = self.run_command([cmd, "-m", "pip", "show", framework])
            data["frameworks"][framework] = (rc == 0 and stdout.strip() != "")

        # Get outdated packages
        stdout, _, rc = self.run_command([cmd, "-m", "pip", "list", "--outdated", "--format=columns"])
        if rc == 0 and stdout:
            outdated = self._parse_pip_outdated(stdout)
            data["outdated"] = outdated

        return data if data["packages"] else None

    def _parse_pip_list(self, output: str) -> List[Dict]:
        """Parse pip list output."""
        packages = []
        lines = output.strip().split("\n")

        # Skip header lines (usually first 2 lines)
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 2:
                packages.append({
                    "name": parts[0],
                    "version": parts[1],
                })

        return packages

    def _parse_pip_outdated(self, output: str) -> List[Dict]:
        """Parse pip list --outdated output."""
        outdated = []
        lines = output.strip().split("\n")

        # Skip header lines
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 3:
                outdated.append({
                    "name": parts[0],
                    "current": parts[1],
                    "latest": parts[2],
                })

        return outdated

    def _audit_project(self) -> Dict:
        """Audit a specific Python project directory."""
        project_data = {
            "has_requirements": False,
            "has_pyproject": False,
            "has_pipfile": False,
            "has_venv": False,
            "requirements": [],
            "venv_packages": [],
        }

        # Check for requirements.txt
        if self.check_file_exists("requirements.txt"):
            project_data["has_requirements"] = True
            content = self.read_file("requirements.txt")
            if content:
                project_data["requirements"] = self._parse_requirements(content)

        # Check for pyproject.toml
        if self.check_file_exists("pyproject.toml"):
            project_data["has_pyproject"] = True

        # Check for Pipfile
        if self.check_file_exists("Pipfile"):
            project_data["has_pipfile"] = True

        # Check for venv directory
        venv_paths = ["venv", ".venv", "env", "ENV"]
        for venv_name in venv_paths:
            venv_path = self.target_dir / venv_name
            if venv_path.exists() and venv_path.is_dir():
                project_data["has_venv"] = True
                project_data["venv_path"] = venv_name
                # Try to get packages from venv
                venv_packages = self._get_venv_packages(venv_name)
                if venv_packages:
                    project_data["venv_packages"] = venv_packages
                break

        return project_data

    def _parse_requirements(self, content: str) -> List[str]:
        """Parse requirements.txt content."""
        requirements = []
        for line in content.split("\n"):
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith("#"):
                # Extract package name (before ==, >=, etc.)
                pkg_name = re.split(r'[=<>!]', line)[0].strip()
                if pkg_name:
                    requirements.append(line)
        return requirements

    def _get_venv_packages(self, venv_name: str) -> List[Dict]:
        """Get packages from a virtual environment."""
        import platform

        # Determine pip path in venv
        if platform.system() == "Windows":
            pip_path = self.target_dir / venv_name / "Scripts" / "pip.exe"
        else:
            pip_path = self.target_dir / venv_name / "bin" / "pip"

        if not pip_path.exists():
            return []

        # Run pip list in the venv
        stdout, _, rc = self.run_command_in_target([str(pip_path), "list", "--format=columns"])
        if rc == 0 and stdout:
            return self._parse_pip_list(stdout)

        return []

    def _check_vulnerabilities(self) -> List[Dict]:
        """Check for known vulnerabilities using pip-audit if available."""
        vulnerabilities = []

        # Check if pip-audit is installed
        stdout, _, rc = self.run_command(["pip-audit", "--version"], timeout=5)
        if rc != 0:
            # pip-audit not installed, try to use Safety as fallback
            stdout, _, rc = self.run_command(["safety", "--version"], timeout=5)
            if rc != 0:
                # Neither tool available, return empty list
                return vulnerabilities

            # Use Safety
            return self._check_with_safety()

        # Use pip-audit
        return self._check_with_pip_audit()

    def _check_with_pip_audit(self) -> List[Dict]:
        """Check vulnerabilities using pip-audit."""
        import json

        vulnerabilities = []

        try:
            # Run pip-audit with JSON output
            stdout, stderr, rc = self.run_command(
                ["pip-audit", "--format=json", "--progress-spinner=off"],
                timeout=60
            )

            if rc == 0 and stdout:
                try:
                    data = json.loads(stdout)
                    # pip-audit format: {"dependencies": [...]}
                    for dep in data.get("dependencies", []):
                        for vuln in dep.get("vulns", []):
                            vulnerabilities.append({
                                "package": dep.get("name"),
                                "version": dep.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description", "")[:200],
                                "severity": self._map_cvss_to_severity(vuln.get("fix_versions", [])),
                                "fixed_in": vuln.get("fix_versions", []),
                            })
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            # Silently fail - vulnerability scanning is optional
            pass

        return vulnerabilities

    def _check_with_safety(self) -> List[Dict]:
        """Check vulnerabilities using Safety."""
        import json

        vulnerabilities = []

        try:
            # Run safety check with JSON output
            stdout, stderr, rc = self.run_command(
                ["safety", "check", "--json"],
                timeout=60
            )

            if stdout:
                try:
                    data = json.loads(stdout)
                    # Safety format is a list of vulnerabilities
                    for vuln in data:
                        vulnerabilities.append({
                            "package": vuln.get("package"),
                            "version": vuln.get("installed_version"),
                            "vulnerability_id": vuln.get("vulnerability_id"),
                            "description": vuln.get("advisory", "")[:200],
                            "severity": vuln.get("severity", "unknown"),
                            "fixed_in": vuln.get("fixed_versions", []),
                        })
                except json.JSONDecodeError:
                    pass

        except Exception:
            # Silently fail - vulnerability scanning is optional
            pass

        return vulnerabilities

    def _map_cvss_to_severity(self, fix_versions: List) -> str:
        """Map CVSS score or fix availability to severity."""
        if not fix_versions:
            return "unknown"
        # If there are fix versions available, it's at least medium severity
        return "medium"

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about Python packages and dependencies.

        Returns educational content from docs/concepts/dependencies.md and docs/concepts/cves.md.
        """
        # Primary content about dependencies
        return get_educational_content("dependencies", fallback={
            "what_is_it": "Python packages are reusable libraries that add functionality to your Python projects.",
            "why_it_matters": "Outdated or vulnerable packages can expose your application to security risks and bugs.",
            "when_to_update": "Update packages when you see security vulnerabilities (CVEs) or critical bug fixes.",
            "when_to_skip": "If everything works well and there are no security issues, updates can wait.",
            "how_to_fix": "Run 'pip install --upgrade package-name' to update specific packages, or 'pip list --outdated' to see all outdated packages.",
            "risks": "Package updates can introduce breaking changes. Always test in a development environment first.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/dependencies.md"
        })
