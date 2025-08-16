"""
Core functionality for AppImage desktop file fixing.
"""

# mypy: disable-error-code="assignment"

import os
import re
import glob
import subprocess
import shutil

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .config import get_app_config, FIXER_SETTINGS


class AppImageFixer:
    """
    Main class for fixing AppImageLauncher-generated desktop files.

    Handles:
    - Icon reference cleanup
    - Sandbox flag addition for Electron apps
    - Desktop database and icon cache updates
    """

    def __init__(
        self, home_dir: Optional[Path] = None, log_file: Optional[Path] = None
    ):
        """
        Initialize the AppImage fixer.

        Args:
            home_dir: User's home directory (defaults to current user)
            log_file: Path to log file (defaults to /tmp/appimage-fixer.log)
        """
        self.home_dir = home_dir or Path.home()
        self.apps_dir = self.home_dir / str(FIXER_SETTINGS["apps_dir_relative"])
        self.icons_dir = self.home_dir / str(FIXER_SETTINGS["icons_dir_relative"])
        self.log_file = log_file or Path(str(FIXER_SETTINGS["log_file"]))

        # Ensure directories exist
        self.apps_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        from .database import AppImageDatabase

        self.db = AppImageDatabase()

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log message with timestamp to both console and file.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)

        # Append to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Warning: Could not write to log file {self.log_file}: {e}")

    def read_desktop_file(self, file_path: Path) -> List[str]:
        """Read desktop file contents."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except Exception as e:
            self.log(f"Error reading {file_path}: {e}", "ERROR")
            return []

    def write_desktop_file(self, file_path: Path, lines: List[str]) -> bool:
        """Write desktop file contents."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            self.log(f"Error writing {file_path}: {e}", "ERROR")
            return False

    def extract_app_name(self, file_path: Path) -> Optional[str]:
        """Extract application name from desktop file."""
        lines = self.read_desktop_file(file_path)
        for line in lines:
            if line.startswith("Name="):
                return line.split("=", 1)[1].strip()
        return None

    def extract_appimage_version(self, appimage_path: Path) -> Optional[str]:
        """
        Extract version from AppImage file using ONLY static analysis.
        NO EXECUTION of the AppImage file is allowed.

        Args:
            appimage_path: Path to the AppImage file

        Returns:
            Version string if found, None otherwise
        """
        if not appimage_path.exists():
            return None

        # Method 1: Extract version from filename (safest method)
        filename = appimage_path.name
        version_match = re.search(r"(\d+\.\d+\.\d+)", filename)
        if version_match:
            return version_match.group(1)

        # Method 2: Try external tools that don't execute the AppImage
        # Try appimagetool if available
        try:
            result = subprocess.run(
                ["appimagetool", "-h", str(appimage_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                # Parse version from appimagetool output
                version_match = re.search(
                    r"version[:\s]+([0-9]+\.[0-9]+\.[0-9]+)",
                    result.stdout,
                    re.IGNORECASE,
                )
                if version_match:
                    return version_match.group(1)
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        # Method 3: Try binwalk if available
        try:
            result = subprocess.run(
                ["binwalk", str(appimage_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                # Look for version information in binwalk output
                version_match = re.search(
                    r"version[:\s]+([0-9]+\.[0-9]+\.[0-9]+)",
                    result.stdout,
                    re.IGNORECASE,
                )
                if version_match:
                    return version_match.group(1)
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        # Method 4: Try file command to get basic info
        try:
            result = subprocess.run(
                ["file", str(appimage_path)], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout:
                # Look for version information in file output
                version_match = re.search(
                    r"version[:\s]+([0-9]+\.[0-9]+\.[0-9]+)",
                    result.stdout,
                    re.IGNORECASE,
                )
                if version_match:
                    return version_match.group(1)
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        return None

    def extract_desktop_version(self, file_path: Path) -> Optional[str]:
        """
        Extract version from desktop file name or X-AppImage-Version field.

        Args:
            file_path: Path to the desktop file

        Returns:
            Version string if found, None otherwise
        """
        # First try to get version from X-AppImage-Version field
        lines = self.read_desktop_file(file_path)
        for line in lines:
            if line.startswith("X-AppImage-Version="):
                return line.split("=", 1)[1].strip()

        # If not found, try to extract from filename
        filename = file_path.name
        version_match = re.search(r"(\d+\.\d+\.\d+)", filename)
        if version_match:
            return version_match.group(1)

        # Try to extract from Name field (e.g., "Cursor (1.4.5)" or "Warp (1)")
        app_name = self.extract_app_name(file_path)
        if app_name:
            # Try standard version format first
            version_match = re.search(r"\((\d+\.\d+\.\d+)\)", app_name)
            if version_match:
                return version_match.group(1)
            # Try single number version (e.g., "Warp (1)")
            version_match = re.search(r"\((\d+)\)", app_name)
            if version_match:
                return version_match.group(1)

        return None

    def get_appimage_path_from_desktop(self, file_path: Path) -> Optional[Path]:
        """
        Extract AppImage path from desktop file Exec field.

        Args:
            file_path: Path to the desktop file

        Returns:
            Path to AppImage file if found, None otherwise
        """
        lines = self.read_desktop_file(file_path)
        for line in lines:
            if line.startswith("Exec="):
                exec_line = line.split("=", 1)[1].strip()
                # Extract path before any arguments
                appimage_path = exec_line.split()[0]
                if appimage_path.endswith(".AppImage"):
                    return Path(appimage_path)
        return None

    def compare_versions(self, desktop_file: Path) -> Dict[str, Any]:
        """
        Compare version in desktop file with version in AppImage file.

        Args:
            desktop_file: Path to the desktop file

        Returns:
            Dict with comparison results
        """
        desktop_version = self.extract_desktop_version(desktop_file)
        appimage_path = self.get_appimage_path_from_desktop(desktop_file)

        result = {
            "desktop_file": str(desktop_file),
            "desktop_version": desktop_version,
            "appimage_path": str(appimage_path) if appimage_path else None,
            "appimage_version": None,
            "versions_match": False,
            "status": "unknown",
        }

        if not desktop_version:
            result["status"] = "no_desktop_version"
            return result

        if not appimage_path or not appimage_path.exists():
            result["status"] = "appimage_not_found"
            return result

        appimage_version = self.extract_appimage_version(appimage_path)
        result["appimage_version"] = appimage_version

        if not appimage_version:
            result["status"] = "no_appimage_version"
            return result

        result["versions_match"] = desktop_version == appimage_version
        result["status"] = "match" if result["versions_match"] else "mismatch"

        return result

    def fix_icon_references(
        self, lines: List[str], icon_name: str
    ) -> Tuple[List[str], bool]:
        """Fix icon references in desktop file lines."""
        modified = False
        result_lines = []

        for line in lines:
            original_line = line

            # Fix main icon references
            if line.startswith("Icon="):
                # Remove appimagekit_ prefixes
                line = re.sub(r"^Icon=appimagekit_[^\s]*", f"Icon={icon_name}", line)
                # Clean up version numbers in parentheses
                line = re.sub(r"^Icon=.* \(.*\)", f"Icon={icon_name}", line)
                # If line still has version numbers or complex names, simplify
                if line.startswith("Icon=") and line.strip() != f"Icon={icon_name}":
                    line = f"Icon={icon_name}\n"

            if line != original_line:
                modified = True

            result_lines.append(line)

        return result_lines, modified

    def add_no_sandbox_flag(self, lines: List[str]) -> Tuple[List[str], bool]:
        """Add --no-sandbox flag to Exec lines that contain AppImage paths."""
        modified = False
        result_lines = []

        # Check if --no-sandbox is already present
        has_no_sandbox = any("--no-sandbox" in line for line in lines)
        if has_no_sandbox:
            return lines, False

        for line in lines:
            original_line = line

            # Process Exec lines that contain .AppImage
            if line.startswith("Exec=") and ".AppImage" in line:
                # Add --no-sandbox after .AppImage path
                line = re.sub(r"(\.AppImage)(\s)", r"\1 --no-sandbox\2", line)
                # Handle case where .AppImage is at the end of the line
                line = re.sub(r"(\.AppImage)$", r"\1 --no-sandbox", line)
                # Handle case where .AppImage is followed by newline
                line = re.sub(r"(\.AppImage)(\n)$", r"\1 --no-sandbox\2", line)

            if line != original_line:
                modified = True

            result_lines.append(line)

        return result_lines, modified

    def needs_fixing(
        self, file_path: Path, icon_name: str, needs_no_sandbox: bool
    ) -> bool:
        """Check if desktop file needs fixing."""
        lines = self.read_desktop_file(file_path)
        if not lines:
            return False

        content = "".join(lines)

        # Check icon
        icon_correct = f"Icon={icon_name}\n" in content

        # Check sandbox flag if needed
        sandbox_correct = True
        if needs_no_sandbox:
            sandbox_correct = "--no-sandbox" in content

        return not (icon_correct and sandbox_correct)

    def fix_desktop_file(self, file_path: Path) -> bool:
        """Fix a single desktop file."""
        if not file_path.exists():
            return False

        # Extract app name
        app_name = self.extract_app_name(file_path)
        if not app_name:
            self.log(f"Could not extract app name from {file_path}", "WARNING")
            return False

        # Get app configuration
        config = get_app_config(app_name)
        icon_name = config["icon"]
        needs_no_sandbox = config["needs_no_sandbox"]

        # Check if fixing is needed
        if not self.needs_fixing(file_path, icon_name, needs_no_sandbox):
            return False

        self.log(f"Fixing {file_path} for {app_name}")

        # Create backup
        backup_path = file_path.with_suffix(
            file_path.suffix + str(FIXER_SETTINGS["backup_extension"])
        )
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            self.log(f"Error creating backup: {e}", "ERROR")
            return False

        # Read and fix file
        lines = self.read_desktop_file(file_path)
        if not lines:
            return False

        # Fix icons
        lines, icon_modified = self.fix_icon_references(lines, icon_name)

        # Add sandbox flag if needed
        sandbox_modified = False
        if needs_no_sandbox:
            lines, sandbox_modified = self.add_no_sandbox_flag(lines)
            if sandbox_modified:
                self.log(f"Added --no-sandbox flag for {app_name}")

        # Write fixed file
        if icon_modified or sandbox_modified:
            if self.write_desktop_file(file_path, lines):
                self.log(f"Fixed icon reference in {file_path} to use: {icon_name}")
                return True

        return False

    def update_desktop_database(self) -> None:
        """Update desktop database."""
        try:
            result = subprocess.run(
                ["update-desktop-database", str(self.apps_dir)],
                capture_output=True,
                check=False,
                text=True,
            )
            if result.returncode == 0:
                self.log("Updated desktop database")
            else:
                self.log(f"Desktop database update warning: {result.stderr}", "WARNING")
        except Exception as e:
            self.log(f"Error updating desktop database: {e}", "ERROR")

    def update_icon_cache(self) -> None:
        """Update GTK icon cache."""
        if self.icons_dir.exists():
            try:
                result = subprocess.run(
                    ["gtk-update-icon-cache", str(self.icons_dir)],
                    capture_output=True,
                    check=False,
                    text=True,
                )
                if result.returncode == 0:
                    self.log("Updated icon cache")
                else:
                    self.log(f"Icon cache update warning: {result.stderr}", "WARNING")
            except Exception as e:
                self.log(f"Error updating icon cache: {e}", "ERROR")

    def find_appimage_files(self) -> List[Path]:  # type: ignore
        """Find all AppImageLauncher generated desktop files with smart integration."""
        from .appimaged_integration import get_appimaged_integration

        integration = get_appimaged_integration()
        status = integration.get_appimaged_status()

        # Check if AppImageLauncher/appimaged integration is available
        if status["config_loaded"] or status["running"]:
            self.log("Using AppImageLauncher/appimaged integration", "INFO")
            desktop_files = integration.find_desktop_files()

            # Filter only AppImageLauncher files
            appimage_files = []
            for file_path in desktop_files:
                if "appimagekit_" in file_path.name or "AppImage" in file_path.name:
                    appimage_files.append(file_path)

            self.log(
                f"Found {len(appimage_files)} AppImageLauncher desktop files via integration"
            )
            return appimage_files
        else:
            # Fallback to default directory
            self.log(
                "No AppImageLauncher/appimaged integration found, using default ~/Applications",
                "INFO",
            )
            default_dir = Path.home() / "Applications"

            if not default_dir.exists():
                self.log(f"Default directory {default_dir} does not exist", "WARNING")
                return []

            # Look for desktop files in default directory
            pattern = str(default_dir / "*.desktop")
            desktop_files = glob.glob(pattern)

            # Also check for appimagekit_ files in standard location
            standard_pattern = str(self.apps_dir / "appimagekit_*.desktop")
            standard_files = glob.glob(standard_pattern)

            all_files = []  # type: ignore[assignment]
            for f in desktop_files + standard_files:
                if f:
                    all_files.append(Path(f))

            self.log(f"Found {len(all_files)} desktop files in default locations")
            return all_files

    def find_appimage_executables(self) -> List[Path]:
        """Find all AppImage executable files with smart integration."""
        from .appimaged_integration import get_appimaged_integration

        integration = get_appimaged_integration()
        status = integration.get_appimaged_status()

        # Check if AppImageLauncher/appimaged integration is available
        if status["config_loaded"] or status["running"]:
            self.log(
                "Using AppImageLauncher/appimaged integration for executable search",
                "INFO",
            )
            return integration.find_appimage_files()
        else:
            # Fallback to default directories
            self.log(
                "No AppImageLauncher/appimaged integration found, "
                "using default directories",
                "INFO",
            )
            default_dirs = [
                Path.home() / "Applications",
                Path.home() / ".local/bin",
                Path("/opt/appimages"),
                Path("/usr/local/bin"),
            ]

            appimage_files = []
            for directory in default_dirs:
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

            self.log(
                f"Found {len(appimage_files)} AppImage files in default directories"
            )
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

    def scan_and_update_database(self) -> Dict[str, Any]:
        """Scan AppImage files and update database."""
        desktop_files = self.find_appimage_files()
        scanned_count = 0
        updated_count = 0

        for desktop_file in desktop_files:
            appimage_path = self.get_appimage_path_from_desktop(desktop_file)
            if not appimage_path or not appimage_path.exists():
                continue

            app_name = self.extract_app_name(desktop_file)
            if not app_name:
                continue

            # Calculate checksum
            checksum = self.db.calculate_checksum(appimage_path)

            # Extract version
            version = self.extract_appimage_version(appimage_path)

            # Update database
            data = {
                "name": app_name,
                "version": version,
                "checksum": checksum,
                "file_path": str(appimage_path),
                "desktop_file": str(desktop_file),
                "appimage_id": None,  # Can be added later
            }

            if self.db.add_or_update_appimage(data):
                updated_count += 1
            scanned_count += 1

        # Clean up orphaned records
        existing_paths = []
        for f in desktop_files:
            path = self.get_appimage_path_from_desktop(f)
            if path and path.exists():
                existing_paths.append(path)
        cleaned_count = self.db.cleanup_orphaned(existing_paths)

        return {
            "scanned": scanned_count,
            "updated": updated_count,
            "cleaned": cleaned_count,
        }

    def compare_versions_with_db(self, desktop_file: Path) -> Dict[str, Any]:
        """Compare versions using database."""
        appimage_path = self.get_appimage_path_from_desktop(desktop_file)
        if not appimage_path or not appimage_path.exists():
            return {"status": "appimage_not_found"}

        # Get data from database
        checksum = self.db.calculate_checksum(appimage_path)
        db_record = self.db.get_by_checksum(checksum)

        desktop_version = self.extract_desktop_version(desktop_file)
        appimage_version = db_record["version"] if db_record else None

        # Determine if versions match
        if desktop_version is None and appimage_version is None:
            versions_match = False
            status = "no_version"
        elif desktop_version is None or appimage_version is None:
            versions_match = False
            status = "no_version"
        else:
            versions_match = desktop_version == appimage_version
            status = "match" if versions_match else "mismatch"

        return {
            "desktop_version": desktop_version,
            "appimage_version": appimage_version,
            "versions_match": versions_match,
            "status": status,
        }

    def run(self) -> Dict[str, Any]:
        """
        Main execution function with smart AppImageD integration.

        Logic:
        1. Check for AppImageLauncher/appimaged integration
        2. Use integration if available, fallback to ~/Applications
        3. Always check icons and parameters for all found files
        4. Update database with all findings
        5. Fix any issues found

        Returns:
            Dict with execution statistics
        """
        self.log("Starting AppImage desktop file fixer with smart integration...")

        # Update database first
        db_result = self.scan_and_update_database()
        self.log(
            f"Database updated: {db_result['updated']} records, "
            f"cleaned: {db_result['cleaned']} orphaned"
        )

        desktop_files = self.find_appimage_files()

        if not desktop_files:
            self.log("No AppImage desktop files found")
            return {
                "files_found": 0,
                "files_fixed": 0,
                "db_scanned": db_result["scanned"],
                "db_updated": db_result["updated"],
                "db_cleaned": db_result["cleaned"],
                "success": True,
            }

        self.log(f"Found {len(desktop_files)} AppImage desktop files to check")

        changes_made = False
        files_fixed = 0

        # Always check and fix icons and parameters for all found files
        for file_path in desktop_files:
            if self.fix_desktop_file(file_path):
                changes_made = True
                files_fixed += 1

        # Update system databases if changes were made
        if changes_made:
            self.log("Changes made, refreshing desktop database...")
            self.update_desktop_database()
            self.update_icon_cache()
            self.log("Desktop integration updated successfully")
        else:
            self.log("No changes needed")

        return {
            "files_found": len(desktop_files),
            "files_fixed": files_fixed,
            "success": True,
            "changes_made": changes_made,
            "db_scanned": db_result["scanned"],
            "db_updated": db_result["updated"],
            "db_cleaned": db_result["cleaned"],
        }
