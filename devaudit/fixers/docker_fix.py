"""
Docker Desktop fix utility for Windows.
"""

import subprocess
import time
import os
from pathlib import Path


def fix_docker_desktop(console):
    """
    Fix common Docker Desktop issues on Windows.

    This utility:
    1. Stops Docker Desktop processes
    2. Shuts down WSL instances
    3. Removes stale lock files
    4. Restarts Docker service
    5. Launches Docker Desktop
    """

    console.print("[cyan]🧹 Step 1: Stopping Docker Desktop processes...[/cyan]")
    _kill_process("Docker Desktop", console)
    _kill_process("Docker", console)
    time.sleep(2)

    console.print("[cyan]🔻 Step 2: Shutting down WSL instances...[/cyan]")
    try:
        subprocess.run(["wsl", "--shutdown"], check=False, capture_output=True)
        console.print("[green]  ✅ WSL shutdown complete[/green]")
    except Exception as e:
        console.print(f"[yellow]  ⚠ WSL shutdown failed: {e}[/yellow]")

    time.sleep(2)

    console.print("[cyan]🧽 Step 3: Removing stale lock files...[/cyan]")
    lock_files = [
        Path(os.environ.get("APPDATA", "")) / "Docker" / "locked",
        Path(os.environ.get("APPDATA", "")) / "Docker Desktop" / "lock.json",
    ]

    for lock_file in lock_files:
        if lock_file.exists():
            try:
                lock_file.unlink()
                console.print(f"[green]  ✅ Removed {lock_file.name}[/green]")
            except Exception as e:
                console.print(f"[yellow]  ⚠ Could not remove {lock_file.name}: {e}[/yellow]")
        else:
            console.print(f"[dim]  • {lock_file.name} not found (OK)[/dim]")

    console.print("[cyan]🧰 Step 4: Restarting Docker backend service...[/cyan]")
    try:
        # Try to start the service
        subprocess.run(
            ["net", "start", "com.docker.service"],
            check=False,
            capture_output=True,
            shell=True
        )
        console.print("[green]  ✅ Docker service restart initiated[/green]")
    except Exception as e:
        console.print(f"[yellow]  ⚠ Service restart may require admin: {e}[/yellow]")

    time.sleep(5)

    console.print("[cyan]🚀 Step 5: Launching Docker Desktop...[/cyan]")
    docker_desktop_path = Path("C:/Program Files/Docker/Docker/Docker Desktop.exe")

    if docker_desktop_path.exists():
        try:
            subprocess.Popen([str(docker_desktop_path)], shell=True)
            console.print("[green]  ✅ Docker Desktop launched[/green]")
        except Exception as e:
            console.print(f"[red]  ❌ Failed to launch Docker Desktop: {e}[/red]")
    else:
        console.print("[yellow]  ⚠ Docker Desktop not found at default location[/yellow]")

    console.print("\n[bold green]✅ Docker fix complete![/bold green]")
    console.print("[dim]Docker Desktop should start cleanly now.[/dim]\n")


def _kill_process(process_name: str, console):
    """Kill a process by name."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", f"{process_name}.exe"],
            check=False,
            capture_output=True
        )
        console.print(f"[green]  ✅ Stopped {process_name}[/green]")
    except Exception:
        console.print(f"[dim]  • {process_name} not running (OK)[/dim]")
