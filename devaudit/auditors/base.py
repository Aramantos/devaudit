"""
Base auditor class that all specific auditors inherit from.
"""

import subprocess
import shutil
import platform
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Literal
from abc import ABC, abstractmethod
from enum import Enum


class RiskLevel(str, Enum):
    """Risk levels for audit findings."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditorCategory(str, Enum):
    """Auditor categories."""
    PACKAGE = "package"  # Package managers (Python, Node, Docker, Go)
    SYSTEM = "system"    # System-level (BIOS, OS, drivers, disk, etc.)


class BaseAuditor(ABC):
    """
    Abstract base class for all auditors.

    Each auditor must implement:
        - name: The display name of the tool being audited
        - category: PACKAGE or SYSTEM
        - is_installed(): Check if the tool is installed
        - get_version(): Get the tool's version
        - audit(): Perform detailed audit

    New in v0.3.0:
        - get_educational_content(): Return educational content
        - assess_risk(): Assess risk level of findings
        - can_run(): Check if auditor can run (permissions, platform)
        - requires_elevation(): Check if needs admin/root
    """

    def __init__(self, target_dir: Optional[str] = None):
        self.name = "Unknown"
        self.category = AuditorCategory.PACKAGE
        self.installed = False
        self.version = None
        self.data = {}
        self.target_dir = Path(target_dir) if target_dir else None
        self.platform = platform.system()  # Windows, Darwin, Linux

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the tool is installed on the system."""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get the version of the installed tool."""
        pass

    @abstractmethod
    def audit(self) -> Dict:
        """
        Perform a detailed audit of the tool.

        Returns:
            Dict containing audit results with keys:
                - installed: bool
                - version: str or None
                - packages: List[Dict] (optional)
                - cleanup_candidates: List[Dict] (optional)
                - warnings: List[str] (optional)
                - educational_content: Dict (optional, v0.3.0+)
                - risk_level: str (optional, v0.3.0+)
        """
        pass

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about this auditor's findings.

        Returns:
            Dict with educational information:
                - what_is_it: Brief explanation
                - why_it_matters: Real-world impact
                - when_to_update: Guidance on urgency
                - when_to_skip: When it's safe to ignore
                - how_to_fix: Step-by-step instructions
                - risks: Risks of taking action
                - learn_more_url: Link to full docs
        """
        return {
            "what_is_it": f"{self.name} helps manage your development environment.",
            "why_it_matters": "Keeping tools updated improves security and stability.",
            "when_to_update": "Update when you see outdated packages or vulnerabilities.",
            "when_to_skip": "If everything is working well, updates can wait.",
            "how_to_fix": f"Use {self.name}'s built-in update commands.",
            "risks": "Updates may rarely introduce breaking changes.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/README.md"
        }

    def assess_risk(self, result: Dict) -> RiskLevel:
        """
        Assess risk level based on audit results.

        Args:
            result: The audit result dictionary

        Returns:
            RiskLevel enum value

        Override this in subclasses for specific risk logic.
        """
        # Default risk assessment logic
        if not result.get("installed"):
            return RiskLevel.NONE

        # Check for vulnerabilities
        vulnerabilities = result.get("vulnerabilities", [])
        if vulnerabilities:
            critical = sum(1 for v in vulnerabilities if v.get("severity") == "CRITICAL")
            high = sum(1 for v in vulnerabilities if v.get("severity") == "HIGH")
            if critical > 0:
                return RiskLevel.CRITICAL
            elif high > 0:
                return RiskLevel.HIGH
            elif vulnerabilities:
                return RiskLevel.MEDIUM

        # Check for outdated packages
        outdated = result.get("outdated_packages", [])
        if len(outdated) > 10:
            return RiskLevel.MEDIUM
        elif outdated:
            return RiskLevel.LOW

        return RiskLevel.LOW

    def can_run(self) -> bool:
        """
        Check if this auditor can run on the current system.

        Checks:
            - Platform compatibility
            - Required permissions
            - Dependencies available

        Returns:
            True if auditor can run, False otherwise
        """
        # Check platform
        if hasattr(self, "supported_platforms"):
            if self.platform not in self.supported_platforms:
                return False

        # Check if requires elevation but doesn't have it
        if self.requires_elevation() and not self.has_elevation():
            return False

        return True

    def requires_elevation(self) -> bool:
        """
        Check if this auditor requires admin/root privileges.

        Returns:
            True if elevation needed, False otherwise
        """
        return False

    def has_elevation(self) -> bool:
        """
        Check if running with admin/root privileges.

        Returns:
            True if elevated, False otherwise
        """
        if self.platform == "Windows":
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            # macOS and Linux
            return os.geteuid() == 0

    def get_platform_name(self) -> str:
        """Get friendly platform name."""
        platform_names = {
            "Windows": "Windows",
            "Darwin": "macOS",
            "Linux": "Linux"
        }
        return platform_names.get(self.platform, self.platform)

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run a shell command and return output.

        Args:
            cmd: Command to run as list of strings
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", -1
        except FileNotFoundError:
            return "", f"Command not found: {cmd[0]}", -1
        except Exception as e:
            return "", f"Error running command: {str(e)}", -1

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None

    def run_command_in_target(self, cmd: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run a command in the target directory if specified.

        Args:
            cmd: Command to run as list of strings
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.target_dir) if self.target_dir else None
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", -1
        except FileNotFoundError:
            return "", f"Command not found: {cmd[0]}", -1
        except Exception as e:
            return "", f"Error running command: {str(e)}", -1

    def check_file_exists(self, filename: str) -> bool:
        """Check if a file exists in the target directory."""
        if not self.target_dir:
            return False
        file_path = self.target_dir / filename
        return file_path.exists() and file_path.is_file()

    def read_file(self, filename: str) -> Optional[str]:
        """Read a file from the target directory."""
        if not self.target_dir:
            return None
        file_path = self.target_dir / filename
        try:
            return file_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            return None
