"""
Backup auditor: the words must say what DevAudit actually checked.

Caretaker's read of John's PC (2026-11-12): its CRITICAL "no backup" is
probably TRUE (a nightly copy of raw session data only, no system image, no
File History, nothing off-site), so the fix is not to clear the red but to make
it say what DevAudit looked for, so the red names what is missing.

And the reverse: a backup found only because a scheduled job is NAMED for a
backup proves that the job ran, not what it copies. The line must say so.

Written RED first (M2, 2026-11-12).
"""
import json
from datetime import datetime, timedelta

from devaudit.auditors.system_auditors.backup_audit import BackupAuditor


def test_windows_critical_names_what_it_looked_for(fake_host):
    auditor = BackupAuditor()

    def powershell(args, sudo):
        return json.dumps({"Configured": False}), "", 0

    fake_host(auditor, platform="Windows", on_path={"powershell"}, handlers={"powershell": powershell})

    result = auditor.audit()

    assert result["risk_level"] == "critical"
    assert "looked for" in result["recommendation"]
    assert "Windows Backup" in result["recommendation"]
    assert "File History" in result["recommendation"]


def test_macos_critical_names_what_it_looked_for(fake_host):
    auditor = BackupAuditor()

    def tmutil(args, sudo):
        return "", "No destinations configured.", 1

    fake_host(auditor, platform="Darwin", on_path={"tmutil"}, handlers={"tmutil": tmutil})

    result = auditor.audit()

    assert result["risk_level"] == "critical"
    assert "looked for" in result["recommendation"]
    assert "Time Machine" in result["recommendation"]


def test_linux_critical_names_what_it_looked_for(monkeypatch, fake_host):
    auditor = BackupAuditor()
    monkeypatch.setattr(BackupAuditor, "LINUX_BACKUP_CONFIGS", {}, raising=False)
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result["risk_level"] == "critical"
    assert "looked for" in result["recommendation"]
    assert "systemd timer" in result["recommendation"]


def test_a_backup_found_by_its_timer_name_says_coverage_is_unseen(monkeypatch, fake_host):
    auditor = BackupAuditor()
    monkeypatch.setattr(BackupAuditor, "LINUX_BACKUP_CONFIGS", {}, raising=False)
    stamp = (datetime.now() - timedelta(hours=20)).strftime("%a %Y-%m-%d %H:%M:%S UTC")

    def systemctl(args, sudo):
        if "list-unit-files" in args:
            return "pi-backup.timer enabled enabled\n", "", 0
        unit = args[args.index("show") + 1]
        if unit == "pi-backup.timer":
            return f"Unit=pi-backup.service\nLastTriggerUSec={stamp}\n", "", 0
        return "Result=success\n", "", 0

    fake_host(auditor, on_path={"systemctl"}, handlers={"systemctl": systemctl})

    result = auditor.audit()

    assert result["risk_level"] == "none"
    assert "not what it copies" in result["recommendation"]
