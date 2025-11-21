"""
Python Virtual Environment Auditor.

Scans the entire system for Python environments and provides comprehensive
package tracking across global, local venvs, Poetry, and Conda environments.
"""

import os
import platform
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from .base import BaseAuditor


class PythonVenvAuditor(BaseAuditor):
    """Audits all Python virtual environments on the system."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Python Environments"
        self.python_commands = ["python", "python3", "py"]

    def is_installed(self) -> bool:
        """Check if Python is installed."""
        for cmd in self.python_commands:
            if self.check_command_exists(cmd):
                return True
        return False

    def get_version(self) -> Optional[str]:
        """Get Python version."""
        if not self.is_installed():
            return None

        for cmd in self.python_commands:
            if self.check_command_exists(cmd):
                stdout, _, rc = self.run_command([cmd, "--version"])
                if rc == 0 and stdout.strip():
                    return stdout.strip()
        return None

    def audit(self) -> Dict:
        """
        Perform comprehensive Python environment audit.

        Returns:
            Dict containing:
                - installed: bool
                - version: str (Python version)
                - environments: List[Dict] (all detected environments)
                - global_packages: List[Dict]
                - total_packages: int
                - duplicate_packages: List[Dict] (packages in multiple envs)
                - orphaned_global: List[str] (global packages also in venvs)
                - recommendations: List[str]
        """
        result = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "environments": [],
            "global_packages": [],
            "total_packages": 0,
            "duplicate_packages": [],
            "orphaned_global": [],
            "recommendations": [],
            "warnings": []
        }

        if not result["installed"]:
            return result

        # 1. Scan global Python packages
        global_env = self._scan_global_environment()
        if global_env:
            result["environments"].append(global_env)
            result["global_packages"] = global_env.get("packages", [])

        # 2. Scan for local venvs in common project locations
        local_venvs = self._scan_local_venvs()
        result["environments"].extend(local_venvs)

        # 3. Scan Poetry environments
        poetry_venvs = self._scan_poetry_environments()
        result["environments"].extend(poetry_venvs)

        # 4. Scan Conda environments
        conda_venvs = self._scan_conda_environments()
        result["environments"].extend(conda_venvs)

        # Calculate statistics
        result["total_packages"] = sum(
            len(env.get("packages", [])) for env in result["environments"]
        )

        # Analyze package distribution
        result["duplicate_packages"] = self._find_duplicate_packages(result["environments"])
        result["orphaned_global"] = self._find_orphaned_global(result["environments"])
        result["recommendations"] = self._generate_recommendations(result)

        return result

    def _scan_global_environment(self) -> Optional[Dict]:
        """Scan global Python environment (user-installed packages)."""
        for cmd in self.python_commands:
            if not self.check_command_exists(cmd):
                continue

            # Get global packages (user site-packages)
            stdout, _, rc = self.run_command([cmd, "-m", "pip", "list", "--user", "--format=json"], timeout=30)
            if rc == 0 and stdout.strip():
                try:
                    import json
                    packages_raw = json.loads(stdout)
                    packages = [
                        {"name": pkg["name"], "version": pkg["version"]}
                        for pkg in packages_raw
                    ]

                    return {
                        "name": "Global (System)",
                        "type": "global",
                        "path": self._get_user_site_packages_path(cmd),
                        "packages": packages,
                        "package_count": len(packages),
                        "python_version": self.get_version()
                    }
                except Exception as e:
                    self.warnings.append(f"Failed to parse global packages: {e}")

        return None

    def _get_user_site_packages_path(self, cmd: str) -> str:
        """Get the user site-packages directory path."""
        stdout, _, rc = self.run_command(
            [cmd, "-m", "site", "--user-site"],
            timeout=10
        )
        if rc == 0 and stdout.strip():
            return stdout.strip()
        return "Unknown"

    def _scan_local_venvs(self) -> List[Dict]:
        """
        Scan for local virtual environments in common project directories.

        Searches in:
        - User's home directory dev folders
        - Current working directory
        - Common project paths
        - Entire drives (with depth limits for performance)
        """
        venvs = []
        search_roots = []

        # Common development directories
        home = Path.home()
        common_dev_dirs = [
            home / "dev",
            home / "dev_files",
            home / "projects",
            home / "code",
            home / "repos",
            home / "work",
            home / "workspace",
            home / "Documents" / "GitHub",
            home / "Documents" / "projects",
            home / "Documents" / "dev",
            home / "Desktop" / "projects",
            home / "Desktop" / "Software Development",  # Added
            home / "OneDrive" / "projects",
            home / "OneDrive" / "Desktop",  # Added
            home / "iCloudDrive" / "Desktop",  # Added - iCloud
            home / "iCloudDrive" / "Desktop" / "Software Development",  # Added - iCloud dev folder
            home / "iCloudDrive" / "Documents",  # Added - iCloud
            home / "Dropbox",  # Added - Dropbox
            home / "Google Drive",  # Added - Google Drive
        ]

        for dev_dir in common_dev_dirs:
            if dev_dir.exists() and dev_dir.is_dir():
                search_roots.append(dev_dir)

        # Also add current working directory
        search_roots.append(Path.cwd())

        # Check for custom search paths from config
        custom_paths = self._load_custom_search_paths()
        for custom_path in custom_paths:
            if custom_path.exists() and custom_path.is_dir():
                search_roots.append(custom_path)

        # Scan each root for projects with venvs (up to 4 levels deep)
        # Include common venv directory names
        venv_names = [
            "venv", ".venv", "env", "ENV", ".env",
            "virtualenv", ".virtualenv", "venv_local",
            "python-env", "py-env", "pyenv"
        ]

        # Track found venvs to avoid duplicates
        found_venv_paths = set()

        for root in search_roots:
            try:
                venvs_in_root = self._scan_directory_recursive(
                    root,
                    venv_names,
                    found_venv_paths,
                    max_depth=4,  # Increased to 4 to find nested venvs
                    current_depth=0
                )
                venvs.extend(venvs_in_root)

            except (PermissionError, OSError):
                # Skip directories we can't access
                continue

        return venvs

    def _load_custom_search_paths(self) -> List[Path]:
        """Load custom search paths from config file."""
        config_file = Path.home() / ".devaudit" / "venv_search_paths.txt"

        if not config_file.exists():
            return []

        try:
            paths = []
            content = config_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    path = Path(line)
                    if path.exists():
                        paths.append(path)
            return paths
        except Exception:
            return []

    def _scan_directory_recursive(
        self,
        directory: Path,
        venv_names: List[str],
        found_venv_paths: Set[str],
        max_depth: int = 3,
        current_depth: int = 0
    ) -> List[Dict]:
        """
        Recursively scan a directory for venvs up to max_depth.

        Args:
            directory: Directory to scan
            venv_names: Names of venv directories to look for
            found_venv_paths: Set of already-found venv paths (to avoid duplicates)
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth

        Returns:
            List of venv data dictionaries
        """
        venvs = []

        # Stop if we've reached max depth
        if current_depth > max_depth:
            return venvs

        # Skip common non-project directories to speed up scan
        skip_dirs = {
            'node_modules', '__pycache__', '.git', '.svn', 'build', 'dist',
            'target', 'bin', 'obj', '.tox', '.pytest_cache', '.mypy_cache',
            'site-packages', 'Lib', 'Include', 'Scripts', 'Library',
            'AppData', 'Application Data', 'ProgramData', 'Program Files',
            'Windows', 'System32', '$Recycle.Bin', 'Recovery',
        }

        try:
            for item in directory.iterdir():
                # Skip hidden files/dirs (except .venv)
                if item.name.startswith('.') and item.name not in venv_names:
                    continue

                # Skip non-directories
                if not item.is_dir():
                    continue

                # Skip known non-project directories
                if item.name in skip_dirs:
                    continue

                # Check if this is a venv directory
                if item.name in venv_names:
                    # Verify it's actually a venv (has Scripts/pip or bin/pip)
                    if self._is_valid_venv(item):
                        venv_path_str = str(item.resolve())

                        # Skip if already found
                        if venv_path_str in found_venv_paths:
                            continue

                        found_venv_paths.add(venv_path_str)

                        # Get project name from parent directory
                        project_name = item.parent.name

                        venv_data = self._scan_venv_directory(
                            item,
                            project_name=project_name,
                            venv_type="local"
                        )
                        if venv_data:
                            venvs.append(venv_data)
                    continue  # Don't recurse into venv directories

                # Recurse into subdirectories
                try:
                    sub_venvs = self._scan_directory_recursive(
                        item,
                        venv_names,
                        found_venv_paths,
                        max_depth,
                        current_depth + 1
                    )
                    venvs.extend(sub_venvs)
                except (PermissionError, OSError):
                    # Skip directories we can't access
                    continue

        except (PermissionError, OSError):
            # Can't access this directory
            pass

        return venvs

    def _is_valid_venv(self, venv_path: Path) -> bool:
        """
        Check if a directory is actually a Python venv.

        Uses multiple indicators for reliability:
        1. pyvenv.cfg file (universal indicator)
        2. Scripts/pip.exe or bin/pip (platform-specific)
        3. Scripts/python.exe or bin/python (platform-specific)
        """
        # Check for pyvenv.cfg (most reliable indicator)
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        if pyvenv_cfg.exists():
            return True

        # Check for platform-specific executables
        if platform.system() == "Windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"

        return pip_path.exists() or python_path.exists()

    def _scan_venv_directory(
        self,
        venv_path: Path,
        project_name: str,
        venv_type: str = "local"
    ) -> Optional[Dict]:
        """Scan a specific virtual environment directory."""
        # Check both Windows (Scripts/) and Unix (bin/) locations
        # This handles cross-platform synced venvs (e.g., Mac venvs in iCloud on Windows)
        pip_path = None
        python_path = None

        # Try Windows paths first
        scripts_pip = venv_path / "Scripts" / "pip.exe"
        scripts_python = venv_path / "Scripts" / "python.exe"

        if scripts_pip.exists():
            pip_path = scripts_pip
            python_path = scripts_python

        # Try Unix paths if Windows paths don't exist
        if pip_path is None:
            bin_pip = venv_path / "bin" / "pip"
            bin_python = venv_path / "bin" / "python"

            if bin_pip.exists():
                pip_path = bin_pip
                python_path = bin_python

        # Check if this is a cross-platform venv (Unix venv on Windows or vice versa)
        is_cross_platform = False
        if pip_path and not str(pip_path).endswith('.exe'):
            # Unix-style venv on Windows - pip is a shell script, not executable
            if platform.system() == "Windows":
                is_cross_platform = True

        if pip_path is None:
            return None

        # If cross-platform, return basic info without scanning packages
        if is_cross_platform:
            return {
                "name": f"{project_name}/{venv_path.name}",
                "type": "cross-platform",
                "path": str(venv_path),
                "packages": [],
                "package_count": 0,
                "python_version": "Cross-platform (not executable on this OS)",
                "has_requirements": False,
                "requirements_packages": [],
                "warning": f"This appears to be a {'Unix' if platform.system() == 'Windows' else 'Windows'}-style venv that cannot be executed on {platform.system()}"
            }

        # Get packages from this venv
        stdout, _, rc = self.run_command(
            [str(pip_path), "list", "--format=json"],
            timeout=30
        )

        if rc != 0 or not stdout.strip():
            # Venv exists but pip failed or returned no packages
            # Still report it but mark as empty/broken
            return {
                "name": f"{project_name}/{venv_path.name}",
                "type": venv_type,
                "path": str(venv_path),
                "packages": [],
                "package_count": 0,
                "python_version": "Unknown",
                "has_requirements": False,
                "requirements_packages": [],
                "warning": "Unable to scan packages (pip may be broken or venv is empty)"
            }

        try:
            import json
            packages_raw = json.loads(stdout)
            packages = [
                {"name": pkg["name"], "version": pkg["version"]}
                for pkg in packages_raw
            ]

            # Try to get Python version for this venv
            python_version = "Unknown"
            if python_path.exists():
                stdout, _, rc = self.run_command([str(python_path), "--version"], timeout=10)
                if rc == 0 and stdout.strip():
                    python_version = stdout.strip()

            # Check for requirements.txt
            requirements_file = venv_path.parent / "requirements.txt"
            has_requirements = requirements_file.exists()
            requirements_packages = []

            if has_requirements:
                try:
                    content = requirements_file.read_text(encoding='utf-8')
                    requirements_packages = self._parse_requirements(content)
                except Exception:
                    pass

            return {
                "name": f"{project_name}/{venv_path.name}",
                "type": venv_type,
                "path": str(venv_path),
                "packages": packages,
                "package_count": len(packages),
                "python_version": python_version,
                "has_requirements": has_requirements,
                "requirements_packages": requirements_packages,
            }

        except Exception as e:
            return None

    def _parse_requirements(self, content: str) -> List[str]:
        """Parse requirements.txt and extract package names."""
        packages = []
        for line in content.split("\n"):
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith("#"):
                # Extract package name (before ==, >=, etc.)
                pkg_name = re.split(r'[=<>!]', line)[0].strip()
                if pkg_name:
                    packages.append(pkg_name)
        return packages

    def _scan_poetry_environments(self) -> List[Dict]:
        """Scan Poetry virtual environments."""
        venvs = []

        # Check if Poetry is installed
        if not self.check_command_exists("poetry"):
            return venvs

        try:
            # Get Poetry cache directory
            stdout, _, rc = self.run_command(
                ["poetry", "config", "virtualenvs.path"],
                timeout=10
            )

            if rc != 0 or not stdout.strip():
                # Default Poetry venv location
                if platform.system() == "Windows":
                    poetry_cache = Path.home() / "AppData" / "Local" / "pypoetry" / "Cache" / "virtualenvs"
                else:
                    poetry_cache = Path.home() / ".cache" / "pypoetry" / "virtualenvs"
            else:
                poetry_cache = Path(stdout.strip())

            if not poetry_cache.exists():
                return venvs

            # Scan each Poetry venv
            for venv_dir in poetry_cache.iterdir():
                if venv_dir.is_dir():
                    # Extract project name from Poetry venv name (format: project-name-hash-py3.x)
                    project_name = venv_dir.name.rsplit('-', 2)[0] if '-' in venv_dir.name else venv_dir.name

                    venv_data = self._scan_venv_directory(
                        venv_dir,
                        project_name=f"{project_name} (Poetry)",
                        venv_type="poetry"
                    )
                    if venv_data:
                        venvs.append(venv_data)

        except Exception as e:
            self.warnings.append(f"Failed to scan Poetry environments: {e}")

        return venvs

    def _scan_conda_environments(self) -> List[Dict]:
        """Scan Conda virtual environments."""
        venvs = []

        # Check if Conda is installed
        if not self.check_command_exists("conda"):
            return venvs

        try:
            # Get list of Conda environments
            stdout, _, rc = self.run_command(
                ["conda", "env", "list", "--json"],
                timeout=30
            )

            if rc != 0 or not stdout.strip():
                return venvs

            import json
            conda_data = json.loads(stdout)
            env_paths = conda_data.get("envs", [])

            for env_path in env_paths:
                env_path = Path(env_path)
                env_name = env_path.name

                # Skip base environment (usually huge and system-managed)
                if env_name == "base" or "miniconda" in str(env_path).lower():
                    continue

                # Get packages in this Conda env
                stdout, _, rc = self.run_command(
                    ["conda", "list", "-n", env_name, "--json"],
                    timeout=30
                )

                if rc == 0 and stdout.strip():
                    packages_raw = json.loads(stdout)
                    packages = [
                        {"name": pkg["name"], "version": pkg["version"]}
                        for pkg in packages_raw
                    ]

                    venvs.append({
                        "name": f"{env_name} (Conda)",
                        "type": "conda",
                        "path": str(env_path),
                        "packages": packages,
                        "package_count": len(packages),
                        "python_version": "Conda managed"
                    })

        except Exception as e:
            self.warnings.append(f"Failed to scan Conda environments: {e}")

        return venvs

    def _find_duplicate_packages(self, environments: List[Dict]) -> List[Dict]:
        """Find packages that exist in multiple environments."""
        # Track package names and which environments they appear in
        package_locations: Dict[str, List[str]] = {}

        for env in environments:
            env_name = env.get("name", "Unknown")
            for pkg in env.get("packages", []):
                pkg_name = pkg["name"]
                if pkg_name not in package_locations:
                    package_locations[pkg_name] = []
                package_locations[pkg_name].append(env_name)

        # Find packages in 2+ environments
        duplicates = []
        for pkg_name, locations in package_locations.items():
            if len(locations) > 1:
                duplicates.append({
                    "name": pkg_name,
                    "count": len(locations),
                    "environments": locations
                })

        # Sort by most duplicated
        duplicates.sort(key=lambda x: x["count"], reverse=True)
        return duplicates[:20]  # Top 20 duplicates

    def _find_orphaned_global(self, environments: List[Dict]) -> List[str]:
        """Find global packages that are also installed in venvs (potentially redundant)."""
        global_env = next((env for env in environments if env.get("type") == "global"), None)
        if not global_env:
            return []

        global_packages = {pkg["name"] for pkg in global_env.get("packages", [])}
        venv_packages: Set[str] = set()

        # Collect all packages from venvs
        for env in environments:
            if env.get("type") != "global":
                venv_packages.update(pkg["name"] for pkg in env.get("packages", []))

        # Find global packages also in venvs
        orphaned = list(global_packages & venv_packages)
        return sorted(orphaned)[:15]  # Top 15

    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate smart recommendations based on the scan."""
        recommendations = []

        global_count = len(result.get("global_packages", []))
        env_count = len([e for e in result.get("environments", []) if e.get("type") != "global"])
        orphaned_count = len(result.get("orphaned_global", []))
        duplicate_count = len(result.get("duplicate_packages", []))

        # Recommendation: Clean up global packages
        if orphaned_count > 5:
            global_after_cleanup = global_count - orphaned_count
            recommendations.append(
                f"You have {global_count} global packages. {orphaned_count} are also installed in venvs. "
                f"Removing them would reduce your global packages to {global_after_cleanup}, "
                "keeping your system clean and avoiding version conflicts."
            )

        # Recommendation: Use venvs consistently
        if global_count > 20 and env_count == 0:
            recommendations.append(
                f"You have {global_count} global packages but no virtual environments detected. "
                "Consider using venvs to isolate project dependencies."
            )

        # Recommendation: Reduce duplicates
        if duplicate_count > 10:
            recommendations.append(
                f"Found {duplicate_count} packages duplicated across environments. "
                "Consider consolidating common dependencies or removing unused venvs."
            )

        # Recommendation: Missing requirements.txt
        missing_reqs = [
            env["name"] for env in result.get("environments", [])
            if env.get("type") == "local" and not env.get("has_requirements")
        ]
        if missing_reqs:
            recommendations.append(
                f"{len(missing_reqs)} virtual environment(s) missing requirements.txt: {', '.join(missing_reqs[:3])}. "
                "Run 'pip freeze > requirements.txt' to track dependencies."
            )

        if not recommendations:
            recommendations.append("Your Python environment management looks good! All environments are well-organized.")

        return recommendations
