"""
Docker environment auditor.
"""

import re
from typing import Dict, List, Optional
from .base import BaseAuditor
from devaudit.educational import get_educational_content


class DockerAuditor(BaseAuditor):
    """Audits Docker installations, containers, and images."""

    def __init__(self, target_dir=None):
        super().__init__(target_dir)
        self.name = "Docker"
        self.large_image_threshold_mb = 500  # Images larger than this are cleanup candidates

    def is_installed(self) -> bool:
        """Check if Docker is installed."""
        self.installed = self.check_command_exists("docker")
        return self.installed

    def get_version(self) -> Optional[str]:
        """Get Docker version."""
        if not self.is_installed():
            return None

        stdout, _, rc = self.run_command(["docker", "--version"])
        if rc == 0 and stdout.strip():
            self.version = stdout.strip()
            return self.version
        return None

    def audit(self) -> Dict:
        """Perform full Docker audit."""
        result = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "containers": [],
            "images": [],
            "cleanup_candidates": [],
            "warnings": [],
            "stats": {
                "total_containers": 0,
                "running_containers": 0,
                "stopped_containers": 0,
                "total_images": 0,
                "dangling_images": 0,
            },
        }

        if not result["installed"]:
            return result

        # Check if Docker daemon is running
        stdout, stderr, rc = self.run_command(["docker", "info"], timeout=10)
        if rc != 0:
            result["warnings"].append("Docker daemon is not running")
            return result

        # Get containers
        stdout, _, rc = self.run_command(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"]
        )
        if rc == 0 and stdout:
            containers = self._parse_containers(stdout)
            result["containers"] = containers
            result["stats"]["total_containers"] = len(containers)
            result["stats"]["running_containers"] = sum(1 for c in containers if c["status"].startswith("Up"))
            result["stats"]["stopped_containers"] = sum(1 for c in containers if not c["status"].startswith("Up"))

        # Get images
        stdout, _, rc = self.run_command(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}"]
        )
        if rc == 0 and stdout:
            images = self._parse_images(stdout)
            result["images"] = images
            result["stats"]["total_images"] = len(images)

        # Find dangling images
        stdout, _, rc = self.run_command(["docker", "images", "-f", "dangling=true", "-q"])
        if rc == 0 and stdout:
            dangling = stdout.strip().split("\n")
            result["stats"]["dangling_images"] = len([i for i in dangling if i])

        # Generate cleanup candidates
        large_images = [img for img in result["images"] if img["size_mb"] >= self.large_image_threshold_mb]
        if large_images:
            result["cleanup_candidates"].append({
                "type": "large_images",
                "count": len(large_images),
                "description": f"{len(large_images)} Docker images larger than {self.large_image_threshold_mb}MB",
                "total_size_mb": sum(img["size_mb"] for img in large_images),
            })

        if result["stats"]["dangling_images"] > 0:
            result["cleanup_candidates"].append({
                "type": "dangling_images",
                "count": result["stats"]["dangling_images"],
                "description": f"{result['stats']['dangling_images']} dangling Docker images",
            })

        stopped_containers = [c for c in result["containers"] if not c["status"].startswith("Up")]
        if len(stopped_containers) > 0:
            result["cleanup_candidates"].append({
                "type": "stopped_containers",
                "count": len(stopped_containers),
                "description": f"{len(stopped_containers)} stopped Docker containers",
            })

        return result

    def _parse_containers(self, output: str) -> List[Dict]:
        """Parse docker ps output."""
        containers = []
        lines = output.strip().split("\n")

        for line in lines:
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                containers.append({
                    "name": parts[0],
                    "image": parts[1],
                    "status": parts[2],
                    "ports": parts[3] if len(parts) > 3 else "",
                })

        return containers

    def _parse_images(self, output: str) -> List[Dict]:
        """Parse docker images output."""
        images = []
        lines = output.strip().split("\n")

        for line in lines:
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                size_mb = self._parse_size_to_mb(parts[2])
                images.append({
                    "name": parts[0],
                    "id": parts[1],
                    "size": parts[2],
                    "size_mb": size_mb,
                })

        return images

    def _parse_size_to_mb(self, size_str: str) -> float:
        """Convert Docker size string to MB."""
        size_str = size_str.strip()

        # Match patterns like "1.5GB", "500MB", "123kB"
        match = re.match(r'([\d.]+)\s*([KMGT]?B)', size_str, re.IGNORECASE)
        if not match:
            return 0.0

        value = float(match.group(1))
        unit = match.group(2).upper()

        multipliers = {
            'B': 1 / (1024 * 1024),
            'KB': 1 / 1024,
            'MB': 1,
            'GB': 1024,
            'TB': 1024 * 1024,
        }

        return value * multipliers.get(unit, 0)

    def get_educational_content(self) -> Dict[str, str]:
        """
        Get educational content about Docker cleanup.

        Returns educational content from docs/concepts/docker-cleanup.md.
        """
        return get_educational_content("docker-cleanup", fallback={
            "what_is_it": "Docker cleanup removes unused containers, images, volumes, and networks to reclaim disk space.",
            "why_it_matters": "Docker accumulates gigabytes of unused data over time—stopped containers, dangling images, and orphaned volumes consume disk space unnecessarily.",
            "when_to_update": "Clean up Docker resources weekly or when disk space is low. Always verify what will be removed before cleanup.",
            "when_to_skip": "Skip cleanup if you need stopped containers for logs, or if images will be reused soon.",
            "how_to_fix": "Use 'docker system prune' for safe cleanup (containers and dangling images), or 'docker system prune -a --volumes' for aggressive cleanup (removes ALL unused resources).",
            "risks": "Removing volumes deletes data permanently. Always backup important volumes before cleanup.",
            "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/docker-cleanup.md"
        })
