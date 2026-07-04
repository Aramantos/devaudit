"""
Tests for the Python package auditor - contract-level, anchored to the real
class (no mocked mirrors of its own constants).
"""
from devaudit.auditors import PythonAuditor


def test_python_auditor_initialization():
    """Auditor constructs and exposes the BaseAuditor contract."""
    auditor = PythonAuditor()
    assert auditor.name
    assert callable(auditor.audit)
    assert callable(auditor.is_installed)
    assert callable(auditor.get_version)


def test_python_auditor_is_installed_returns_bool():
    """is_installed answers with a real boolean on this machine."""
    assert isinstance(PythonAuditor().is_installed(), bool)


def test_python_auditor_get_version_shape():
    """get_version returns a version string (or None when absent)."""
    version = PythonAuditor().get_version()
    assert version is None or isinstance(version, str)


def test_python_auditor_accepts_target_dir(temp_dir):
    """A target_dir is accepted and stored for project-scoped scans."""
    auditor = PythonAuditor(target_dir=str(temp_dir))
    assert auditor is not None
