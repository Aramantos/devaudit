"""
Tests for scan history management - real ScanHistory against a temp directory.
"""
import pytest

from devaudit.server.history import ScanHistory


@pytest.fixture
def history(temp_dir):
    return ScanHistory(storage_dir=temp_dir / "history")


def test_save_scan_creates_file(history, mock_scan_data):
    """Saving a scan returns an id and writes a JSON file on disk."""
    scan_id = history.save_scan(mock_scan_data)
    assert scan_id
    saved_files = list(history.storage_dir.glob("*.json"))
    # index.json plus the scan file itself
    assert history.index_file in saved_files
    assert len(saved_files) >= 2


def test_get_scan_roundtrip(history, mock_scan_data):
    """A saved scan can be loaded back and carries the results."""
    scan_id = history.save_scan(mock_scan_data)
    loaded = history.get_scan(scan_id)
    assert loaded is not None
    assert loaded["results"]["python"]["packages"][0]["name"] == "requests"


def test_get_latest_scan_returns_most_recent(history, mock_scan_data):
    """get_latest_scan returns the last-saved scan."""
    history.save_scan(mock_scan_data)
    second = dict(mock_scan_data)
    second["marker"] = "second"
    second_id = history.save_scan(second)
    latest = history.get_latest_scan()
    assert latest is not None
    assert latest.get("id", latest.get("scan_id")) == second_id or \
        latest["results"].get("marker") == "second"


def test_list_scans_respects_limit(history, mock_scan_data):
    """list_scans returns at most `limit` entries."""
    for _ in range(4):
        history.save_scan(mock_scan_data)
    assert len(history.list_scans(limit=2)) == 2
    assert len(history.list_scans(limit=10)) == 4


def test_compare_scans_runs_on_real_scans(history, mock_scan_data):
    """compare_scans produces a comparison dict for two real saved scans."""
    id1 = history.save_scan(mock_scan_data)
    changed = {
        "python": {
            "packages": [
                {"name": "requests", "version": "2.31.0", "latest": "2.31.0"},
            ],
            "vulnerabilities": [],
        },
        "node": {"packages": [], "vulnerabilities": []},
    }
    id2 = history.save_scan(changed)
    comparison = history.compare_scans(id1, id2)
    assert isinstance(comparison, dict)
    assert comparison  # non-empty


def test_history_creates_missing_directory(temp_dir):
    """A nested, not-yet-existing storage dir is created rather than erroring."""
    nested = temp_dir / "does" / "not" / "exist"
    history = ScanHistory(storage_dir=nested)
    assert nested.is_dir()
    assert history.index_file.exists()


def test_delete_scan_removes_it(history, mock_scan_data):
    """Deleted scans disappear from the index and from disk."""
    scan_id = history.save_scan(mock_scan_data)
    assert history.delete_scan(scan_id) is True
    assert history.get_scan(scan_id) is None
