"""
Configuration module for AppImage Fixer

Defines universal settings for AppImage desktop file fixing.
"""

from typing import Dict, Any

# Settings for the fixer behavior
FIXER_SETTINGS = {
    "log_file": "/tmp/appimage-fixer.log",
    "backup_extension": ".bak",
    "scan_interval_seconds": 30,
    "apps_dir_relative": ".local/share/applications",
    "icons_dir_relative": ".local/share/icons/hicolor",
}


def get_app_config(app_name: str) -> Dict[str, Any]:
    """
    Get universal configuration for any AppImage application.

    Args:
        app_name: Name of the application

    Returns:
        Dict containing icon name and sandbox needs
    """
    # Extract first word as icon name
    if not app_name.strip():
        first_word = "unknown"
    else:
        first_word = app_name.split()[0].lower()

    # Universal logic: most modern apps need --no-sandbox
    # This is a reasonable default for Electron and other modern frameworks
    needs_no_sandbox = True

    return {
        "icon": first_word,
        "needs_no_sandbox": needs_no_sandbox,
        "description": f"AppImage application: {app_name}",
    }
