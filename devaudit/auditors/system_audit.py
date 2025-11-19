"""
System-level auditor for Git and other development tools.
"""

import platform
from typing import Dict, List, Optional
from .base import BaseAuditor
from devaudit.educational import get_educational_content


class SystemAuditor(BaseAuditor):
    """Audits system-level development tools."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "System"
        self.tools = {
            "Git": "git",
            "Docker Compose": "docker-compose",
            "Kubectl": "kubectl",
            "Terraform": "terraform",
            "AWS CLI": "aws",
            "Azure CLI": "az",
            "gcloud": "gcloud",
        }

    def is_installed(self) -> bool:
        """Always returns True as this audits system-level tools."""
        self.installed = True
        return True

    def get_version(self) -> Optional[str]:
        """Returns OS information."""
        self.version = f"{platform.system()} {platform.release()}"
        return self.version

    def audit(self) -> Dict:
        """Perform system audit."""
        result = {
            "installed": True,
            "version": self.get_version(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "tools": {},
            "warnings": [],
        }

        # Check for each development tool
        for tool_name, command in self.tools.items():
            tool_info = {"installed": False, "version": None}

            if self.check_command_exists(command):
                tool_info["installed"] = True

                # Try to get version
                version = self._get_tool_version(command)
                if version:
                    tool_info["version"] = version

            result["tools"][tool_name] = tool_info

        # Windows-specific: Get installed programs (if on Windows)
        if platform.system() == "Windows":
            result["windows_programs"] = self._get_windows_programs()

        return result

    def _get_tool_version(self, command: str) -> Optional[str]:
        """Get version for a specific tool."""
        version_args = {
            "git": ["--version"],
            "docker-compose": ["--version"],
            "kubectl": ["version", "--client", "--short"],
            "terraform": ["--version"],
            "aws": ["--version"],
            "az": ["--version"],
            "gcloud": ["--version"],
        }

        args = version_args.get(command, ["--version"])
        stdout, _, rc = self.run_command([command] + args, timeout=10)

        if rc == 0 and stdout:
            # Return first line for most tools
            first_line = stdout.strip().split("\n")[0]
            return first_line

        return None

    def _get_windows_programs(self) -> List[Dict]:
        """Get installed Windows programs (Windows only)."""
        programs = []

        if platform.system() != "Windows":
            return programs

        try:
            import winreg

            # Registry paths for installed programs
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]

            for hkey, path in registry_paths:
                try:
                    key = winreg.OpenKey(hkey, path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)

                            display_name = None
                            version = None
                            publisher = None

                            try:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            except:
                                pass

                            try:
                                version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                            except:
                                pass

                            try:
                                publisher, _ = winreg.QueryValueEx(subkey, "Publisher")
                            except:
                                pass

                            if display_name:
                                programs.append({
                                    "name": display_name,
                                    "version": version or "Unknown",
                                    "publisher": publisher or "Unknown",
                                })

                            winreg.CloseKey(subkey)
                        except:
                            continue

                    winreg.CloseKey(key)
                except:
                    continue

        except ImportError:
            # winreg not available (not Windows)
            pass
        except Exception as e:
            pass

        # Sort by name
        programs.sort(key=lambda x: x["name"].lower())

        return programs

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about system development tools.

        For system tools (Git, kubectl, etc.), we provide general guidance.
        """
        return {
            "what_is_it": "Development tools like Git, Docker Compose, kubectl, and cloud CLIs that support your development workflow.",
            "why_it_matters": "Keeping development tools updated ensures you have the latest features, security patches, and bug fixes.",
            "when_to_update": "Update tools when new features are needed or security vulnerabilities are announced.",
            "when_to_skip": "If tools are working correctly and you don't need new features, updates can wait.",
            "how_to_fix": "Update tools using your system's package manager (brew, apt, choco, etc.) or download from official websites.",
            "risks": "Tool updates can change behavior or introduce breaking changes. Always check release notes before updating.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/README.md"
        }
