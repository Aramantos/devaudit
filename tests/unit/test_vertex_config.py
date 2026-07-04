"""
Tests for VertexConfig - the privacy-by-construction contract.

DevAudit's AI features must run against the USER'S own GCP project. There was
once a hardcoded internal default project here; these tests keep it gone.
"""
import os
from pathlib import Path

import pytest

from devaudit.vertex_analyzer import VertexConfig


@pytest.fixture
def clean_env(monkeypatch):
    for var in ("DEVAUDIT_VERTEX_PROJECT", "DEVAUDIT_VERTEX_LOCATION", "DEVAUDIT_VERTEX_MODEL"):
        monkeypatch.delenv(var, raising=False)


def test_project_env_var_is_required(clean_env):
    """No DEVAUDIT_VERTEX_PROJECT -> a clear, actionable error, never a default."""
    with pytest.raises(ValueError, match="DEVAUDIT_VERTEX_PROJECT"):
        VertexConfig.from_env()


def test_env_values_are_used(clean_env, monkeypatch):
    monkeypatch.setenv("DEVAUDIT_VERTEX_PROJECT", "my-own-project")
    config = VertexConfig.from_env()
    assert config["project_id"] == "my-own-project"
    assert config["location"]
    assert config["model"]


def test_no_hardcoded_project_id_in_source():
    """Guardrail: no GCP project id string may reappear in the module source.

    Anchored to the file on disk, not a constant the code exports - the exact
    regression this guards against was a baked-in default project."""
    import devaudit.vertex_analyzer as module
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "artful-winter" not in source
    assert 'PROJECT_ID = "' not in source
