"""
Go environment auditor.
"""

from typing import Dict, List, Optional
from .base import BaseAuditor
from devaudit.educational import get_educational_content


class GoAuditor(BaseAuditor):
    """Audits Go installations and modules."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Go"

    def is_installed(self) -> bool:
        """Check if Go is installed."""
        self.installed = self.check_command_exists("go")
        return self.installed

    def get_version(self) -> Optional[str]:
        """Get Go version."""
        if not self.is_installed():
            return None

        stdout, _, rc = self.run_command(["go", "version"])
        if rc == 0 and stdout.strip():
            self.version = stdout.strip()
            return self.version
        return None

    def audit(self) -> Dict:
        """Perform full Go audit."""
        result = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "modules": [],
            "module_cache_path": None,
            "cleanup_candidates": [],
            "warnings": [],
        }

        if not result["installed"]:
            return result

        # Get module cache path
        stdout, _, rc = self.run_command(["go", "env", "GOMODCACHE"])
        if rc == 0 and stdout.strip():
            result["module_cache_path"] = stdout.strip()

        # If target directory specified, use it for module listing
        if self.target_dir:
            # Try to list modules in target directory
            stdout, stderr, rc = self.run_command_in_target(["go", "list", "-m", "all"])
            if rc == 0 and stdout:
                modules = []
                for line in stdout.strip().split("\n"):
                    if line:
                        modules.append(line.strip())
                result["modules"] = modules
            elif "go.mod" in stderr:
                result["warnings"].append("Not inside a Go module (go.mod not found)")

            # Add project-specific audit
            result["project_audit"] = self._audit_project()
        else:
            # Try to list modules (only works inside a Go module)
            stdout, stderr, rc = self.run_command(["go", "list", "-m", "all"])
            if rc == 0 and stdout:
                modules = []
                for line in stdout.strip().split("\n"):
                    if line:
                        modules.append(line.strip())
                result["modules"] = modules
            elif "go.mod" in stderr:
                result["warnings"].append("Not inside a Go module (go.mod not found)")

        return result

    def _audit_project(self) -> Dict:
        """Audit a specific Go project directory."""
        project_data = {
            "has_go_mod": False,
            "has_go_sum": False,
            "module_name": None,
            "go_version": None,
        }

        # Check for go.mod
        if self.check_file_exists("go.mod"):
            project_data["has_go_mod"] = True
            content = self.read_file("go.mod")
            if content:
                # Parse module name and Go version
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("module "):
                        project_data["module_name"] = line.replace("module ", "").strip()
                    elif line.startswith("go "):
                        project_data["go_version"] = line.replace("go ", "").strip()

        # Check for go.sum
        if self.check_file_exists("go.sum"):
            project_data["has_go_sum"] = True

        return project_data

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about Go modules and dependencies.

        Returns educational content from docs/concepts/dependencies.md.
        """
        return get_educational_content("dependencies", fallback={
            "what_is_it": "Go modules are packages that provide reusable code for your Go projects.",
            "why_it_matters": "Outdated or vulnerable modules can expose your application to security risks and bugs.",
            "when_to_update": "Update modules when security vulnerabilities are discovered or when you need new features.",
            "when_to_skip": "If your application works correctly and has no security issues, updates can be scheduled.",
            "how_to_fix": "Run 'go get -u' to update modules, or 'go mod tidy' to clean up unused dependencies.",
            "risks": "Module updates can introduce breaking changes. Always test thoroughly before deploying updates.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/dependencies.md"
        })
