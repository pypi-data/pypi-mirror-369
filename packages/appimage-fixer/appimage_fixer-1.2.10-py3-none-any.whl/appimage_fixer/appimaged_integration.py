"""
AppImageD Integration Module

This module provides integration with AppImageD and AppImageLauncher to:
- Read configuration files
- Determine AppImage storage locations
- Find desktop file locations
- Monitor AppImage directories
"""

import configparser
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AppImageDIntegration:
    """Integration with AppImageD and AppImageLauncher."""

    def __init__(self):
        self.config_paths = [
            Path.home() / ".config/appimagelauncher.cfg",
            Path.home() / ".config/appimaged.cfg",
            Path("/etc/appimagelauncher.cfg"),
            Path("/etc/appimaged.cfg"),
        ]
        self.config = self._load_config()

    def _load_config(self) -> configparser.ConfigParser:
        """Load AppImageD/AppImageLauncher configuration."""
        config = configparser.ConfigParser()

        for config_path in self.config_paths:
            if config_path.exists():
                try:
                    config.read(config_path)
                    logger.info(f"Loaded config from: {config_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")

        return config

    def get_appimage_directories(self) -> List[Path]:
        """Get directories where AppImages are stored."""
        directories = []

        # Default AppImageLauncher directories
        default_dirs = [
            Path.home() / "Applications",
            Path.home() / ".local/bin",
            Path("/opt/appimages"),
            Path("/usr/local/bin"),
        ]

        # Check if AppImageLauncher config has custom destination
        if self.config.has_section("AppImageLauncher"):
            if self.config.has_option("AppImageLauncher", "destination"):
                dest = self.config.get("AppImageLauncher", "destination")
                if dest:
                    # Expand ~ to home directory
                    dest_path = Path(dest.replace("~", str(Path.home())))
                    if dest_path.exists():
                        directories.append(dest_path)

        # Check additional directories from appimagelauncherd config
        if self.config.has_section("appimagelauncherd"):
            if self.config.has_option(
                "appimagelauncherd", "additional_directories_to_watch"
            ):
                additional_dirs = self.config.get(
                    "appimagelauncherd", "additional_directories_to_watch"
                )
                if additional_dirs:
                    for dir_path in additional_dirs.split(":"):
                        dir_path = dir_path.strip()
                        if dir_path:
                            # Expand ~ to home directory
                            full_path = Path(dir_path.replace("~", str(Path.home())))
                            if full_path.exists():
                                directories.append(full_path)

        # Add default directories if no custom ones found
        if not directories:
            directories = default_dirs

        # Filter only existing directories
        directories = [d for d in directories if d.exists()]

        logger.info(f"AppImage directories: {directories}")
        return directories

    def get_desktop_file_directories(self) -> List[Path]:
        """Get directories where desktop files are stored."""
        desktop_dirs = [
            Path.home() / ".local/share/applications",
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
        ]

        # Filter only existing directories
        desktop_dirs = [d for d in desktop_dirs if d.exists()]

        logger.info(f"Desktop file directories: {desktop_dirs}")
        return desktop_dirs

    def find_appimage_files(self) -> List[Path]:
        """Find all AppImage files in configured directories."""
        appimage_files = []
        directories = self.get_appimage_directories()

        for directory in directories:
            if directory.exists():
                # Find all executable files with .AppImage extension
                for file_path in directory.rglob("*.AppImage"):
                    if file_path.is_file() and os.access(file_path, os.X_OK):
                        appimage_files.append(file_path)

                # Also find files without extension that are AppImages
                for file_path in directory.rglob("*"):
                    if (
                        file_path.is_file()
                        and os.access(file_path, os.X_OK)
                        and not file_path.suffix
                        and self._is_appimage_file(file_path)
                    ):
                        appimage_files.append(file_path)

        logger.info(f"Found {len(appimage_files)} AppImage files")
        return appimage_files

    def _is_appimage_file(self, file_path: Path) -> bool:
        """Check if a file is an AppImage by examining its magic bytes."""
        try:
            with open(file_path, "rb") as f:
                # Check for AppImage magic bytes
                magic = f.read(8)
                return magic == b"\x7fELF\x02\x01\x01"
        except Exception:
            return False

    def find_desktop_files(self) -> List[Path]:
        """Find all desktop files in configured directories."""
        desktop_files = []
        directories = self.get_desktop_file_directories()

        for directory in directories:
            if directory.exists():
                for file_path in directory.rglob("*.desktop"):
                    if file_path.is_file():
                        desktop_files.append(file_path)

        logger.info(f"Found {len(desktop_files)} desktop files")
        return desktop_files

    def get_appimage_desktop_mapping(self) -> Dict[Path, Optional[Path]]:
        """Get mapping between AppImage files and their desktop files."""
        mapping = {}
        appimage_files = self.find_appimage_files()
        desktop_files = self.find_desktop_files()

        for appimage_path in appimage_files:
            # Look for desktop file with matching name
            app_name = appimage_path.stem
            matching_desktop = None

            for desktop_path in desktop_files:
                desktop_name = desktop_path.stem
                # Check if desktop file name contains app name
                if (
                    app_name.lower() in desktop_name.lower()
                    or desktop_name.lower() in app_name.lower()
                ):
                    matching_desktop = desktop_path
                    break

            mapping[appimage_path] = matching_desktop

        logger.info(f"Created mapping for {len(mapping)} AppImage files")
        return mapping

    def get_monitoring_directories(self) -> List[Path]:
        """Get all directories that should be monitored for changes."""
        monitoring_dirs = []

        # AppImage directories
        monitoring_dirs.extend(self.get_appimage_directories())

        # Desktop file directories
        monitoring_dirs.extend(self.get_desktop_file_directories())

        # Remove duplicates and filter existing directories
        monitoring_dirs = list(set(monitoring_dirs))
        monitoring_dirs = [d for d in monitoring_dirs if d.exists()]

        logger.info(f"Monitoring directories: {monitoring_dirs}")
        return monitoring_dirs

    def is_appimaged_running(self) -> bool:
        """Check if AppImageD daemon is running."""
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "appimagelauncherd"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False

    def get_appimaged_status(self) -> Dict[str, Any]:
        """Get AppImageD daemon status information."""
        status = {
            "running": False,
            "enabled": False,
            "config_loaded": bool(self.config.sections()),
            "appimage_directories": [],
            "desktop_directories": [],
        }

        try:
            # Check if running
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "appimagelauncherd"],
                capture_output=True,
                text=True,
                check=False,
            )
            status["running"] = result.stdout.strip() == "active"

            # Check if enabled
            result = subprocess.run(
                ["systemctl", "--user", "is-enabled", "appimagelauncherd"],
                capture_output=True,
                text=True,
                check=False,
            )
            status["enabled"] = result.stdout.strip() == "enabled"

        except Exception as e:
            logger.warning(f"Failed to check AppImageD status: {e}")

        # Get directories
        status["appimage_directories"] = [
            str(d) for d in self.get_appimage_directories()
        ]
        status["desktop_directories"] = [
            str(d) for d in self.get_desktop_file_directories()
        ]

        return status


def get_appimaged_integration() -> AppImageDIntegration:
    """Get AppImageD integration instance."""
    return AppImageDIntegration()
