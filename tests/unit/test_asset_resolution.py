"""
Tests for build-asset resolution - the packaging bug class.

The dashboard build and the educational markdown live OUTSIDE the package in a
source checkout, so every wheel ever built silently shipped neither. These
tests pin the resolution contract: package-internal copy first, repo-root
fallback second, and the educational loader must find REAL content (not its
generic boilerplate fallback) in a source checkout.
"""
from pathlib import Path

from devaudit.educational.content_loader import EducationalContentLoader


def test_loader_resolves_a_real_content_directory():
    loader = EducationalContentLoader()
    assert loader.docs_path.is_dir(), (
        f"content dir does not exist: {loader.docs_path} - education silently "
        "degrades to boilerplate when this happens"
    )
    assert list(loader.docs_path.glob("*.md")), "content dir has no markdown"


def test_loader_prefers_package_internal_copy_when_present():
    """If the package-internal copy exists (wheel layout, or after
    scripts/prepare_package_assets.py), it wins over the repo docs."""
    import devaudit.educational as edu_pkg
    packaged = Path(edu_pkg.__file__).parent / "content"
    loader = EducationalContentLoader()
    if packaged.is_dir():
        assert loader.docs_path == packaged
    else:
        assert loader.docs_path.name == "concepts"


def test_loader_serves_real_content_not_boilerplate():
    """A known topic loads its real markdown, not the generic fallback."""
    loader = EducationalContentLoader()
    content = loader.load_markdown_content("backups")
    assert content is not None, "backups.md should exist in the content dir"


def test_explicit_docs_path_is_respected(tmp_path):
    loader = EducationalContentLoader(docs_path=tmp_path)
    assert loader.docs_path == tmp_path
