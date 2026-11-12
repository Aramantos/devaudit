"""
BIOS auditor on boards that have no BIOS: an ARM single-board computer such as
a Raspberry Pi has no SMBIOS/DMI table at all, so "could not detect BIOS
information, this may require administrator/root privileges" is wrong twice.
The honest answer is "not applicable on this hardware".

Worked case: the Raspberry Pi 5 (M1's first Linux run, 2026-07-04). It has no
/sys/class/dmi/id, and the device tree names the board in
/proc/device-tree/model ("Raspberry Pi 5 Model B Rev 1.0", NUL-terminated).

Written RED first against the unfixed auditor (M2, 2026-11-12).
"""
from devaudit.auditors.system_auditors.bios_audit import BIOSAuditor


def _no_smbios(args, sudo):
    return "# dmidecode 3.6\n# No SMBIOS nor DMI entry point found, sorry.\n", "", 1


def _board(monkeypatch, tmp_path, model=None, dmi=None):
    """Point the auditor's DMI and device-tree paths at tmp_path."""
    dmi_dir = tmp_path / "dmi_id"
    if dmi is not None:
        dmi_dir.mkdir()
        for name, value in dmi.items():
            (dmi_dir / name).write_text(value + "\n", encoding="utf-8")
    model_path = tmp_path / "device-tree-model"
    if model is not None:
        model_path.write_bytes(model)
    monkeypatch.setattr(BIOSAuditor, "DMI_ID_DIR", dmi_dir, raising=False)
    monkeypatch.setattr(BIOSAuditor, "DEVICE_TREE_MODEL", model_path, raising=False)


def test_raspberry_pi_reads_not_applicable(monkeypatch, fake_host, tmp_path):
    _board(monkeypatch, tmp_path, model=b"Raspberry Pi 5 Model B Rev 1.0\x00")
    auditor = BIOSAuditor()
    fake_host(auditor, on_path=set(), in_sbin={"dmidecode"}, handlers={"dmidecode": _no_smbios})

    result = auditor.audit()

    assert "error" not in result
    assert result["applicable"] is False
    assert result["risk_level"] == "none"
    assert "not applicable" in result["recommendation"].lower()
    assert result["motherboard"] == "Raspberry Pi 5 Model B Rev 1.0"
    assert "rpi-eeprom-update" in result["recommendation"]


def test_other_device_tree_board_reads_not_applicable_without_pi_advice(monkeypatch, fake_host, tmp_path):
    _board(monkeypatch, tmp_path, model=b"Pine64 RockPro64 v2.1\x00")
    auditor = BIOSAuditor()
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result["applicable"] is False
    assert result["risk_level"] == "none"
    assert "rpi-eeprom-update" not in result["recommendation"]


def test_pc_shaped_linux_reads_bios_from_sysfs(monkeypatch, fake_host, tmp_path):
    """Regression: a DMI-bearing Linux box still reads its BIOS from sysfs, unprivileged."""
    _board(
        monkeypatch,
        tmp_path,
        dmi={"bios_vendor": "Dell Inc.", "bios_version": "1.21.0", "bios_date": "03/15/2025"},
    )
    auditor = BIOSAuditor()
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result.get("applicable", True) is True
    assert result["version"] == "1.21.0"
    assert result["vendor"] == "Dell Inc."
    assert result["age_days"] is not None


def test_no_dmi_and_no_device_tree_still_says_could_not_detect(monkeypatch, fake_host, tmp_path):
    """Positive control: when we truly cannot tell, we still say we could not detect."""
    _board(monkeypatch, tmp_path)
    auditor = BIOSAuditor()
    fake_host(auditor, on_path=set(), handlers={})

    result = auditor.audit()

    assert result.get("error") == "Could not detect BIOS information"
    assert result["risk_level"] == "none"
