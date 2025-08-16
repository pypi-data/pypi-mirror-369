import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import configparser

from appimage_fixer.appimaged_integration import (
    AppImageDIntegration,
    get_appimaged_integration,
)


class TestAppImageDIntegration:
    """Test AppImageD integration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.integration = AppImageDIntegration()

    def test_init(self):
        """Test initialization."""
        assert self.integration is not None
        assert hasattr(self.integration, "config_paths")
        assert hasattr(self.integration, "config")

    @patch("appimage_fixer.appimaged_integration.configparser.ConfigParser")
    def test_load_config_success(self, mock_config_parser):
        """Test successful config loading."""
        mock_config = MagicMock()
        mock_config_parser.return_value = mock_config

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("[AppImageLauncher]\nappimage_dir=/test/path\n")
            config_path = f.name

        try:
            with patch.object(self.integration, "config_paths", [Path(config_path)]):
                result = self.integration._load_config()
                assert result is not None
        finally:
            os.unlink(config_path)

    def test_load_config_no_files(self):
        """Test config loading when no config files exist."""
        with patch.object(self.integration, "config_paths", []):
            result = self.integration._load_config()
            assert isinstance(result, configparser.ConfigParser)

    @patch("appimage_fixer.appimaged_integration.subprocess.run")
    def test_is_appimaged_running_true(self, mock_run):
        """Test detecting running AppImageD."""
        mock_result = MagicMock()
        mock_result.stdout = "active\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        assert self.integration.is_appimaged_running() is True

    @patch("appimage_fixer.appimaged_integration.subprocess.run")
    def test_is_appimaged_running_false(self, mock_run):
        """Test detecting stopped AppImageD."""
        mock_run.return_value = MagicMock(returncode=1)
        assert self.integration.is_appimaged_running() is False

    def test_get_appimage_directories_with_config(self):
        """Test getting AppImage directories from config."""
        mock_config = MagicMock()
        mock_config.has_section.return_value = True
        mock_config.has_option.return_value = True
        mock_config.get.return_value = "/custom/path"

        with patch.object(self.integration, "config", mock_config):
            with patch("pathlib.Path.exists", return_value=True):
                directories = self.integration.get_appimage_directories()
                assert any("/custom/path" in str(d) for d in directories)

    def test_get_appimage_directories_default(self):
        """Test getting default AppImage directories."""
        mock_config = MagicMock()
        mock_config.has_section.return_value = False
        mock_config.has_option.return_value = False

        with patch.object(self.integration, "config", mock_config):
            with patch("pathlib.Path.exists", return_value=True):
                directories = self.integration.get_appimage_directories()
                expected_dirs = [
                    Path.home() / "Applications",
                    Path.home() / ".local/bin",
                    Path("/opt/appimages"),
                    Path("/usr/local/bin"),
                ]
                for expected_dir in expected_dirs:
                    assert expected_dir in directories

    @patch("pathlib.Path.exists")
    def test_get_desktop_file_directories(self, mock_exists):
        """Test getting desktop file directories."""
        # Mock all directories as existing
        mock_exists.return_value = True

        directories = self.integration.get_desktop_file_directories()
        expected_dirs = [
            Path.home() / ".local/share/applications",
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
        ]
        for expected_dir in expected_dirs:
            assert expected_dir in directories

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rglob")
    @patch("os.access")
    def test_find_appimage_files(self, mock_access, mock_rglob, mock_exists):
        """Test finding AppImage files."""
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_file = MagicMock()
        mock_file.name = "test.AppImage"
        mock_file.is_file.return_value = True
        mock_file.suffix = ".AppImage"
        mock_rglob.return_value = [mock_file]

        with patch.object(
            self.integration, "get_appimage_directories", return_value=[Path("/test")]
        ):
            files = self.integration.find_appimage_files()
            assert len(files) > 0

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rglob")
    def test_find_desktop_files(self, mock_rglob, mock_exists):
        """Test finding desktop files."""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.name = "test.desktop"
        mock_file.is_file.return_value = True
        mock_rglob.return_value = [mock_file]

        with patch.object(
            self.integration,
            "get_desktop_file_directories",
            return_value=[Path("/test")],
        ):
            files = self.integration.find_desktop_files()
            assert len(files) > 0

    def test_get_appimaged_status(self):
        """Test getting comprehensive AppImageD status."""
        with patch.object(self.integration, "is_appimaged_running", return_value=True):
            with patch.object(self.integration, "config", MagicMock()):
                status = self.integration.get_appimaged_status()

                assert "running" in status
                assert "enabled" in status
                assert "config_loaded" in status
                assert "appimage_directories" in status
                assert "desktop_directories" in status

    def test_get_appimaged_integration(self):
        """Test getting integration instance."""
        integration = get_appimaged_integration()
        assert isinstance(integration, AppImageDIntegration)
