"""
FastAPI application for local dashboard server.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import asyncio
from typing import List, Optional

# Create FastAPI app
app = FastAPI(
    title="DevAudit Dashboard",
    description="Local web dashboard for DevAudit",
    version="0.3.0"
)

# Add CORS middleware (localhost only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get dashboard directory (go up to project root: app.py -> server -> devaudit -> project root)
DASHBOARD_DIR = Path(__file__).parent.parent.parent / "dashboard" / "dist"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        message_str = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Scanner and history instances (will be initialized later)
scanner = None
scan_history = None


@app.get("/")
async def read_root():
    """Serve dashboard HTML."""
    index_file = DASHBOARD_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)
    else:
        return JSONResponse({
            "status": "dashboard_not_built",
            "message": "Dashboard frontend not built yet. Run 'npm run build' in dashboard directory.",
            "api_available": True
        })


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.3.0",
        "dashboard_ready": DASHBOARD_DIR.exists()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for now (can be used for commands later)
            await websocket.send_text(json.dumps({
                "type": "echo",
                "data": data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/scan")
async def trigger_scan(target_dir: Optional[str] = None):
    """
    Trigger a new audit scan.

    Args:
        target_dir: Optional target directory for project-specific scan

    Returns:
        Status message
    """
    if scanner is None:
        return JSONResponse({
            "status": "error",
            "message": "Scanner not initialized"
        }, status_code=500)

    # Start scan in background
    asyncio.create_task(scanner.run_scan(target_dir))

    return {
        "status": "scan_started",
        "target_dir": target_dir
    }


@app.get("/api/scan/status")
async def scan_status():
    """Get current scan status."""
    if scanner is None:
        return {
            "status": "not_initialized"
        }

    return {
        "status": scanner.status if hasattr(scanner, 'status') else "idle",
        "current_auditor": scanner.current_auditor if hasattr(scanner, 'current_auditor') else None
    }


@app.post("/api/cleanup/python/upgrade")
async def upgrade_python_packages(packages: List[str]):
    """Upgrade Python packages."""
    import subprocess

    try:
        results = []
        for package in packages:
            proc = subprocess.run(
                ["pip", "install", "--upgrade", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            results.append({
                "package": package,
                "success": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr
            })

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/api/cleanup/python/uninstall")
async def uninstall_python_packages(packages: List[str]):
    """Uninstall Python packages from global environment."""
    import subprocess

    try:
        results = []
        for package in packages:
            proc = subprocess.run(
                ["pip", "uninstall", "-y", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            results.append({
                "package": package,
                "success": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr
            })

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/api/cleanup/node/upgrade")
async def upgrade_node_packages(packages: List[str]):
    """Upgrade Node.js packages."""
    import subprocess

    try:
        results = []
        for package in packages:
            proc = subprocess.run(
                ["npm", "install", "-g", f"{package}@latest"],
                capture_output=True,
                text=True,
                timeout=120
            )
            results.append({
                "package": package,
                "success": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr
            })

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/api/cleanup/docker/remove-containers")
async def remove_docker_containers(container_ids: List[str]):
    """Remove Docker containers."""
    import subprocess

    try:
        results = []
        for container_id in container_ids:
            proc = subprocess.run(
                ["docker", "rm", "-f", container_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            results.append({
                "container_id": container_id,
                "success": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr
            })

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/api/cleanup/docker/remove-images")
async def remove_docker_images(image_ids: List[str]):
    """Remove Docker images."""
    import subprocess

    try:
        results = []
        for image_id in image_ids:
            proc = subprocess.run(
                ["docker", "rmi", "-f", image_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            results.append({
                "image_id": image_id,
                "success": proc.returncode == 0,
                "output": proc.stdout if proc.returncode == 0 else proc.stderr
            })

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/api/history")
async def get_scan_history(limit: int = 100):
    """Get scan history."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    try:
        scans = scan_history.list_scans(limit=limit)
        return {
            "status": "success",
            "scans": scans
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/api/history/latest")
async def get_latest_scan():
    """Get the most recent scan."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    try:
        latest = scan_history.get_latest_scan()
        if latest is None:
            return JSONResponse({
                "status": "not_found",
                "message": "No scans found"
            }, status_code=404)

        return {
            "status": "success",
            "scan": latest
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/api/history/{scan_id}")
async def get_scan_details(scan_id: str):
    """Get details of a specific scan."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    scan = scan_history.get_scan(scan_id)
    if scan is None:
        return JSONResponse({
            "status": "error",
            "message": "Scan not found"
        }, status_code=404)

    return {
        "status": "success",
        "scan": scan
    }


@app.get("/api/history/compare/{scan_id_1}/{scan_id_2}")
async def compare_scans(scan_id_1: str, scan_id_2: str):
    """Compare two scans."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    comparison = scan_history.compare_scans(scan_id_1, scan_id_2)

    if "error" in comparison:
        return JSONResponse({
            "status": "error",
            "message": comparison["error"]
        }, status_code=404)

    return {
        "status": "success",
        "comparison": comparison
    }


@app.delete("/api/history/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan from history."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    success = scan_history.delete_scan(scan_id)

    if not success:
        return JSONResponse({
            "status": "error",
            "message": "Failed to delete scan"
        }, status_code=404)

    return {
        "status": "success",
        "message": "Scan deleted"
    }


@app.patch("/api/history/{scan_id}/notes")
async def update_scan_notes(scan_id: str, body: dict = Body(...)):
    """Update notes for a scan."""
    if scan_history is None:
        return JSONResponse({
            "status": "error",
            "message": "History not initialized"
        }, status_code=500)

    notes = body.get("notes", "")
    success = scan_history.update_scan_notes(scan_id, notes)

    if not success:
        return JSONResponse({
            "status": "error",
            "message": "Failed to update scan notes"
        }, status_code=404)

    return {
        "status": "success",
        "message": "Notes updated"
    }


# Widget status cache
widget_status_cache = {
    "data": None,
    "timestamp": 0
}


@app.get("/api/status/quick")
async def get_quick_status():
    """
    Lightweight status endpoint for widgets.

    Returns minimal data for frequent polling by system tray/mobile widgets.
    Response is cached for 60 seconds to avoid excessive computation.
    """
    import time

    # Check cache (60 second TTL)
    cache_age = time.time() - widget_status_cache["timestamp"]
    if widget_status_cache["data"] is not None and cache_age < 60:
        return widget_status_cache["data"]

    # Get most recent scan from history
    if scan_history is None:
        return {
            "status": "unknown",
            "color": "gray",
            "summary": "Scanner not initialized",
            "risk_level": "none",
            "counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "last_scan": None,
            "auditors": {}
        }

    try:
        scans = scan_history.list_scans(limit=1)
        if not scans:
            response = {
                "status": "no_scan",
                "color": "gray",
                "summary": "No scans yet",
                "risk_level": "none",
                "counts": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "last_scan": None,
                "auditors": {}
            }
        else:
            latest_scan = scans[0]
            results = latest_scan.get("results", {})
            summary_data = latest_scan.get("summary", {})

            # Calculate status from results
            risk_counts = summary_data.get("risk_counts", {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "none": 0
            })

            vulnerabilities = summary_data.get("total_vulnerabilities", 0)

            # Determine overall status and color
            if risk_counts.get("critical", 0) > 0:
                status = "critical"
                color = "red"
                risk_level = "critical"
            elif risk_counts.get("high", 0) > 0 or vulnerabilities > 0:
                status = "warning"
                color = "yellow"
                risk_level = "high"
            elif risk_counts.get("medium", 0) > 0:
                status = "attention"
                color = "yellow"
                risk_level = "medium"
            else:
                status = "ok"
                color = "green"
                risk_level = "low"

            # Generate summary text
            issues = []
            if risk_counts.get("critical", 0) > 0:
                issues.append(f"{risk_counts['critical']} critical")
            if risk_counts.get("high", 0) > 0:
                issues.append(f"{risk_counts['high']} high")
            if vulnerabilities > 0:
                issues.append(f"{vulnerabilities} vulnerabilities")

            if issues:
                summary = ", ".join(issues)
            else:
                summary = "All systems secure"

            # Get auditor statuses
            auditor_statuses = {}
            for auditor_name, auditor_result in results.items():
                if isinstance(auditor_result, dict):
                    auditor_risk = auditor_result.get("risk_level", "none")
                    auditor_statuses[auditor_name] = "ok" if auditor_risk in ["none", "low"] else "warning"

            response = {
                "status": status,
                "color": color,
                "summary": summary,
                "risk_level": risk_level,
                "counts": {
                    "critical": risk_counts.get("critical", 0),
                    "high": risk_counts.get("high", 0),
                    "medium": risk_counts.get("medium", 0),
                    "low": risk_counts.get("low", 0)
                },
                "last_scan": latest_scan.get("timestamp"),
                "auditors": auditor_statuses
            }

        # Update cache
        widget_status_cache["data"] = response
        widget_status_cache["timestamp"] = time.time()

        return response

    except Exception as e:
        return {
            "status": "error",
            "color": "gray",
            "summary": f"Error: {str(e)}",
            "risk_level": "none",
            "counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "last_scan": None,
            "auditors": {}
        }


# Mount static files if dashboard exists
if DASHBOARD_DIR.exists():
    try:
        # Next.js uses _next directory for static assets
        next_dir = DASHBOARD_DIR / "_next"
        if next_dir.exists():
            app.mount("/_next", StaticFiles(directory=next_dir), name="next_static")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")


async def broadcast_to_clients(message: dict):
    """Helper function to broadcast messages to all WebSocket clients."""
    await manager.broadcast(message)


def start_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    """
    Start the FastAPI server.

    Args:
        host: Host to bind to
        port: Port to run on
        open_browser: Whether to open browser automatically
    """
    import uvicorn

    # Initialize scanner and history
    global scanner, scan_history
    from .scanner import RealtimeScanner
    from .history import ScanHistory
    scan_history = ScanHistory()
    scanner = RealtimeScanner(broadcast_to_clients, history_manager=scan_history)

    # Open browser if requested
    if open_browser:
        import webbrowser
        import threading
        import time

        def open_browser_delayed():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False
    )
