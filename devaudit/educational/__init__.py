"""
Educational content system for DevAudit.

Provides educational content to auditors and users explaining:
- What security issues are
- Why they matter
- When to take action
- How to fix them
- Risks involved

Content can be provided inline (code) or loaded from markdown files.
"""

from .content_loader import EducationalContentLoader, get_educational_content

__all__ = [
    "EducationalContentLoader",
    "get_educational_content",
]
