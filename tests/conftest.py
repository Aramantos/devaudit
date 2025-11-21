"""
Pytest configuration and shared fixtures for DevAudit tests.
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_scan_data():
    """Provide sample scan data for testing."""
    return {
        "timestamp": "2025-01-20T12:00:00",
        "python": {
            "packages": [
                {"name": "requests", "version": "2.31.0", "latest": "2.31.0"},
                {"name": "flask", "version": "2.3.0", "latest": "3.0.0"}
            ],
            "vulnerabilities": [
                {
                    "package": "flask",
                    "id": "CVE-2023-12345",
                    "severity": "HIGH",
                    "description": "Test vulnerability"
                }
            ]
        },
        "node": {
            "packages": [],
            "vulnerabilities": []
        }
    }


@pytest.fixture
def mock_system_info():
    """Provide sample system information for testing."""
    return {
        "platform": "Windows",
        "version": "10.0.22000",
        "hostname": "test-machine",
        "python_version": "3.12.0"
    }
