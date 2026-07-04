"""
Copy build-time assets INTO the devaudit package so they ship in the wheel.

Why this exists: the dashboard build (dashboard/dist/) and the educational
content (docs/concepts/*.md) live at the repo root, OUTSIDE the devaudit/
package. Files outside a package cannot ship in a wheel, so every wheel ever
built silently contained neither - the flagship dashboard and the education
layer never reached a real pip install. This script copies both into the
package (devaudit/dashboard/dist/ and devaudit/educational/content/), where
setup.py's package_data and MANIFEST.in already point. CI runs it before
`python -m build` and then asserts the wheel RECORD actually contains both.

Run from anywhere: python scripts/prepare_package_assets.py
"""

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_SRC = REPO_ROOT / "dashboard" / "dist"
DASHBOARD_DEST = REPO_ROOT / "devaudit" / "dashboard" / "dist"
CONCEPTS_SRC = REPO_ROOT / "docs" / "concepts"
CONCEPTS_DEST = REPO_ROOT / "devaudit" / "educational" / "content"


def copy_tree(src: Path, dest: Path, pattern: str = "**/*") -> int:
    if not src.is_dir():
        print(f"[!] Source missing: {src}")
        return -1
    if dest.exists():
        shutil.rmtree(dest)
    copied = 0
    for item in sorted(src.glob(pattern)):
        if item.is_file():
            target = dest / item.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            copied += 1
    return copied


def main() -> int:
    dash = copy_tree(DASHBOARD_SRC, DASHBOARD_DEST)
    if dash < 0:
        print("[!] Build the dashboard first: cd dashboard && npm install && npm run build")
        return 1
    print(f"[+] Dashboard: {dash} files -> {DASHBOARD_DEST.relative_to(REPO_ROOT)}")

    docs = copy_tree(CONCEPTS_SRC, CONCEPTS_DEST, "*.md")
    if docs < 0:
        return 1
    print(f"[+] Educational content: {docs} files -> {CONCEPTS_DEST.relative_to(REPO_ROOT)}")

    if dash == 0 or docs == 0:
        print("[!] A copy produced 0 files - refusing to call that success.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
