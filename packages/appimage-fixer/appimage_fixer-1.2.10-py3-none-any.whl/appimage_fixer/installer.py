"""
Installation utilities for systemd service setup.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

from .config import FIXER_SETTINGS


def get_systemd_user_dir() -> Path:
    """Get the systemd user directory."""
    return Path.home() / ".config/systemd/user"


def get_executable_path() -> Path:
    """Get the path to the appimage-fixer executable."""
    # Try to find the executable in PATH
    executable = shutil.which("appimage-fixer")
    if executable:
        return Path(executable)

    # If not in PATH, assume it's in ~/.local/bin
    local_bin = Path.home() / ".local/bin/appimage-fixer"
    if local_bin.exists():
        return local_bin

    # Last resort: use python -m
    python_exe = sys.executable
    return Path(python_exe)


def create_service_file() -> str:
    """Create the systemd service file content."""
    executable = get_executable_path()

    # If we're using python -m, adjust the command
    if executable.name.endswith("python") or executable.name.endswith("python3"):
        exec_start = f"{executable} -m appimage_fixer.cli run"
    else:
        exec_start = f"{executable} run"

    return dedent(
        f"""
        [Unit]
        Description=AppImage Fixer - Fix AppImageLauncher desktop files
        After=graphical-session.target

        [Service]
        Type=oneshot
        ExecStart={exec_start}
        StandardOutput=journal
        StandardError=journal

        # Environment
        Environment=HOME=%h
        Environment=XDG_DATA_HOME=%h/.local/share

        # Security settings
        NoNewPrivileges=yes
        PrivateTmp=yes
        ProtectSystem=strict
        ProtectHome=no
        ReadWritePaths=%h/.local/share/applications %h/.local/share/icons /tmp
    """
    ).strip()


def create_timer_file() -> str:
    """Create the systemd timer file content."""
    interval = FIXER_SETTINGS["scan_interval_seconds"]

    return dedent(
        f"""
        [Unit]
        Description=AppImage Fixer Timer - Run every {interval} seconds
        Requires=appimage-fixer.service

        [Timer]
        OnBootSec={interval}
        OnUnitActiveSec={interval}
        Persistent=true

        [Install]
        WantedBy=timers.target
    """
    ).strip()


def install_systemd_service() -> None:
    """Install the systemd user service and timer."""
    systemd_dir = get_systemd_user_dir()
    systemd_dir.mkdir(parents=True, exist_ok=True)

    service_file = systemd_dir / "appimage-fixer.service"
    timer_file = systemd_dir / "appimage-fixer.timer"

    # Create service file
    with open(service_file, "w") as f:
        f.write(create_service_file())

    # Create timer file
    with open(timer_file, "w") as f:
        f.write(create_timer_file())

    print(f"Created service file: {service_file}")
    print(f"Created timer file: {timer_file}")

    # Reload systemd and enable/start the timer
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(
            ["systemctl", "--user", "enable", "appimage-fixer.timer"], check=True
        )
        subprocess.run(
            ["systemctl", "--user", "start", "appimage-fixer.timer"], check=True
        )
        print("✓ Systemd service enabled and started")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to setup systemd service: {e}")


def uninstall_systemd_service() -> None:
    """Uninstall the systemd user service and timer."""
    systemd_dir = get_systemd_user_dir()
    service_file = systemd_dir / "appimage-fixer.service"
    timer_file = systemd_dir / "appimage-fixer.timer"

    # Stop and disable the timer/service
    try:
        subprocess.run(
            ["systemctl", "--user", "stop", "appimage-fixer.timer"],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["systemctl", "--user", "disable", "appimage-fixer.timer"],
            check=False,
            capture_output=True,
        )
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        print("✓ Systemd service stopped and disabled")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to stop service: {e}")

    # Remove files
    if service_file.exists():
        service_file.unlink()
        print(f"Removed service file: {service_file}")

    if timer_file.exists():
        timer_file.unlink()
        print(f"Removed timer file: {timer_file}")


def check_service_status() -> dict:
    """Check the status of the appimage-fixer service."""
    try:
        # Check timer status
        timer_result = subprocess.run(
            ["systemctl", "--user", "is-active", "appimage-fixer.timer"],
            capture_output=True,
            text=True,
        )
        timer_active = timer_result.stdout.strip() == "active"

        # Check service status
        subprocess.run(
            [
                "systemctl",
                "--user",
                "show",
                "appimage-fixer.service",
                "--property=ExecMainStatus",
            ],
            capture_output=True,
            text=True,
        )

        return {
            "timer_active": timer_active,
            "service_installed": (
                get_systemd_user_dir() / "appimage-fixer.service"
            ).exists(),
            "timer_installed": (
                get_systemd_user_dir() / "appimage-fixer.timer"
            ).exists(),
        }
    except subprocess.CalledProcessError:
        return {
            "timer_active": False,
            "service_installed": False,
            "timer_installed": False,
        }
