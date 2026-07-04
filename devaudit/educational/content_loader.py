"""
Educational content loader for DevAudit.

Loads educational content from:
1. Inline content (provided directly by auditors)
2. Markdown files in docs/concepts/
3. Cached content (for performance)

Usage:
    from devaudit.educational import get_educational_content

    # Get content for a specific topic
    content = get_educational_content("cves")

    # Returns dict with keys:
    #   - what_is_it
    #   - why_it_matters
    #   - when_to_update
    #   - when_to_skip
    #   - how_to_fix
    #   - risks
    #   - learn_more_url
"""

import os
from pathlib import Path
from typing import Dict, Optional
import re


class EducationalContentLoader:
    """Loader for educational content from markdown files."""

    def __init__(self, docs_path: Optional[Path] = None):
        """
        Initialize the content loader.

        Args:
            docs_path: Path to docs/concepts directory. If None, auto-detects.
        """
        if docs_path is None:
            current_file = Path(__file__).resolve()
            # Package-internal copy first (ships in the wheel via
            # scripts/prepare_package_assets.py), repo docs/concepts second
            # (source checkout where the copy step hasn't run).
            packaged = current_file.parent / "content"
            if packaged.is_dir():
                docs_path = packaged
            else:
                project_root = current_file.parent.parent.parent
                docs_path = project_root / "docs" / "concepts"

        self.docs_path = Path(docs_path)
        self._cache: Dict[str, Dict[str, str]] = {}

    def load_markdown_content(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Load educational content from a markdown file.

        Args:
            topic: Topic name (e.g., "cves", "dependencies", "docker-cleanup")

        Returns:
            Dict with educational content sections, or None if not found
        """
        # Check cache first
        if topic in self._cache:
            return self._cache[topic]

        # Try to find the markdown file
        markdown_file = self.docs_path / f"{topic}.md"
        if not markdown_file.exists():
            # Try with underscore instead of hyphen
            markdown_file = self.docs_path / f"{topic.replace('-', '_')}.md"
            if not markdown_file.exists():
                return None

        # Read and parse the markdown file
        try:
            content = markdown_file.read_text(encoding='utf-8', errors='replace')
            parsed = self._parse_markdown(content, topic)
            self._cache[topic] = parsed
            return parsed
        except Exception as e:
            print(f"Error loading educational content for {topic}: {e}")
            return None

    def _parse_markdown(self, content: str, topic: str) -> Dict[str, str]:
        """
        Parse markdown content into structured educational content.

        This is a simple parser that extracts key sections.
        For more sophisticated parsing, we could use a markdown library.

        Args:
            content: Markdown file content
            topic: Topic name for URL generation

        Returns:
            Dict with educational content sections
        """
        # Extract first paragraph after title as "what_is_it"
        what_is_it_match = re.search(r'^#[^\n]+\n\n([^\n]+(?:\n(?!#)[^\n]+)*)', content, re.MULTILINE)
        what_is_it = what_is_it_match.group(1).strip() if what_is_it_match else f"Learn about {topic}."

        # Extract "Why ... Matter" or "Real-World Impact" section
        why_matches = re.findall(
            r'##\s+(?:Why.*?Matter|Real-World Impact|Why It Matters)[^\n]*\n\n((?:[^\n]+\n)*?)(?=\n##|\Z)',
            content,
            re.MULTILINE | re.IGNORECASE
        )
        why_it_matters = why_matches[0].strip() if why_matches else "Understanding this helps keep your system secure."

        # Extract "When to Update" or similar section
        when_update_matches = re.findall(
            r'##\s+When to (?:Update|Act)[^\n]*\n\n((?:[^\n]+\n)*?)(?=\n##|\Z)',
            content,
            re.MULTILINE | re.IGNORECASE
        )
        when_to_update = when_update_matches[0].strip() if when_update_matches else "Update when you see security issues or vulnerabilities."

        # Extract "When to Skip" or similar section
        when_skip_matches = re.findall(
            r'##\s+When to Skip[^\n]*\n\n((?:[^\n]+\n)*?)(?=\n##|\Z)',
            content,
            re.MULTILINE | re.IGNORECASE
        )
        when_to_skip = when_skip_matches[0].strip() if when_skip_matches else "If everything is working well and there are no security concerns."

        # Extract "How to" or "Safe Cleanup" section
        how_to_matches = re.findall(
            r'##\s+(?:How to|Safe.*?:|What To Do)[^\n]*\n\n((?:[^\n]+\n)*?)(?=\n##|\Z)',
            content,
            re.MULTILINE | re.IGNORECASE
        )
        how_to_fix = how_to_matches[0].strip() if how_to_matches else "Follow the recommended steps in the documentation."

        # Extract risks or warnings
        risks_matches = re.findall(
            r'##\s+(?:Risks?|Warnings?|What.*?Risky)[^\n]*\n\n((?:[^\n]+\n)*?)(?=\n##|\Z)',
            content,
            re.MULTILINE | re.IGNORECASE
        )
        risks = risks_matches[0].strip() if risks_matches else "Follow instructions carefully to avoid issues."

        # Generate learn more URL
        learn_more_url = f"https://github.com/aramantos/devaudit/blob/main/docs/concepts/{topic}.md"

        return {
            "what_is_it": self._clean_text(what_is_it),
            "why_it_matters": self._clean_text(why_it_matters),
            "when_to_update": self._clean_text(when_to_update),
            "when_to_skip": self._clean_text(when_to_skip),
            "how_to_fix": self._clean_text(how_to_fix),
            "risks": self._clean_text(risks),
            "learn_more_url": learn_more_url
        }

    def _clean_text(self, text: str) -> str:
        """
        Clean markdown text for display.

        Removes excessive markdown formatting while preserving readability.

        Args:
            text: Raw markdown text

        Returns:
            Cleaned text suitable for display
        """
        # Limit to first 500 characters for inline display
        if len(text) > 500:
            text = text[:500] + "..."

        # Remove excessive markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'`([^`]+)`', r'"\1"', text)      # Code
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links

        # Remove multiple newlines
        text = re.sub(r'\n\n+', ' ', text)
        text = re.sub(r'\n', ' ', text)

        return text.strip()

    def get_content(self, topic: str, fallback: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get educational content for a topic.

        Args:
            topic: Topic name (e.g., "cves", "dependencies")
            fallback: Fallback content if markdown file not found

        Returns:
            Dict with educational content sections
        """
        content = self.load_markdown_content(topic)
        if content is None and fallback is not None:
            return fallback
        elif content is None:
            # Return generic fallback
            return {
                "what_is_it": f"Information about {topic}.",
                "why_it_matters": "Keeping your system secure and up-to-date is important.",
                "when_to_update": "Update when you see security issues or outdated components.",
                "when_to_skip": "If everything is working well.",
                "how_to_fix": "Follow recommended security practices.",
                "risks": "Always backup before making changes.",
                "learn_more_url": f"https://github.com/aramantos/devaudit/blob/main/docs/README.md"
            }
        return content

    def clear_cache(self):
        """Clear the content cache (useful for testing or reloading content)."""
        self._cache.clear()


# Global content loader instance
_content_loader: Optional[EducationalContentLoader] = None


def get_educational_content(topic: str, fallback: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Get educational content for a topic.

    This is a convenience function that uses a global content loader instance.

    Args:
        topic: Topic name (e.g., "cves", "dependencies", "docker-cleanup", "bios-uefi")
        fallback: Optional fallback content if topic not found

    Returns:
        Dict with educational content sections:
            - what_is_it: Brief explanation
            - why_it_matters: Real-world impact
            - when_to_update: Guidance on urgency
            - when_to_skip: When it's safe to ignore
            - how_to_fix: Step-by-step instructions
            - risks: Risks of taking action
            - learn_more_url: Link to full documentation

    Example:
        >>> content = get_educational_content("cves")
        >>> print(content["what_is_it"])
        "CVE (Common Vulnerabilities and Exposures) is a standardized identifier..."
    """
    global _content_loader
    if _content_loader is None:
        _content_loader = EducationalContentLoader()

    return _content_loader.get_content(topic, fallback)


def clear_educational_cache():
    """Clear the educational content cache."""
    global _content_loader
    if _content_loader is not None:
        _content_loader.clear_cache()
