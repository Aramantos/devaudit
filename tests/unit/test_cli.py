"""
CLI surface tests - every documented command exists and answers --help.
Fast by design: no real scans run here.
"""
from click.testing import CliRunner

from devaudit.cli import main


def test_cli_help():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("scan", "security", "serve", "compare", "widget"):
        assert command in result.output


def test_cli_version():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0


def test_scan_help():
    result = CliRunner().invoke(main, ["scan", "--help"])
    assert result.exit_code == 0
    assert "--target" in result.output


def test_security_help():
    """The system-security auditors are CLI-reachable (they were
    dashboard-only until 2026-07-04)."""
    result = CliRunner().invoke(main, ["security", "--help"])
    assert result.exit_code == 0
    assert "--format" in result.output


def test_module_entrypoint_exists():
    """python -m devaudit works (devaudit/__main__.py present)."""
    import devaudit.__main__  # noqa: F401
