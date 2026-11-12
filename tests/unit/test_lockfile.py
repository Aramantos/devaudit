"""
The hashed lockfile (requirements-lock.txt) stays true to setup.py.

Why it exists (conference call 2, room c2-rc, decision R2, 2026-10-18): the
estate server's job queue installs a product's Python dependencies from a
HASHED bundle, so DevAudit needs one pinned, hashed list for its `[server,dev]`
extras. It is regenerated, never hand-edited:

    pip-compile --generate-hashes --allow-unsafe --strip-extras \
        --extra server --extra dev --no-emit-index-url \
        --output-file requirements-lock.txt setup.py

These tests keep it honest: every pin carries a hash, every package setup.py
asks for is pinned, and the pins stay above the fixed versions of the
advisories surety found in DevAudit's own environment
(operations/surety/findings/DEVAUDIT_BOX_WHEELS_AND_CVE_2026-11-07.md).

DEVAUDIT_LOCK_UNDER_TEST points the tests at another file (the mutant check).
"""
import os
import re
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
LOCK = Path(os.environ.get("DEVAUDIT_LOCK_UNDER_TEST", ROOT / "requirements-lock.txt"))

PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\;]+)")

# Surety, 7 Nov 2026: the first fixed version of each advisory it found in
# DevAudit's .venv. starlette: GHSA-wqp7-x3pw-xc5r (UNC paths in StaticFiles on
# Windows, fixed 1.1.0) and GHSA-82w8-qh3p-5jfq (form limits, fixed 1.3.1);
# anyio GHSA-82r6-8w77-94w6; certifi GHSA-6q48-6c7w-9gw2; idna GHSA-65pc-fj4g-8rjx.
ADVISORY_FLOORS = {
    "starlette": "1.3.1",
    "anyio": "4.14.2",
    "certifi": "2026.10.18",
    "idna": "3.15",
}


def _canon(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _pins():
    """{name: (version, hash_count)} from the lockfile."""
    pins = {}
    current = None
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        match = PIN.match(line)
        if match:
            current = _canon(match.group(1))
            pins[current] = (match.group(2), 0)
        elif current and "--hash=sha256:" in line:
            version, count = pins[current]
            pins[current] = (version, count + 1)
        elif not line.startswith((" ", "\t")):
            current = None
    return pins


def _setup_py_requirements():
    """Package names from install_requires and the server and dev extras."""
    text = (ROOT / "setup.py").read_text(encoding="utf-8")
    blocks = [re.search(r"install_requires=\[(.*?)\]", text, re.S).group(1)]
    for extra in ("server", "dev"):
        blocks.append(re.search(rf"'{extra}':\s*\[(.*?)\]", text, re.S).group(1))
    names = set()
    for block in blocks:
        for spec in re.findall(r"['\"]([A-Za-z0-9][A-Za-z0-9._-]*)", block):
            names.add(_canon(spec))
    return names


def test_lockfile_exists_and_every_pin_is_hashed():
    assert LOCK.is_file(), f"no lockfile at {LOCK}"
    pins = _pins()
    assert pins, "the lockfile pins nothing"
    unhashed = sorted(name for name, (_, hashes) in pins.items() if hashes == 0)
    assert unhashed == [], f"pins with no --hash: {unhashed}"


def test_lockfile_pins_everything_setup_py_asks_for():
    missing = sorted(_setup_py_requirements() - set(_pins()))
    assert missing == [], f"setup.py asks for these, the lockfile does not pin them: {missing}"


def test_lockfile_stays_above_the_advisories_surety_found():
    pins = _pins()
    below = {
        name: pins[name][0]
        for name, floor in ADVISORY_FLOORS.items()
        if name in pins and Version(pins[name][0]) < Version(floor)
    }
    assert below == {}, f"pinned below an advisory's fixed version: {below}"
    assert "starlette" in pins, "the server's web framework is not pinned"
