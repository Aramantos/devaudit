"""
Backup auditor on Linux: a real backup that runs as a systemd timer must read
as a backup, never as CRITICAL "no backup".

The worked case is the Raspberry Pi 5 (M1's first Linux run, 2026-07-04): its
nightly off-site backup is `pi-backup.timer` -> `pi-backup.service`
(operations/pi5-server/ops/), and DevAudit only looked for rsnapshot,
duplicity, timeshift, borg and restic config files, so it read CRITICAL.

Written RED first against the unfixed auditor (M2, 2026-11-12).
"""
from datetime import datetime, timedelta

from devaudit.auditors.system_auditors.backup_audit import BackupAuditor

# Debian ships dpkg-db-backup.timer enabled by default: it copies dpkg's own
# package database, which is not a backup of the user's data.
PI_TIMERS = (
    "apt-daily.timer                enabled enabled\n"
    "dpkg-db-backup.timer           enabled enabled\n"
    "e2scrub_all.timer              enabled enabled\n"
    "pi-backup.timer                {state} enabled\n"
)


def _stamp(hours_ago):
    return (datetime.now() - timedelta(hours=hours_ago)).strftime("%a %Y-%m-%d %H:%M:%S UTC")


def _systemctl(timers, units):
    """A systemctl that lists `timers` and answers `show` from `units`."""

    def handler(args, sudo):
        if "list-unit-files" in args:
            return timers, "", 0
        if "show" in args:
            unit = args[args.index("show") + 1]
            props = units.get(unit, {})
            return "".join(f"{k}={v}\n" for k, v in props.items()), "", 0
        return "", "", 1

    return handler


def _pi_backup(monkeypatch, fake_host, state="enabled", last_trigger=None, result="success"):
    auditor = BackupAuditor()
    monkeypatch.setattr(BackupAuditor, "LINUX_BACKUP_CONFIGS", {}, raising=False)
    units = {
        "pi-backup.timer": {
            "Unit": "pi-backup.service",
            "LastTriggerUSec": last_trigger if last_trigger is not None else _stamp(20),
        },
        "pi-backup.service": {"Result": result},
        "dpkg-db-backup.timer": {
            "Unit": "dpkg-db-backup.service",
            "LastTriggerUSec": _stamp(2),
        },
        "dpkg-db-backup.service": {"Result": "success"},
    }
    fake_host(
        auditor,
        on_path={"systemctl"},
        handlers={"systemctl": _systemctl(PI_TIMERS.format(state=state), units)},
    )
    return auditor.audit()


def test_pi_backup_timer_reads_as_a_recent_backup(monkeypatch, fake_host):
    result = _pi_backup(monkeypatch, fake_host)

    assert result["backup_configured"] is True
    assert "pi-backup" in result["backup_type"]
    assert result["backup_enabled"] is True
    assert result["days_since_backup"] in (0, 1)
    assert result["risk_level"] == "none"
    assert "CRITICAL" not in result["recommendation"]


def test_dpkg_db_backup_alone_is_not_a_backup(monkeypatch, fake_host):
    """Positive control: Debian's own dpkg-db-backup must not pass for a real backup."""
    auditor = BackupAuditor()
    monkeypatch.setattr(BackupAuditor, "LINUX_BACKUP_CONFIGS", {}, raising=False)
    timers = "apt-daily.timer enabled enabled\ndpkg-db-backup.timer enabled enabled\n"
    units = {
        "dpkg-db-backup.timer": {"Unit": "dpkg-db-backup.service", "LastTriggerUSec": _stamp(2)},
        "dpkg-db-backup.service": {"Result": "success"},
    }
    fake_host(auditor, on_path={"systemctl"}, handlers={"systemctl": _systemctl(timers, units)})

    result = auditor.audit()

    assert result["backup_configured"] is False
    assert result["risk_level"] == "critical"


def test_failed_last_run_is_high_and_says_it_failed(monkeypatch, fake_host):
    result = _pi_backup(monkeypatch, fake_host, result="exit-code")

    assert result["risk_level"] == "high"
    assert "failed" in result["recommendation"].lower()
    assert "CRITICAL" not in result["recommendation"]


def test_disabled_backup_timer_is_high_not_critical(monkeypatch, fake_host):
    result = _pi_backup(monkeypatch, fake_host, state="disabled")

    assert result["backup_configured"] is True
    assert result["backup_enabled"] is False
    assert result["risk_level"] == "high"
    assert "DISABLED" in result["recommendation"]


def test_timer_that_never_ran_says_so_not_999_days(monkeypatch, fake_host):
    result = _pi_backup(monkeypatch, fake_host, last_trigger="n/a")

    assert result["risk_level"] == "high"
    assert "999" not in result["recommendation"]
    assert "not run" in result["recommendation"].lower()


def test_config_found_but_last_run_unknown_is_status_unknown(monkeypatch, fake_host, tmp_path):
    """A backup tool's config with no readable last-run time is UNKNOWN, not '999 days ago'."""
    conf = tmp_path / "rsnapshot.conf"
    conf.write_text("config_version\t1.2\n")
    auditor = BackupAuditor()
    monkeypatch.setattr(
        BackupAuditor, "LINUX_BACKUP_CONFIGS", {"rsnapshot": str(conf)}, raising=False
    )
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result["backup_configured"] is True
    assert result.get("status_unknown") is True
    assert result["risk_level"] == "medium"
    assert "999" not in result["recommendation"]


def test_nothing_at_all_is_still_critical(monkeypatch, fake_host):
    """Positive control: a machine with no backup of any kind still reads CRITICAL."""
    auditor = BackupAuditor()
    monkeypatch.setattr(BackupAuditor, "LINUX_BACKUP_CONFIGS", {}, raising=False)
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result["backup_configured"] is False
    assert result["risk_level"] == "critical"
