"""
Firewall auditor on Linux: a firewall the auditor cannot find or cannot read
must never read as CRITICAL "Unknown is disabled".

The worked case is the Raspberry Pi 5 (M1's first Linux run, 2026-07-04). Its
firewall is native nftables (the captive portal and the server-segment fence,
no ufw), `nft` and `iptables` live in /usr/sbin, and /usr/sbin is not on the
pi5 user's PATH. shutil.which found nothing, so the auditor printed
"Unknown is disabled" at CRITICAL.

Written RED first against the unfixed auditor (M2, 2026-11-12).
"""
import json

from devaudit.auditors.system_auditors.firewall_audit import FirewallAuditor

# Shaped on the Pi's real ruleset (pi5-server architecture, measured 2026-09-24):
# an empty inet filter, the captive portal's forward chain at policy drop, the
# server-segment fence's input chain, and Docker's iptables-nft table.
PI_RULESET = """table inet filter {
\tchain input {
\t\ttype filter hook input priority filter; policy accept;
\t}
\tchain forward {
\t\ttype filter hook forward priority filter; policy accept;
\t}
\tchain output {
\t\ttype filter hook output priority filter; policy accept;
\t}
}
table inet captive_portal {
\tset auth_clients {
\t\ttype ether_addr
\t}
\tchain forward {
\t\ttype filter hook forward priority filter; policy drop;
\t\tct state established,related accept
\t\tiifname "wg0" accept
\t\toifname "wg0" accept
\t\tether saddr @auth_clients accept
\t\tiifname "srv0" oifname "eth0" accept comment "server-segment"
\t}
}
table inet server_segment {
\tchain input {
\t\ttype filter hook input priority filter - 10; policy accept;
\t\tiifname != "srv0" accept
\t\tct state established,related accept
\t\tip daddr 10.20.0.1 udp dport 53 accept
\t\tip protocol icmp accept
\t\tdrop
\t}
}
table ip filter {
\tchain FORWARD {
\t\ttype filter hook forward priority filter; policy accept;
\t\tcounter packets 0 bytes 0 jump DOCKER-USER
\t}
}
"""

LOCKED_DOWN_RULESET = """table inet filter {
\tchain input {
\t\ttype filter hook input priority filter; policy drop;
\t\tct state established,related accept
\t\tiif "lo" accept
\t\ttcp dport 22 accept
\t}
}
"""


def _nft(ruleset, readable=True):
    def handler(args, sudo):
        if args[:2] == ["list", "ruleset"]:
            if readable:
                return ruleset, "", 0
            return "", "Error: Could not process rule: Operation not permitted", 1
        return "", "", 1

    return handler


def _iptables_should_not_be_needed(args, sudo):
    raise AssertionError("nft was found: iptables should not be the reader")


def test_pi_nftables_in_sbin_is_found_and_read(fake_host):
    auditor = FirewallAuditor()
    fake_host(
        auditor,
        on_path=set(),
        in_sbin={"nft", "iptables"},
        handlers={"nft": _nft(PI_RULESET), "iptables": _iptables_should_not_be_needed},
    )

    result = auditor.audit()

    assert "nftables" in result["firewall_type"].lower()
    assert result["enabled"] is True
    assert result["risk_level"] != "critical"
    assert "Unknown" not in result["recommendation"]


def test_pi_ruleset_with_open_input_reads_medium_review_inbound(fake_host):
    """Drops exist (forward), but no input chain defaults to drop: MEDIUM, review inbound."""
    auditor = FirewallAuditor()
    fake_host(auditor, on_path=set(), in_sbin={"nft"}, handlers={"nft": _nft(PI_RULESET)})

    result = auditor.audit()

    assert result["inbound_default"] == "Allow"
    assert result["risk_level"] == "medium"


def test_nftables_input_policy_drop_reads_low(fake_host):
    auditor = FirewallAuditor()
    fake_host(auditor, on_path=set(), in_sbin={"nft"}, handlers={"nft": _nft(LOCKED_DOWN_RULESET)})

    result = auditor.audit()

    assert result["enabled"] is True
    assert result["inbound_default"] == "Drop"
    assert result["risk_level"] == "low"


def test_unreadable_nftables_is_status_unknown_not_disabled(fake_host):
    """nft present, no root and no passwordless sudo: we do not know, so we say so."""
    auditor = FirewallAuditor()
    fake_host(
        auditor,
        on_path=set(),
        in_sbin={"nft"},
        sudo_ok=False,
        handlers={"nft": _nft(PI_RULESET, readable=False)},
    )

    result = auditor.audit()

    assert result.get("status_unknown") is True
    assert result["risk_level"] == "medium"
    assert "is disabled" not in result["recommendation"]
    assert "sudo nft list ruleset" in result["recommendation"]


def test_unreadable_ufw_is_status_unknown_not_disabled(fake_host):
    """Ubuntu desktop shape: ufw on PATH, `ufw status` needs root, no passwordless sudo."""
    auditor = FirewallAuditor()

    def ufw(args, sudo):
        return "", "ERROR: You need to be root to run this script", 1

    fake_host(auditor, on_path={"ufw"}, sudo_ok=False, handlers={"ufw": ufw})

    result = auditor.audit()

    assert result.get("status_unknown") is True
    assert result["risk_level"] == "medium"
    assert "Unknown is disabled" not in result["recommendation"]
    assert "sudo ufw status" in result["recommendation"]


def test_no_firewall_tool_anywhere_says_so_plainly(fake_host):
    """Nothing on PATH or in sbin: a real absence, said in words, not 'Unknown is disabled'."""
    auditor = FirewallAuditor()
    fake_host(auditor, on_path=set(), in_sbin=set(), handlers={})

    result = auditor.audit()

    assert result["risk_level"] == "critical"
    assert "Unknown is disabled" not in result["recommendation"]
    assert "no host firewall" in result["recommendation"].lower()


def test_active_ufw_still_reads_low(fake_host):
    """Positive control: the ufw path that already worked keeps working."""
    auditor = FirewallAuditor()

    def ufw(args, sudo):
        return "Status: active\n\nTo                         Action      From\n", "", 0

    fake_host(auditor, on_path={"ufw"}, handlers={"ufw": ufw})

    result = auditor.audit()

    assert result["enabled"] is True
    assert result["risk_level"] == "low"


def test_windows_firewall_all_profiles_on_still_reads_low(fake_host):
    """Positive control for the PC: the Windows path is untouched by the Linux fix."""
    auditor = FirewallAuditor()
    profiles = [
        {"Name": n, "Enabled": True, "DefaultInboundAction": "Block", "DefaultOutboundAction": "Allow"}
        for n in ("Domain", "Private", "Public")
    ]

    def powershell(args, sudo):
        return json.dumps(profiles), "", 0

    fake_host(auditor, platform="Windows", on_path={"powershell"}, handlers={"powershell": powershell})

    result = auditor.audit()

    assert result["enabled"] is True
    assert result["risk_level"] == "low"
