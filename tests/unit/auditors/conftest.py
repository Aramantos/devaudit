"""
Shared fakes for the system-auditor tests: a pretend host the auditors probe.

The worked case is the Raspberry Pi 5 from M1's first Linux run (2026-07-04):
Debian keeps nft, iptables, ufw and dmidecode in /usr/sbin, which is NOT on a
normal user's PATH (the Pi's own record: "no sysctl on pi5's PATH"), and the
pi5 user has passwordless sudo, so `sudo -n <tool>` succeeds there.

Nothing here touches the real machine: shutil.which and the auditor's
run_command are both replaced for the length of one test.
"""
import os
import posixpath
import shutil

import pytest


class FakeHost:
    """A host with some tools on PATH, some only in /usr/sbin, and canned output.

    handlers maps a tool's base name to fn(args, sudo) -> (stdout, stderr, rc).
    """

    def __init__(self, on_path=(), in_sbin=(), handlers=None, sudo_ok=True):
        self.on_path = set(on_path)
        self.in_sbin = set(in_sbin)
        self.handlers = dict(handlers or {})
        self.sudo_ok = sudo_ok
        self.calls = []

    def which(self, cmd, mode=os.F_OK | os.X_OK, path=None):
        if path is None:
            return f"/usr/bin/{cmd}" if cmd in self.on_path else None
        dirs = path.split(os.pathsep)
        if cmd in self.in_sbin and "/usr/sbin" in dirs:
            return f"/usr/sbin/{cmd}"
        if cmd in self.on_path and "/usr/bin" in dirs:
            return f"/usr/bin/{cmd}"
        return None

    def run(self, cmd, timeout=30):
        argv = list(cmd)
        self.calls.append(argv)
        sudo = False
        if argv[:2] == ["sudo", "-n"]:
            sudo = True
            argv = argv[2:]
            if not self.sudo_ok:
                return "", "sudo: a password is required", 1
        exe = argv[0]
        base = posixpath.basename(exe.replace("\\", "/"))
        absolute = "/" in exe
        # A bare name resolves on PATH, or (under sudo) on sudo's secure_path,
        # which includes sbin. An absolute path runs if the tool exists at all.
        if absolute:
            exists = base in self.on_path or base in self.in_sbin
        elif sudo:
            exists = base in self.on_path or base in self.in_sbin
        else:
            exists = base in self.on_path
        if not exists:
            return "", f"Command not found: {exe}", -1
        handler = self.handlers.get(base)
        if handler is None:
            return "", "", 1
        return handler(argv[1:], sudo)


@pytest.fixture
def fake_host(monkeypatch):
    """Install a FakeHost under one auditor: fake_host(auditor, platform=..., ...)."""

    def install(auditor, platform="Linux", **kwargs):
        host = FakeHost(**kwargs)
        monkeypatch.setattr(shutil, "which", host.which)
        monkeypatch.setattr(auditor, "run_command", host.run)
        auditor.platform = platform
        return host

    return install
