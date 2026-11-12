"""
OS update auditor: the HOW TO FIX text must match the machine it runs on, and
the apt security count must count packages, not lines.

M1's first Linux run (the Pi 5, 2026-07-04) told a Raspberry Pi user to open
"Settings -> Windows Update". And `apt-get --just-print upgrade` prints each
package twice (an Inst line and a Conf line), so counting '-security' text
doubled the security count: 3 real security updates read 6, which is CRITICAL
(5 or more) instead of HIGH.

Written RED first against the unfixed auditor (M2, 2026-11-12).
"""
import json

from devaudit.auditors.system_auditors.os_update_audit import OSUpdateAuditor

APT_UPGRADABLE_PLAIN = (
    "Listing...\n"
    "curl/stable 8.14.1-2+deb13u1 arm64 [upgradable from: 8.14.1-2]\n"
    "tzdata/stable 2025b-4+deb13u1 all [upgradable from: 2025b-4]\n"
    "vim/stable 2:9.1.1230-2+deb13u1 arm64 [upgradable from: 2:9.1.1230-2]\n"
)

JUST_PRINT_PLAIN = (
    "NOTE: This is only a simulation!\n"
    "Reading package lists...\n"
    "Inst curl [8.14.1-2] (8.14.1-2+deb13u1 Debian:13.2/stable [arm64])\n"
    "Inst tzdata [2025b-4] (2025b-4+deb13u1 Debian:13.2/stable [all])\n"
    "Inst vim [2:9.1.1230-2] (2:9.1.1230-2+deb13u1 Debian:13.2/stable [arm64])\n"
    "Conf curl (8.14.1-2+deb13u1 Debian:13.2/stable [arm64])\n"
    "Conf tzdata (2025b-4+deb13u1 Debian:13.2/stable [all])\n"
    "Conf vim (2:9.1.1230-2+deb13u1 Debian:13.2/stable [arm64])\n"
)

APT_UPGRADABLE_SECURITY = (
    "Listing...\n"
    "libssl3t64/stable-security 3.5.1-1+deb13u1 arm64 [upgradable from: 3.5.1-1]\n"
    "openssl/stable-security 3.5.1-1+deb13u1 arm64 [upgradable from: 3.5.1-1]\n"
    "libxml2/stable-security 2.12.7+dfsg-3+deb13u1 arm64 [upgradable from: 2.12.7+dfsg-3]\n"
    "tzdata/stable 2025b-4+deb13u1 all [upgradable from: 2025b-4]\n"
)

JUST_PRINT_SECURITY = (
    "NOTE: This is only a simulation!\n"
    "Inst libssl3t64 [3.5.1-1] (3.5.1-1+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Inst openssl [3.5.1-1] (3.5.1-1+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Inst libxml2 [2.12.7+dfsg-3] (2.12.7+dfsg-3+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Inst tzdata [2025b-4] (2025b-4+deb13u1 Debian:13.2/stable [all])\n"
    "Conf libssl3t64 (3.5.1-1+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Conf openssl (3.5.1-1+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Conf libxml2 (2.12.7+dfsg-3+deb13u1 Debian-Security:13/stable-security [arm64])\n"
    "Conf tzdata (2025b-4+deb13u1 Debian:13.2/stable [all])\n"
)


def _apt_host(fake_host, auditor, upgradable, just_print):
    def apt_get(args, sudo):
        if args[:1] == ["update"]:
            return "", "E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)", 100
        if "--just-print" in args:
            return just_print, "", 0
        return "", "", 1

    def apt(args, sudo):
        if args[:2] == ["list", "--upgradable"]:
            return upgradable, "WARNING: apt does not have a stable CLI interface.", 0
        return "", "", 1

    return fake_host(auditor, on_path={"apt-get", "apt"}, handlers={"apt-get": apt_get, "apt": apt})


def test_linux_fix_text_names_apt_not_windows_update(fake_host):
    auditor = OSUpdateAuditor()
    _apt_host(fake_host, auditor, APT_UPGRADABLE_PLAIN, JUST_PRINT_PLAIN)

    result = auditor.audit()

    assert result["update_count"] == 3
    assert result["risk_level"] == "low"
    assert "Windows Update" not in result["recommendation"]
    assert "apt" in result["recommendation"]


def test_apt_security_updates_are_counted_once_each(fake_host):
    """3 security packages are 3, not 6: HIGH, not a false CRITICAL."""
    auditor = OSUpdateAuditor()
    _apt_host(fake_host, auditor, APT_UPGRADABLE_SECURITY, JUST_PRINT_SECURITY)

    result = auditor.audit()

    assert result["security_updates"] == 3
    assert result["risk_level"] == "high"
    assert "Windows Update" not in result["recommendation"]


def test_dnf_fix_text_names_dnf(fake_host):
    auditor = OSUpdateAuditor()

    def dnf(args, sudo):
        out = (
            "\n"
            "kernel.x86_64          6.11.4-301.fc41      updates\n"
            "openssl.x86_64         1:3.2.2-9.fc41       updates\n"
        )
        return out, "", 100

    fake_host(auditor, on_path={"dnf"}, handlers={"dnf": dnf})

    result = auditor.audit()

    assert result["update_count"] == 2
    assert "Windows Update" not in result["recommendation"]
    assert "dnf" in result["recommendation"]


def test_macos_fix_text_names_software_update(fake_host):
    auditor = OSUpdateAuditor()

    def sw_vers(args, sudo):
        return "ProductName:\tmacOS\nProductVersion:\t15.1\n", "", 0

    def softwareupdate(args, sudo):
        out = (
            "Software Update Tool\n\n"
            "Finding available software\n"
            "Software Update found the following new or updated software:\n"
            "* Label: Safari18.2-18.2\n"
            "\tTitle: Safari, Version: 18.2, Size: 190000KiB, Recommended: YES,\n"
        )
        return out, "", 0

    fake_host(
        auditor,
        platform="Darwin",
        on_path={"sw_vers", "softwareupdate"},
        handlers={"sw_vers": sw_vers, "softwareupdate": softwareupdate},
    )

    result = auditor.audit()

    assert result["update_count"] == 1
    assert "Windows Update" not in result["recommendation"]
    assert "Software Update" in result["recommendation"]


def test_windows_fix_text_still_names_windows_update(fake_host):
    """Positive control for the PC: Windows keeps its own HOW TO FIX."""
    auditor = OSUpdateAuditor()

    def powershell(args, sudo):
        script = args[-1]
        if "Win32_OperatingSystem" in script:
            return json.dumps({"Caption": "Microsoft Windows 11 Pro", "Version": "10.0.26300", "Build": 26300}), "", 0
        if "Microsoft.Update.Session" in script:
            updates = [
                {"Title": "2026-11 Cumulative Update", "IsSecurityUpdate": 1, "Severity": "Critical"},
                {"Title": "Defender definitions", "IsSecurityUpdate": 1, "Severity": None},
            ]
            return json.dumps(updates), "", 0
        return "2026-11-12 08:00:00", "", 0

    fake_host(auditor, platform="Windows", on_path={"powershell"}, handlers={"powershell": powershell})

    result = auditor.audit()

    assert result["security_updates"] == 2
    assert result["risk_level"] == "high"
    assert "Windows Update" in result["recommendation"]
