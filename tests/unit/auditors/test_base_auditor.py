"""
Tests for BaseAuditor class.
"""
import pytest
from devaudit.auditors.base import BaseAuditor


class MockAuditor(BaseAuditor):
    """Mock auditor for testing base functionality."""

    def audit(self):
        return {
            "status": "success",
            "findings": []
        }

    def is_installed(self):
        return True

    def get_version(self):
        return "0.0.0-test"


def test_base_auditor_initialization():
    """Test that BaseAuditor can be initialized."""
    auditor = MockAuditor()
    assert auditor is not None


def test_base_auditor_audit_method_exists():
    """Test that audit method exists and can be called."""
    auditor = MockAuditor()
    result = auditor.audit()
    assert result is not None
    assert "status" in result


def test_base_auditor_subclass_required():
    """Test that BaseAuditor cannot be instantiated directly."""
    # BaseAuditor should be abstract or require subclassing
    # This test verifies the design pattern
    with pytest.raises(TypeError):
        BaseAuditor()
