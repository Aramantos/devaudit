"""
Node.js/npm environment auditor.
"""

import re
import json
from typing import Dict, List, Optional
from .base import BaseAuditor
from devaudit.educational import get_educational_content


class NodeAuditor(BaseAuditor):
    """Audits Node.js and npm installations."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Node.js/npm"
        self.frameworks = ["express", "react", "vue", "angular", "next"]

    def is_installed(self) -> bool:
        """Check if npm is installed."""
        self.installed = self.check_command_exists("npm")
        return self.installed

    def get_version(self) -> Optional[str]:
        """Get npm version."""
        if not self.is_installed():
            return None

        stdout, _, rc = self.run_command(["npm", "--version"])
        if rc == 0 and stdout.strip():
            npm_version = stdout.strip()

            # Also get Node.js version
            stdout, _, rc = self.run_command(["node", "--version"])
            if rc == 0 and stdout.strip():
                node_version = stdout.strip()
                self.version = f"Node {node_version}, npm {npm_version}"
            else:
                self.version = f"npm {npm_version}"

            return self.version
        return None

    def audit(self) -> Dict:
        """Perform full Node.js/npm audit."""
        result = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "global_packages": [],
            "frameworks": {},
            "outdated_packages": [],
            "vulnerabilities": [],
            "cleanup_candidates": [],
            "warnings": [],
        }

        if not result["installed"]:
            return result

        # Get global packages
        stdout, _, rc = self.run_command(["npm", "list", "-g", "--depth=0", "--json"], timeout=60)
        if rc == 0 and stdout:
            try:
                data = json.loads(stdout)
                if "dependencies" in data:
                    for name, info in data["dependencies"].items():
                        result["global_packages"].append({
                            "name": name,
                            "version": info.get("version", "unknown"),
                        })
            except json.JSONDecodeError:
                # Fallback to text parsing
                stdout, _, rc = self.run_command(["npm", "list", "-g", "--depth=0"])
                if rc == 0:
                    packages = self._parse_npm_list(stdout)
                    result["global_packages"] = packages

        # Check for common frameworks
        for framework in self.frameworks:
            is_installed = any(pkg["name"] == framework for pkg in result["global_packages"])
            if is_installed:
                result["frameworks"][framework] = True

        # Get outdated global packages
        stdout, _, rc = self.run_command(["npm", "outdated", "-g", "--json"], timeout=60)
        if rc == 0 and stdout:
            try:
                outdated_data = json.loads(stdout)
                for name, info in outdated_data.items():
                    result["outdated_packages"].append({
                        "name": name,
                        "current": info.get("current", "unknown"),
                        "latest": info.get("latest", "unknown"),
                    })
            except json.JSONDecodeError:
                pass

        # Check for vulnerabilities using npm audit
        result["vulnerabilities"] = self._check_vulnerabilities()

        # Generate cleanup candidates
        if result["outdated_packages"]:
            result["cleanup_candidates"].append({
                "type": "outdated_packages",
                "count": len(result["outdated_packages"]),
                "description": f"{len(result['outdated_packages'])} outdated npm global packages",
            })

        if result["vulnerabilities"]:
            result["cleanup_candidates"].append({
                "type": "vulnerabilities",
                "count": len(result["vulnerabilities"]),
                "description": f"{len(result['vulnerabilities'])} vulnerable npm packages",
                "severity": "high",
            })

        # Project-specific audit (if target directory is specified)
        if self.target_dir:
            result["project_audit"] = self._audit_project()

        return result

    def _parse_npm_list(self, output: str) -> List[Dict]:
        """Parse npm list text output (fallback)."""
        packages = []
        lines = output.strip().split("\n")

        for line in lines:
            # Match patterns like: ├── package@version or └── package@version
            match = re.match(r'[├└─\s]+(.+)@(.+)', line)
            if match:
                packages.append({
                    "name": match.group(1),
                    "version": match.group(2),
                })

        return packages

    def _audit_project(self) -> Dict:
        """Audit a specific Node.js project directory."""
        project_data = {
            "has_package_json": False,
            "has_package_lock": False,
            "has_node_modules": False,
            "dependencies": {},
            "dev_dependencies": {},
            "scripts": {},
            "node_modules_count": 0,
        }

        # Check for package.json
        if self.check_file_exists("package.json"):
            project_data["has_package_json"] = True
            content = self.read_file("package.json")
            if content:
                try:
                    pkg_data = json.loads(content)
                    project_data["dependencies"] = pkg_data.get("dependencies", {})
                    project_data["dev_dependencies"] = pkg_data.get("devDependencies", {})
                    project_data["scripts"] = pkg_data.get("scripts", {})
                except json.JSONDecodeError:
                    pass

        # Check for package-lock.json
        if self.check_file_exists("package-lock.json"):
            project_data["has_package_lock"] = True

        # Check for node_modules directory
        node_modules_path = self.target_dir / "node_modules"
        if node_modules_path.exists() and node_modules_path.is_dir():
            project_data["has_node_modules"] = True
            try:
                # Count subdirectories (packages) in node_modules
                subdirs = [d for d in node_modules_path.iterdir() if d.is_dir()]
                project_data["node_modules_count"] = len(subdirs)
            except Exception:
                pass

        return project_data

    def _check_vulnerabilities(self) -> List[Dict]:
        """Check for vulnerabilities using npm audit."""
        vulnerabilities = []

        try:
            # Run npm audit with JSON output
            stdout, stderr, rc = self.run_command(
                ["npm", "audit", "--json"],
                timeout=60
            )

            if stdout:
                try:
                    data = json.loads(stdout)

                    # npm audit returns vulnerabilities grouped by severity
                    if "vulnerabilities" in data:
                        for pkg_name, vuln_data in data["vulnerabilities"].items():
                            # Extract severity and advisory information
                            severity = vuln_data.get("severity", "unknown")

                            # Get via information if available
                            via = vuln_data.get("via", [])
                            for item in via:
                                if isinstance(item, dict):
                                    vulnerabilities.append({
                                        "package": pkg_name,
                                        "version": vuln_data.get("range", "unknown"),
                                        "vulnerability_id": item.get("source", ""),
                                        "description": item.get("title", "")[:200],
                                        "severity": severity,
                                        "fixed_in": vuln_data.get("fixAvailable", {}).get("version", "N/A"),
                                    })
                                elif isinstance(item, str):
                                    # Sometimes via is just a string (package name)
                                    vulnerabilities.append({
                                        "package": pkg_name,
                                        "version": vuln_data.get("range", "unknown"),
                                        "vulnerability_id": "",
                                        "description": f"Vulnerability in {item}",
                                        "severity": severity,
                                        "fixed_in": vuln_data.get("fixAvailable", {}).get("version", "N/A") if isinstance(vuln_data.get("fixAvailable"), dict) else "N/A",
                                    })

                except json.JSONDecodeError:
                    pass

        except Exception:
            # Silently fail - vulnerability scanning is optional
            pass

        return vulnerabilities

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about Node.js packages and dependencies.

        Returns educational content from docs/concepts/dependencies.md.
        """
        return get_educational_content("dependencies", fallback={
            "what_is_it": "npm packages are reusable Node.js modules that provide functionality for your JavaScript projects.",
            "why_it_matters": "Outdated or vulnerable npm packages can expose your application to security risks, including supply chain attacks.",
            "when_to_update": "Update packages when you see security vulnerabilities or critical bug fixes. Check npm audit regularly.",
            "when_to_skip": "If your application works well and has no security issues, updates can be scheduled during maintenance windows.",
            "how_to_fix": "Run 'npm update' to update packages, or 'npm audit fix' to automatically fix security vulnerabilities.",
            "risks": "Package updates can introduce breaking changes. Always test in development before updating production dependencies.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/dependencies.md"
        })
