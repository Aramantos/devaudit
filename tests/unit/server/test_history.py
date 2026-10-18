"""
Tests for scan history management - real ScanHistory against a temp directory.
"""
import os
import stat

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


# --- scan ids are names, never paths (found 2026-10-18) ----------------------
# scan_id went straight into `storage_dir / f"{scan_id}.json"`, so an id of
# "../victim" (or "..\\victim" on Windows, reachable over HTTP there) read,
# rewrote or deleted any .json file the user owns.

TRAVERSAL_IDS = ["../victim", "..\\victim", "sub/../../victim", "/abs/victim", "", "a.b"]


@pytest.fixture
def victim(temp_dir):
    """A JSON file OUTSIDE the history directory (history lives at temp/history)."""
    path = temp_dir / "victim.json"
    path.write_text('{"untouched": true}')
    return path


@pytest.mark.parametrize("scan_id", TRAVERSAL_IDS)
def test_get_scan_refuses_path_ids(history, victim, scan_id):
    assert history.get_scan(scan_id) is None


@pytest.mark.parametrize("scan_id", TRAVERSAL_IDS)
def test_delete_scan_refuses_path_ids(history, victim, scan_id):
    assert history.delete_scan(scan_id) is False
    assert victim.exists()


@pytest.mark.parametrize("scan_id", TRAVERSAL_IDS)
def test_update_notes_refuses_path_ids(history, victim, scan_id):
    assert history.update_scan_notes(scan_id, "owned") is False
    assert victim.read_text() == '{"untouched": true}'


# --- the history is a system inventory: private on POSIX ----------------------

@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits; Windows profiles are user-scoped by ACL")
def test_history_dir_and_files_are_private(history, mock_scan_data):
    scan_id = history.save_scan(mock_scan_data)
    assert stat.S_IMODE(history.storage_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(history.index_file.stat().st_mode) == 0o600
    assert stat.S_IMODE((history.storage_dir / f"{scan_id}.json").stat().st_mode) == 0o600


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_existing_open_history_dir_is_tightened(temp_dir):
    """An install that predates this fix left the dir at the umask default."""
    storage = temp_dir / "history"
    storage.mkdir()
    storage.chmod(0o755)
    ScanHistory(storage_dir=storage)
    assert stat.S_IMODE(storage.stat().st_mode) == 0o700
