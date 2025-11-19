"""
Real-time scanner that streams audit results via WebSocket.
"""

from ..auditors import (
    PythonAuditor,
    NodeAuditor,
    DockerAuditor,
    GoAuditor,
    SystemAuditor,
)
from ..auditors.system_auditors import BIOSAuditor
import asyncio
from typing import Dict, Callable, Optional
from pathlib import Path


class RealtimeScanner:
    """Scanner that broadcasts results in real-time via WebSocket."""

    def __init__(self, broadcast_callback: Callable, history_manager=None):
        """
        Initialize scanner with broadcast callback.

        Args:
            broadcast_callback: Async function to broadcast messages
            history_manager: Optional ScanHistory instance for saving results
        """
        self.broadcast = broadcast_callback
        self.history = history_manager
        self.status = "idle"
        self.current_auditor = None
        self.auditors = [
            PythonAuditor(),
            NodeAuditor(),
            DockerAuditor(),
            GoAuditor(),
            SystemAuditor(),
            BIOSAuditor(),
        ]

    async def run_scan(self, target_dir: Optional[str] = None):
        """
        Run full audit scan and broadcast results in real-time.

        Args:
            target_dir: Optional target directory for project-specific scan
        """
        self.status = "scanning"
        results = {}

        # Update auditors with target directory if provided
        if target_dir:
            target_path = Path(target_dir)
            for auditor in self.auditors:
                auditor.target_dir = target_path

            await self.broadcast({
                "type": "scan_started",
                "target_dir": str(target_dir),
                "total_auditors": len(self.auditors)
            })
        else:
            await self.broadcast({
                "type": "scan_started",
                "target_dir": None,
                "total_auditors": len(self.auditors)
            })

        # Run each auditor and broadcast results immediately
        for index, auditor in enumerate(self.auditors, 1):
            self.current_auditor = auditor.name

            try:
                # Broadcast scanning status
                await self.broadcast({
                    "type": "auditor_started",
                    "auditor": auditor.name,
                    "progress": {
                        "current": index,
                        "total": len(self.auditors)
                    }
                })

                # Run audit in thread pool to avoid blocking
                result = await asyncio.to_thread(auditor.audit)
                results[auditor.name] = result

                # Broadcast auditor result
                await self.broadcast({
                    "type": "auditor_completed",
                    "auditor": auditor.name,
                    "data": result,
                    "progress": {
                        "current": index,
                        "total": len(self.auditors)
                    }
                })

            except Exception as e:
                error_msg = str(e)
                results[auditor.name] = {
                    "installed": False,
                    "error": error_msg
                }

                await self.broadcast({
                    "type": "auditor_error",
                    "auditor": auditor.name,
                    "error": error_msg,
                    "progress": {
                        "current": index,
                        "total": len(self.auditors)
                    }
                })

        # Save to history if history manager is available
        scan_id = None
        if self.history:
            try:
                metadata = {}
                if target_dir:
                    metadata["target_dir"] = str(target_dir)

                scan_id = self.history.save_scan(results, metadata)
            except Exception as e:
                print(f"Warning: Failed to save scan to history: {e}")

        # Broadcast scan completion
        self.status = "idle"
        self.current_auditor = None

        await self.broadcast({
            "type": "scan_completed",
            "results": results,
            "summary": self._generate_summary(results),
            "scan_id": scan_id
        })

        return results

    def _generate_summary(self, results: Dict) -> Dict:
        """
        Generate summary statistics from scan results.

        Args:
            results: Complete scan results

        Returns:
            Summary statistics dictionary
        """
        tools_detected = sum(1 for r in results.values() if r.get('installed', False))
        total_tools = len(results)

        total_packages = 0
        total_outdated = 0
        total_cleanup = 0

        for tool_result in results.values():
            if isinstance(tool_result, dict):
                packages = tool_result.get('packages', [])
                total_packages += len(packages) if isinstance(packages, list) else 0

                outdated = tool_result.get('outdated_packages', [])
                total_outdated += len(outdated) if isinstance(outdated, list) else 0

                cleanup = tool_result.get('cleanup_candidates', [])
                total_cleanup += len(cleanup) if isinstance(cleanup, list) else 0

        return {
            "tools_detected": tools_detected,
            "total_tools": total_tools,
            "total_packages": total_packages,
            "total_outdated_packages": total_outdated,
            "total_cleanup_candidates": total_cleanup
        }
