"""
Scan history management for tracking and comparing audit results over time.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class ScanHistory:
    """Manages scan history storage and retrieval."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize scan history manager.

        Args:
            storage_dir: Directory to store scan history. Defaults to ~/.devaudit/history
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".devaudit" / "history"

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._ensure_index()

    def _ensure_index(self):
        """Ensure index file exists."""
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({
                "scans": [],
                "version": "1.0"
            }, indent=2))

    def _load_index(self) -> Dict:
        """Load scan index."""
        try:
            return json.loads(self.index_file.read_text())
        except Exception:
            return {"scans": [], "version": "1.0"}

    def _save_index(self, index: Dict):
        """Save scan index."""
        self.index_file.write_text(json.dumps(index, indent=2))

    def save_scan(self, results: Dict, metadata: Optional[Dict] = None) -> str:
        """
        Save a scan result to history.

        Args:
            results: Scan results dict
            metadata: Optional metadata (target_dir, etc.)

        Returns:
            Scan ID
        """
        timestamp = datetime.now().isoformat()
        scan_id = hashlib.md5(timestamp.encode()).hexdigest()[:12]

        # Create scan entry
        scan_entry = {
            "id": scan_id,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "summary": self._create_summary(results)
        }

        # Save full results to separate file
        scan_file = self.storage_dir / f"{scan_id}.json"
        scan_data = {
            "id": scan_id,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "results": results
        }
        scan_file.write_text(json.dumps(scan_data, indent=2, default=str))

        # Update index
        index = self._load_index()
        index["scans"].insert(0, scan_entry)  # Most recent first

        # Keep only last 50 scans
        if len(index["scans"]) > 50:
            # Delete old scan files
            for old_scan in index["scans"][50:]:
                old_file = self.storage_dir / f"{old_scan['id']}.json"
                if old_file.exists():
                    old_file.unlink()

            index["scans"] = index["scans"][:50]

        self._save_index(index)

        return scan_id

    def get_scan(self, scan_id: str) -> Optional[Dict]:
        """Get a specific scan by ID."""
        scan_file = self.storage_dir / f"{scan_id}.json"
        if not scan_file.exists():
            return None

        try:
            return json.loads(scan_file.read_text())
        except Exception:
            return None

    def list_scans(self, limit: int = 10) -> List[Dict]:
        """
        List recent scans.

        Args:
            limit: Maximum number of scans to return

        Returns:
            List of scan entries (id, timestamp, summary)
        """
        index = self._load_index()
        return index["scans"][:limit]

    def compare_scans(self, scan_id_1: str, scan_id_2: str) -> Dict:
        """
        Compare two scans and return differences.

        Args:
            scan_id_1: First scan ID (older)
            scan_id_2: Second scan ID (newer)

        Returns:
            Comparison results
        """
        scan1 = self.get_scan(scan_id_1)
        scan2 = self.get_scan(scan_id_2)

        if not scan1 or not scan2:
            return {"error": "One or both scans not found"}

        comparison = {
            "scan1": {
                "id": scan_id_1,
                "timestamp": scan1.get("timestamp")
            },
            "scan2": {
                "id": scan_id_2,
                "timestamp": scan2.get("timestamp")
            },
            "changes": {
                "packages": self._compare_packages(scan1["results"], scan2["results"]),
                "vulnerabilities": self._compare_vulnerabilities(scan1["results"], scan2["results"]),
                "outdated": self._compare_outdated(scan1["results"], scan2["results"]),
            },
            "summary": {}
        }

        # Create summary
        changes = comparison["changes"]
        comparison["summary"] = {
            "new_packages": len(changes["packages"].get("added", [])),
            "removed_packages": len(changes["packages"].get("removed", [])),
            "new_vulnerabilities": len(changes["vulnerabilities"].get("added", [])),
            "fixed_vulnerabilities": len(changes["vulnerabilities"].get("fixed", [])),
            "newly_outdated": len(changes["outdated"].get("added", [])),
            "updated_packages": len(changes["outdated"].get("fixed", []))
        }

        return comparison

    def _create_summary(self, results: Dict) -> Dict:
        """Create a summary of scan results for quick viewing."""
        summary = {
            "total_packages": 0,
            "outdated_packages": 0,
            "vulnerabilities": 0,
            "cleanup_items": 0,
            "tools_detected": 0
        }

        for tool_name, tool_data in results.items():
            if not isinstance(tool_data, dict):
                continue

            if tool_data.get("installed"):
                summary["tools_detected"] += 1

            packages = tool_data.get("packages", [])
            summary["total_packages"] += len(packages)

            outdated = tool_data.get("outdated_packages", [])
            summary["outdated_packages"] += len(outdated)

            vulns = tool_data.get("vulnerabilities", [])
            summary["vulnerabilities"] += len(vulns)

            cleanup = tool_data.get("cleanup_candidates", [])
            summary["cleanup_items"] += len(cleanup)

        return summary

    def _compare_packages(self, results1: Dict, results2: Dict) -> Dict:
        """Compare package lists between two scans."""
        packages1 = self._extract_all_packages(results1)
        packages2 = self._extract_all_packages(results2)

        added = [p for p in packages2 if p not in packages1]
        removed = [p for p in packages1 if p not in packages2]

        return {
            "added": added,
            "removed": removed
        }

    def _compare_vulnerabilities(self, results1: Dict, results2: Dict) -> Dict:
        """Compare vulnerabilities between two scans."""
        vulns1 = self._extract_all_vulnerabilities(results1)
        vulns2 = self._extract_all_vulnerabilities(results2)

        # Compare by package name + CVE ID
        vulns1_keys = {f"{v['package']}:{v.get('vulnerability_id', '')}" for v in vulns1}
        vulns2_keys = {f"{v['package']}:{v.get('vulnerability_id', '')}" for v in vulns2}

        added = [v for v in vulns2 if f"{v['package']}:{v.get('vulnerability_id', '')}" not in vulns1_keys]
        fixed = [v for v in vulns1 if f"{v['package']}:{v.get('vulnerability_id', '')}" not in vulns2_keys]

        return {
            "added": added,
            "fixed": fixed
        }

    def _compare_outdated(self, results1: Dict, results2: Dict) -> Dict:
        """Compare outdated packages between two scans."""
        outdated1 = self._extract_all_outdated(results1)
        outdated2 = self._extract_all_outdated(results2)

        outdated1_names = {p["name"] for p in outdated1}
        outdated2_names = {p["name"] for p in outdated2}

        added = [p for p in outdated2 if p["name"] not in outdated1_names]
        fixed = [p for p in outdated1 if p["name"] not in outdated2_names]

        return {
            "added": added,
            "fixed": fixed
        }

    def _extract_all_packages(self, results: Dict) -> List[str]:
        """Extract all package names from results."""
        packages = []
        for tool_data in results.values():
            if isinstance(tool_data, dict) and tool_data.get("packages"):
                for pkg in tool_data["packages"]:
                    if isinstance(pkg, dict):
                        packages.append(pkg.get("name", ""))
                    else:
                        packages.append(str(pkg))
        return [p for p in packages if p]  # Filter empty strings

    def _extract_all_vulnerabilities(self, results: Dict) -> List[Dict]:
        """Extract all vulnerabilities from results."""
        vulns = []
        for tool_data in results.values():
            if isinstance(tool_data, dict) and tool_data.get("vulnerabilities"):
                vulns.extend(tool_data["vulnerabilities"])
        return vulns

    def _extract_all_outdated(self, results: Dict) -> List[Dict]:
        """Extract all outdated packages from results."""
        outdated = []
        for tool_data in results.values():
            if isinstance(tool_data, dict) and tool_data.get("outdated_packages"):
                outdated.extend(tool_data["outdated_packages"])
        return outdated

    def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan from history."""
        scan_file = self.storage_dir / f"{scan_id}.json"
        if not scan_file.exists():
            return False

        try:
            scan_file.unlink()

            # Update index
            index = self._load_index()
            index["scans"] = [s for s in index["scans"] if s["id"] != scan_id]
            self._save_index(index)

            return True
        except Exception:
            return False

    def update_scan_notes(self, scan_id: str, notes: str) -> bool:
        """
        Update notes for a scan.

        Args:
            scan_id: Scan ID to update
            notes: Notes text to save

        Returns:
            True if successful, False otherwise
        """
        scan_file = self.storage_dir / f"{scan_id}.json"
        if not scan_file.exists():
            return False

        try:
            # Load scan data
            scan_data = json.loads(scan_file.read_text())

            # Update metadata
            if "metadata" not in scan_data:
                scan_data["metadata"] = {}
            scan_data["metadata"]["notes"] = notes

            # Save updated scan
            scan_file.write_text(json.dumps(scan_data, indent=2, default=str))

            # Update index
            index = self._load_index()
            for scan in index["scans"]:
                if scan["id"] == scan_id:
                    if "metadata" not in scan:
                        scan["metadata"] = {}
                    scan["metadata"]["notes"] = notes
                    break
            self._save_index(index)

            return True
        except Exception as e:
            print(f"Error updating scan notes: {e}")
            return False

    def clear_all(self):
        """Clear all scan history."""
        # Delete all scan files
        for scan_file in self.storage_dir.glob("*.json"):
            if scan_file != self.index_file:
                scan_file.unlink()

        # Reset index
        self._ensure_index()
