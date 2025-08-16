import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import shutil

from appimage_fixer.core import AppImageFixer


class TestAppImageFixer:
    """Test AppImageFixer core functionality with AppImageD integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = AppImageFixer()

    def test_init(self):
        """Test initialization."""
        assert self.fixer is not None
        assert hasattr(self.fixer, "apps_dir")
        assert hasattr(self.fixer, "db")

    def test_init_with_custom_paths(self):
        """Test initialization with custom paths."""
        temp_dir = tempfile.mkdtemp()
        try:
            custom_home = Path(temp_dir) / "custom_home"
            custom_log = Path(temp_dir) / "custom.log"

            fixer = AppImageFixer(home_dir=custom_home, log_file=custom_log)

            assert fixer.home_dir == custom_home
            assert fixer.log_file == custom_log
        finally:
            shutil.rmtree(temp_dir)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "[Desktop Entry]\nName=Test App\nExec=/test/app.AppImage\nIcon=test-icon"
        ),
    )
    def test_read_desktop_file_success(self, mock_file):
        """Test reading desktop file successfully."""
        result = self.fixer.read_desktop_file(Path("/test/app.desktop"))
        assert len(result) == 4  # Including newlines
        assert "[Desktop Entry]" in result[0]
        assert "Name=Test App" in result[1]

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_read_desktop_file_error(self, mock_file):
        """Test reading desktop file with error."""
        result = self.fixer.read_desktop_file(Path("/nonexistent/app.desktop"))
        assert result == []

    @patch("builtins.open", new_callable=mock_open)
    def test_write_desktop_file_success(self, mock_file):
        """Test writing desktop file successfully."""
        lines = ["[Desktop Entry]\n", "Name=Test App\n", "Exec=/test/app.AppImage\n"]
        result = self.fixer.write_desktop_file(Path("/test/app.desktop"), lines)
        assert result is True
        mock_file.assert_called_once()

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_write_desktop_file_error(self, mock_file):
        """Test writing desktop file with error."""
        lines = ["[Desktop Entry]\n", "Name=Test App\n"]
        result = self.fixer.write_desktop_file(Path("/protected/app.desktop"), lines)
        assert result is False

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_extract_app_name_success(self, mock_read):
        """Test extracting app name successfully."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test Application\n",
            "Exec=/test/app.AppImage\n",
        ]
        result = self.fixer.extract_app_name(Path("/test/app.desktop"))
        assert result == "Test Application"

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_extract_app_name_not_found(self, mock_read):
        """Test extracting app name when not found."""
        mock_read.return_value = ["[Desktop Entry]\n", "Exec=/test/app.AppImage\n"]
        result = self.fixer.extract_app_name(Path("/test/app.desktop"))
        assert result is None

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_extract_desktop_version_from_x_appimage_version(self, mock_read):
        """Test extracting version from X-AppImage-Version field."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "X-AppImage-Version=1.2.3\n",
            "Exec=/test/app.AppImage\n",
        ]
        result = self.fixer.extract_desktop_version(Path("/test/app.desktop"))
        assert result == "1.2.3"

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_extract_desktop_version_from_name_with_version(self, mock_read):
        """Test extracting version from Name field with version."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App (1.2.3)\n",
            "Exec=/test/app.AppImage\n",
        ]
        result = self.fixer.extract_desktop_version(Path("/test/app.desktop"))
        assert result == "1.2.3"

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_extract_desktop_version_from_filename(self, mock_read):
        """Test extracting version from filename."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
        ]
        result = self.fixer.extract_desktop_version(Path("/test/TestApp-1.2.3.desktop"))
        assert result == "1.2.3"

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_get_appimage_path_from_desktop_success(self, mock_read):
        """Test getting AppImage path from desktop file."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/home/user/Applications/TestApp.AppImage --no-sandbox\n",
            "Icon=test-icon\n",
        ]
        result = self.fixer.get_appimage_path_from_desktop(Path("/test/app.desktop"))
        assert result == Path("/home/user/Applications/TestApp.AppImage")

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_get_appimage_path_from_desktop_no_exec(self, mock_read):
        """Test getting AppImage path when Exec field is missing."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Icon=test-icon\n",
        ]
        result = self.fixer.get_appimage_path_from_desktop(Path("/test/app.desktop"))
        assert result is None

    @patch("pathlib.Path.exists", return_value=True)
    def test_extract_appimage_version_from_filename(self, mock_exists):
        """Test extracting version from AppImage filename."""
        appimage_path = Path("/test/TestApp-1.2.3-x86_64.AppImage")
        result = self.fixer.extract_appimage_version(appimage_path)
        assert result == "1.2.3"

    @patch("pathlib.Path.exists", return_value=True)
    def test_extract_appimage_version_no_version_in_filename(self, mock_exists):
        """Test extracting version when no version in filename."""
        appimage_path = Path("/test/TestApp.AppImage")
        result = self.fixer.extract_appimage_version(appimage_path)
        assert result is None

    def test_fix_icon_references_with_icon(self):
        """Test fixing icon references when icon is provided."""
        lines = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=old-icon\n",
        ]
        result_lines, changed = self.fixer.fix_icon_references(lines, "new-icon")

        assert changed is True
        assert "Icon=new-icon" in result_lines[3]

    def test_fix_icon_references_no_icon_field(self):
        """Test fixing icon references when no Icon field exists."""
        lines = ["[Desktop Entry]\n", "Name=Test App\n", "Exec=/test/app.AppImage\n"]
        result_lines, changed = self.fixer.fix_icon_references(lines, "new-icon")

        assert changed is False  # No Icon field to fix
        assert len(result_lines) == 3  # No Icon field added

    def test_fix_icon_references_icon_already_correct(self):
        """Test fixing icon references when icon is already correct."""
        lines = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=correct-icon\n",
        ]
        result_lines, changed = self.fixer.fix_icon_references(lines, "correct-icon")

        assert changed is False
        assert "Icon=correct-icon" in result_lines[3]

    def test_add_no_sandbox_flag_with_exec(self):
        """Test adding --no-sandbox flag to Exec field."""
        lines = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=test-icon\n",
        ]
        result_lines, changed = self.fixer.add_no_sandbox_flag(lines)

        assert changed is True
        assert "Exec=/test/app.AppImage --no-sandbox" in result_lines[2]

    def test_add_no_sandbox_flag_already_present(self):
        """Test adding --no-sandbox flag when already present."""
        lines = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage --no-sandbox\n",
            "Icon=test-icon\n",
        ]
        result_lines, changed = self.fixer.add_no_sandbox_flag(lines)

        assert changed is False
        assert "Exec=/test/app.AppImage --no-sandbox" in result_lines[2]

    def test_add_no_sandbox_flag_no_exec(self):
        """Test adding --no-sandbox flag when no Exec field."""
        lines = ["[Desktop Entry]\n", "Name=Test App\n", "Icon=test-icon\n"]
        result_lines, changed = self.fixer.add_no_sandbox_flag(lines)

        assert changed is False
        assert len(result_lines) == 3  # No Exec field added

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    def test_needs_fixing_icon_mismatch(self, mock_extract_name, mock_read):
        """Test needs_fixing when icon needs to be fixed."""
        mock_extract_name.return_value = "Test App"
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=wrong-icon\n",
        ]

        result = self.fixer.needs_fixing(
            Path("/test/app.desktop"), "correct-icon", True
        )
        assert result is True

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    def test_needs_fixing_no_sandbox_missing(self, mock_extract_name, mock_read):
        """Test needs_fixing when --no-sandbox flag is missing."""
        mock_extract_name.return_value = "Test App"
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=correct-icon\n",
        ]

        result = self.fixer.needs_fixing(
            Path("/test/app.desktop"), "correct-icon", True
        )
        assert result is True

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    def test_needs_fixing_no_changes_needed(self, mock_extract_name, mock_read):
        """Test needs_fixing when no changes are needed."""
        mock_extract_name.return_value = "Test App"
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage --no-sandbox\n",
            "Icon=correct-icon\n",
        ]

        result = self.fixer.needs_fixing(
            Path("/test/app.desktop"), "correct-icon", True
        )
        assert result is False

    @patch("appimage_fixer.core.AppImageFixer.needs_fixing")
    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.write_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.config.get_app_config")
    def test_fix_desktop_file_success(
        self, mock_get_config, mock_extract_name, mock_write, mock_read, mock_needs
    ):
        """Test fixing desktop file successfully."""
        mock_extract_name.return_value = "Test App"
        mock_get_config.return_value = {"icon": "test-icon", "needs_no_sandbox": True}
        mock_needs.return_value = True
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
            "Icon=old-icon\n",
        ]
        mock_write.return_value = True

        with patch("pathlib.Path.exists", return_value=True):
            with patch("shutil.copy2"):
                # Mock the fix_icon_references and add_no_sandbox_flag methods
                with patch.object(
                    self.fixer, "fix_icon_references", return_value=([], True)
                ):
                    with patch.object(
                        self.fixer, "add_no_sandbox_flag", return_value=([], True)
                    ):
                        result = self.fixer.fix_desktop_file(Path("/test/app.desktop"))
                        assert result is True
                        mock_write.assert_called_once()

    @patch("appimage_fixer.core.AppImageFixer.needs_fixing")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.config.get_app_config")
    def test_fix_desktop_file_no_fixing_needed(
        self, mock_get_config, mock_extract_name, mock_needs
    ):
        """Test fixing desktop file when no fixing is needed."""
        mock_extract_name.return_value = "Test App"
        mock_get_config.return_value = {"icon": "test-icon", "needs_no_sandbox": True}
        mock_needs.return_value = False

        with patch("pathlib.Path.exists", return_value=True):
            result = self.fixer.fix_desktop_file(Path("/test/app.desktop"))
            assert result is False

    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    def test_fix_desktop_file_no_app_name(self, mock_extract_name):
        """Test fixing desktop file when app name cannot be extracted."""
        mock_extract_name.return_value = None

        with patch("pathlib.Path.exists", return_value=True):
            result = self.fixer.fix_desktop_file(Path("/test/app.desktop"))
            assert result is False

    @patch("subprocess.run")
    def test_update_desktop_database_success(self, mock_run):
        """Test updating desktop database successfully."""
        mock_run.return_value = MagicMock(returncode=0)

        self.fixer.update_desktop_database()
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_update_desktop_database_error(self, mock_run):
        """Test updating desktop database with error."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error message")

        self.fixer.update_desktop_database()
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_update_icon_cache_success(self, mock_run):
        """Test updating icon cache successfully."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch("pathlib.Path.exists", return_value=True):
            self.fixer.update_icon_cache()
            mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_update_icon_cache_error(self, mock_run):
        """Test updating icon cache with error."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error message")

        with patch("pathlib.Path.exists", return_value=True):
            self.fixer.update_icon_cache()
            mock_run.assert_called_once()

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    def test_find_appimage_files_with_integration(self, mock_get_integration):
        """Test finding AppImage files with integration enabled."""
        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "config_loaded": True,
            "running": True,
        }
        mock_integration.find_desktop_files.return_value = [
            Path("/test/appimagekit_app1.desktop"),
            Path("/test/appimagekit_app2.desktop"),
            Path("/test/regular_app.desktop"),
        ]
        mock_get_integration.return_value = mock_integration

        result = self.fixer.find_appimage_files()
        assert len(result) == 2  # Only appimagekit_ files
        assert all("appimagekit_" in str(f) for f in result)

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    def test_find_appimage_files_without_integration(self, mock_get_integration):
        """Test finding AppImage files without integration (fallback)."""
        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "config_loaded": False,
            "running": False,
        }
        mock_get_integration.return_value = mock_integration

        with patch("pathlib.Path.exists", return_value=True):
            with patch("glob.glob") as mock_glob:
                # Mock both glob calls separately to avoid duplication
                mock_glob.side_effect = [
                    [
                        "/test/app1.desktop",
                        "/test/app2.desktop",
                    ],  # First call for default_dir
                    [],  # Second call for standard_pattern
                ]

                result = self.fixer.find_appimage_files()
                assert len(result) == 2

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    def test_find_appimage_executables_with_integration(self, mock_get_integration):
        """Test finding AppImage executables with integration enabled."""
        mock_files = [Path("/test/app1.AppImage"), Path("/test/app2.AppImage")]

        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "config_loaded": True,
            "running": True,
        }
        mock_integration.find_appimage_files.return_value = mock_files
        mock_get_integration.return_value = mock_integration

        result = self.fixer.find_appimage_executables()
        assert result == mock_files

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    def test_find_appimage_executables_without_integration(self, mock_get_integration):
        """Test finding AppImage executables without integration (fallback)."""
        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "config_loaded": False,
            "running": False,
        }
        mock_get_integration.return_value = mock_integration

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.rglob") as mock_rglob:
                mock_file = MagicMock()
                mock_file.name = "test.AppImage"
                mock_file.is_file.return_value = True
                mock_rglob.return_value = [mock_file]

                with patch("os.access", return_value=True):
                    result = self.fixer.find_appimage_executables()
                    assert len(result) > 0

    def test_is_appimage_file_true(self):
        """Test detecting AppImage file correctly."""
        with patch("builtins.open", mock_open(read_data=b"\x7fELF\x02\x01\x01")):
            result = self.fixer._is_appimage_file(Path("/test/app.AppImage"))
            assert result is True

    def test_is_appimage_file_false(self):
        """Test detecting non-AppImage file correctly."""
        with patch("builtins.open", mock_open(read_data=b"NOT_AN_APPIMAGE")):
            result = self.fixer._is_appimage_file(Path("/test/not_app"))
            assert result is False

    @patch("appimage_fixer.core.AppImageFixer.scan_and_update_database")
    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    @patch("appimage_fixer.core.AppImageFixer.fix_desktop_file")
    def test_run_with_integration(self, mock_fix, mock_find, mock_scan):
        """Test main run method with integration."""
        mock_scan.return_value = {"scanned": 3, "updated": 3, "cleaned": 0}
        mock_find.return_value = [
            Path("/test/app1.desktop"),
            Path("/test/app2.desktop"),
        ]
        mock_fix.return_value = True

        result = self.fixer.run()

        assert result["files_found"] == 2
        assert result["files_fixed"] == 2
        assert result["success"] is True
        assert result["db_scanned"] == 3
        assert result["db_updated"] == 3
        assert result["db_cleaned"] == 0

    @patch("appimage_fixer.core.AppImageFixer.scan_and_update_database")
    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    def test_run_no_files_found(self, mock_find, mock_scan):
        """Test main run method when no files are found."""
        mock_scan.return_value = {"scanned": 0, "updated": 0, "cleaned": 0}
        mock_find.return_value = []

        result = self.fixer.run()

        assert result["files_found"] == 0
        assert result["files_fixed"] == 0
        assert result["success"] is True
        assert result["db_scanned"] == 0
        assert result["db_updated"] == 0
        assert result["db_cleaned"] == 0

    @patch("appimage_fixer.core.AppImageFixer.scan_and_update_database")
    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    @patch("appimage_fixer.core.AppImageFixer.fix_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.update_desktop_database")
    @patch("appimage_fixer.core.AppImageFixer.update_icon_cache")
    def test_run_with_changes(
        self, mock_icon_cache, mock_desktop_db, mock_fix, mock_find, mock_scan
    ):
        """Test main run method when changes are made."""
        mock_scan.return_value = {"scanned": 2, "updated": 2, "cleaned": 0}
        mock_find.return_value = [Path("/test/app1.desktop")]
        mock_fix.return_value = True  # Changes made

        result = self.fixer.run()

        assert result["changes_made"] is True
        mock_desktop_db.assert_called_once()
        mock_icon_cache.assert_called_once()

    @patch("appimage_fixer.core.AppImageFixer.scan_and_update_database")
    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    @patch("appimage_fixer.core.AppImageFixer.fix_desktop_file")
    @patch("appimage_fixer.core.AppImageFixer.update_desktop_database")
    @patch("appimage_fixer.core.AppImageFixer.update_icon_cache")
    def test_run_no_changes(
        self, mock_icon_cache, mock_desktop_db, mock_fix, mock_find, mock_scan
    ):
        """Test main run method when no changes are made."""
        mock_scan.return_value = {"scanned": 2, "updated": 2, "cleaned": 0}
        mock_find.return_value = [Path("/test/app1.desktop")]
        mock_fix.return_value = False  # No changes

        result = self.fixer.run()

        assert result["changes_made"] is False
        mock_desktop_db.assert_not_called()
        mock_icon_cache.assert_not_called()

    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.core.AppImageFixer.extract_appimage_version")
    def test_scan_and_update_database_success(
        self, mock_extract_version, mock_extract_name, mock_get_path, mock_find
    ):
        """Test scanning and updating database successfully."""
        mock_find.return_value = [
            Path("/test/app1.desktop"),
            Path("/test/app2.desktop"),
        ]
        # Mock get_appimage_path_from_desktop to return values for both calls (in
        # loop and in cleanup)
        mock_get_path.side_effect = [
            Path("/test/app1.AppImage"),
            Path("/test/app2.AppImage"),  # First calls in the loop
            Path("/test/app1.AppImage"),
            Path("/test/app2.AppImage"),  # Second calls in cleanup
        ]
        mock_extract_name.side_effect = ["Test App 1", "Test App 2"]
        mock_extract_version.side_effect = ["1.0.0", "2.0.0"]

        with patch.object(self.fixer.db, "calculate_checksum", return_value="abc123"):
            with patch.object(
                self.fixer.db, "add_or_update_appimage", return_value=True
            ):
                with patch.object(self.fixer.db, "cleanup_orphaned", return_value=1):
                    with patch("pathlib.Path.exists", return_value=True):
                        result = self.fixer.scan_and_update_database()

                        assert result["scanned"] == 2
                        assert result["updated"] == 2
                        assert result["cleaned"] == 1

    @patch("appimage_fixer.core.AppImageFixer.find_appimage_files")
    def test_scan_and_update_database_no_files(self, mock_find):
        """Test scanning and updating database when no files found."""
        mock_find.return_value = []

        with patch.object(self.fixer.db, "cleanup_orphaned", return_value=0):
            result = self.fixer.scan_and_update_database()

            assert result["scanned"] == 0
            assert result["updated"] == 0
            assert result["cleaned"] == 0

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    def test_scan_and_update_database_missing_appimage(
        self, mock_extract_name, mock_get_path
    ):
        """Test scanning when AppImage path is missing."""
        mock_get_path.return_value = None
        mock_extract_name.return_value = "Test App"

        with patch(
            "appimage_fixer.core.AppImageFixer.find_appimage_files",
            return_value=[Path("/test/app.desktop")],
        ):
            with patch.object(
                self.fixer.db, "calculate_checksum", return_value="abc123"
            ):
                with patch.object(
                    self.fixer.db, "add_or_update_appimage", return_value=True
                ):
                    with patch.object(
                        self.fixer.db, "cleanup_orphaned", return_value=0
                    ):
                        result = self.fixer.scan_and_update_database()

                        assert result["scanned"] == 0
                        assert result["updated"] == 0

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    def test_scan_and_update_database_missing_app_name(self, mock_get_path):
        """Test scanning when app name is missing."""
        mock_get_path.return_value = Path("/test/app.AppImage")

        with patch(
            "appimage_fixer.core.AppImageFixer.find_appimage_files",
            return_value=[Path("/test/app.desktop")],
        ):
            with patch(
                "appimage_fixer.core.AppImageFixer.extract_app_name", return_value=None
            ):
                with patch.object(
                    self.fixer.db, "calculate_checksum", return_value="abc123"
                ):
                    with patch.object(
                        self.fixer.db, "add_or_update_appimage", return_value=True
                    ):
                        with patch.object(
                            self.fixer.db, "cleanup_orphaned", return_value=0
                        ):
                            result = self.fixer.scan_and_update_database()

                            assert result["scanned"] == 0
                            assert result["updated"] == 0

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.core.AppImageFixer.extract_appimage_version")
    def test_compare_versions_with_db_success(
        self, mock_extract_version, mock_extract_name, mock_get_path
    ):
        """Test comparing versions with database successfully."""
        mock_get_path.return_value = Path("/test/app.AppImage")
        mock_extract_name.return_value = "Test App"
        mock_extract_version.return_value = "1.0.0"

        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(
                self.fixer.db, "calculate_checksum", return_value="abc123"
            ):
                with patch.object(
                    self.fixer.db, "get_by_checksum", return_value={"version": "1.0.0"}
                ):
                    with patch(
                        "appimage_fixer.core.AppImageFixer.extract_desktop_version",
                        return_value="1.0.0",
                    ):
                        result = self.fixer.compare_versions_with_db(
                            Path("/test/app.desktop")
                        )

                        assert result["desktop_version"] == "1.0.0"
                        assert result["appimage_version"] == "1.0.0"
                        assert result["versions_match"] is True
                        assert result["status"] == "match"

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    def test_compare_versions_with_db_appimage_not_found(self, mock_get_path):
        """Test comparing versions when AppImage is not found."""
        mock_get_path.return_value = None

        result = self.fixer.compare_versions_with_db(Path("/test/app.desktop"))

        assert result["status"] == "appimage_not_found"

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    def test_compare_versions_with_db_appimage_file_not_exists(self, mock_get_path):
        """Test comparing versions when AppImage file doesn't exist."""
        mock_get_path.return_value = Path("/nonexistent/app.AppImage")

        result = self.fixer.compare_versions_with_db(Path("/test/app.desktop"))

        assert result["status"] == "appimage_not_found"

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.core.AppImageFixer.extract_appimage_version")
    def test_compare_versions_with_db_versions_mismatch(
        self, mock_extract_version, mock_extract_name, mock_get_path
    ):
        """Test comparing versions when versions don't match."""
        mock_get_path.return_value = Path("/test/app.AppImage")
        mock_extract_name.return_value = "Test App"
        mock_extract_version.return_value = "2.0.0"

        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(
                self.fixer.db, "calculate_checksum", return_value="abc123"
            ):
                with patch.object(
                    self.fixer.db, "get_by_checksum", return_value={"version": "1.0.0"}
                ):
                    with patch(
                        "appimage_fixer.core.AppImageFixer.extract_desktop_version",
                        return_value="2.0.0",
                    ):
                        result = self.fixer.compare_versions_with_db(
                            Path("/test/app.desktop")
                        )

                        assert result["desktop_version"] == "2.0.0"
                        assert result["appimage_version"] == "1.0.0"
                        assert result["versions_match"] is False
                        assert result["status"] == "mismatch"

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.core.AppImageFixer.extract_appimage_version")
    def test_compare_versions_with_db_no_versions(
        self, mock_extract_version, mock_extract_name, mock_get_path
    ):
        """Test comparing versions when no versions are available."""
        mock_get_path.return_value = Path("/test/app.AppImage")
        mock_extract_name.return_value = "Test App"
        mock_extract_version.return_value = None

        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(
                self.fixer.db, "calculate_checksum", return_value="abc123"
            ):
                with patch.object(self.fixer.db, "get_by_checksum", return_value=None):
                    with patch(
                        "appimage_fixer.core.AppImageFixer.extract_desktop_version",
                        return_value=None,
                    ):
                        result = self.fixer.compare_versions_with_db(
                            Path("/test/app.desktop")
                        )

                        assert result["desktop_version"] is None
                        assert result["appimage_version"] is None
                        assert result["versions_match"] is False
                        assert result["status"] == "no_version"

    @patch("appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop")
    @patch("appimage_fixer.core.AppImageFixer.extract_app_name")
    @patch("appimage_fixer.core.AppImageFixer.extract_appimage_version")
    def test_compare_versions_with_db_no_desktop_version(
        self, mock_extract_version, mock_extract_name, mock_get_path
    ):
        """Test comparing versions when desktop version is not available."""
        mock_get_path.return_value = Path("/test/app.AppImage")
        mock_extract_name.return_value = "Test App"
        mock_extract_version.return_value = "1.0.0"

        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(
                self.fixer.db, "calculate_checksum", return_value="abc123"
            ):
                with patch.object(
                    self.fixer.db, "get_by_checksum", return_value={"version": "1.0.0"}
                ):
                    with patch(
                        "appimage_fixer.core.AppImageFixer.extract_desktop_version",
                        return_value=None,
                    ):
                        result = self.fixer.compare_versions_with_db(
                            Path("/test/app.desktop")
                        )

                        assert result["desktop_version"] is None
                        assert result["appimage_version"] == "1.0.0"
                        assert result["versions_match"] is False
                        assert result["status"] == "no_version"

    def test_log_function(self):
        """Test logging functionality."""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("appimage_fixer.core.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = (
                    "2024-01-01 12:00:00"
                )

                self.fixer.log("Test message", "INFO")

                mock_file.assert_called_once()

    def test_log_function_error(self):
        """Test logging functionality with file write error."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            # Should not raise exception, just print warning
            self.fixer.log("Test message", "ERROR")

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_compare_versions_legacy_method(self, mock_read):
        """Test legacy compare_versions method."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "X-AppImage-Version=1.0.0\n",
            "Exec=/test/app.AppImage\n",
        ]

        with patch(
            "appimage_fixer.core.AppImageFixer.extract_appimage_version",
            return_value="1.0.0",
        ):
            with patch(
                "appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop",
                return_value=Path("/test/app.AppImage"),
            ):
                with patch("pathlib.Path.exists", return_value=True):
                    result = self.fixer.compare_versions(Path("/test/app.desktop"))

                    assert result["desktop_version"] == "1.0.0"
                    assert result["appimage_version"] == "1.0.0"
                    assert result["versions_match"] is True
                    assert result["status"] == "match"

    @patch("appimage_fixer.core.AppImageFixer.read_desktop_file")
    def test_compare_versions_legacy_no_desktop_version(self, mock_read):
        """Test legacy compare_versions method when no desktop version."""
        mock_read.return_value = [
            "[Desktop Entry]\n",
            "Name=Test App\n",
            "Exec=/test/app.AppImage\n",
        ]

        with patch(
            "appimage_fixer.core.AppImageFixer.extract_appimage_version",
            return_value="1.0.0",
        ):
            with patch(
                "appimage_fixer.core.AppImageFixer.get_appimage_path_from_desktop",
                return_value=Path("/test/app.AppImage"),
            ):
                with patch("pathlib.Path.exists", return_value=True):
                    result = self.fixer.compare_versions(Path("/test/app.desktop"))

                    assert result["desktop_version"] is None
                    assert (
                        result["appimage_version"] is None
                    )  # Early return, so appimage_version is not set
                    assert result["versions_match"] is False
                    assert result["status"] == "no_desktop_version"
