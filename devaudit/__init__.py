"""
DevAudit - Developer Environment Auditing Tool
=============================================

Cross-platform tool for auditing developer environments, tracking dependencies,
and identifying cleanup candidates.

Features:
    - Audit Python, Node.js, Go, Docker, and system packages
    - Generate timestamped reports (summary + detailed)
    - Identify outdated packages and cleanup candidates
    - Fix common Docker Desktop issues
    - Beautiful terminal output with Rich

Quick Start:
    devaudit scan              # Full system audit
    devaudit scan --python     # Only Python audit
    devaudit fix-docker        # Fix Docker Desktop UI

Author: John Doyle
Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "John Doyle"
__all__ = []
