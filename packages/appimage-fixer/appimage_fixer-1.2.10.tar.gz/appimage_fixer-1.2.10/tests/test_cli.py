import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from pathlib import Path

from appimage_fixer.cli import (
    main,
    check_appimaged_integration,
    list_installed_apps,
    check_versions,
    run_fixer,
    install_service,
    uninstall_service,
)


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    @patch("sys.argv", ["appimage-fixer", "--version"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_version(self, mock_stdout):
        """Test version command."""
        with patch("appimage_fixer.cli.__version__", "1.2.0"):
            with pytest.raises(SystemExit):
                main()
            output = mock_stdout.getvalue()
            assert "1.2.0" in output

    @patch("sys.argv", ["appimage-fixer", "run"])
    @patch("appimage_fixer.cli.run_fixer")
    def test_run_command(self, mock_run_fixer):
        """Test run command."""
        mock_run_fixer.return_value = {"success": True}
        main()
        mock_run_fixer.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "list"])
    @patch("appimage_fixer.cli.list_installed_apps")
    def test_list_command(self, mock_list_apps):
        """Test list command."""
        main()
        mock_list_apps.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "check-versions"])
    @patch("appimage_fixer.cli.check_versions")
    def test_check_versions_command(self, mock_check_versions):
        """Test check-versions command."""
        main()
        mock_check_versions.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "check-appimaged"])
    @patch("appimage_fixer.cli.check_appimaged_integration")
    def test_check_appimaged_command(self, mock_check_appimaged):
        """Test check-appimaged command."""
        main()
        mock_check_appimaged.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "install-service"])
    @patch("appimage_fixer.cli.install_service")
    def test_install_service_command(self, mock_install_service):
        """Test install-service command."""
        main()
        mock_install_service.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "uninstall-service"])
    @patch("appimage_fixer.cli.uninstall_service")
    def test_uninstall_service_command(self, mock_uninstall_service):
        """Test uninstall-service command."""
        main()
        mock_uninstall_service.assert_called_once()

    @patch("sys.argv", ["appimage-fixer", "--help"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_help(self, mock_stdout):
        """Test help command."""
        with pytest.raises(SystemExit):
            main()
        output = mock_stdout.getvalue()
        assert "check-appimaged" in output  # New command should be in help

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_appimaged_integration(self, mock_stdout, mock_get_integration):
        """Test check_appimaged_integration function."""
        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "running": True,
            "enabled": True,
            "config_loaded": True,
            "appimage_directories": ["/test/dir1", "/test/dir2"],
            "desktop_directories": ["/test/desktop1"],
        }
        mock_integration.get_monitoring_directories.return_value = ["/test/monitor1"]
        mock_integration.find_appimage_files.return_value = [
            Path("app1.AppImage"),
            Path("app2.AppImage"),
            Path("app3.AppImage"),
        ]
        mock_integration.find_desktop_files.return_value = [
            Path("app1.desktop"),
            Path("app2.desktop"),
        ]
        mock_integration.get_appimage_desktop_mapping.return_value = {
            Path("app1.AppImage"): Path("app1.desktop"),
            Path("app2.AppImage"): None,
        }
        mock_get_integration.return_value = mock_integration

        check_appimaged_integration()
        output = mock_stdout.getvalue()

        assert "AppImageD Integration Status:" in output
        assert "Daemon Running: True" in output
        assert "Daemon Enabled: True" in output
        assert "Config Loaded: True" in output
        assert "3 AppImage files" in output
        assert "2 desktop files" in output

    @patch("appimage_fixer.appimaged_integration.get_appimaged_integration")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_appimaged_integration_not_running(
        self, mock_stdout, mock_get_integration
    ):
        """Test check_appimaged_integration when daemon is not running."""
        mock_integration = MagicMock()
        mock_integration.get_appimaged_status.return_value = {
            "running": False,
            "enabled": False,
            "config_loaded": False,
            "appimage_directories": [],
            "desktop_directories": [],
        }
        mock_integration.get_monitoring_directories.return_value = []
        mock_integration.find_appimage_files.return_value = []
        mock_integration.find_desktop_files.return_value = []
        mock_integration.get_appimage_desktop_mapping.return_value = {}
        mock_get_integration.return_value = mock_integration

        check_appimaged_integration()
        output = mock_stdout.getvalue()

        assert "Daemon Running: False" in output
        assert "Daemon Enabled: False" in output
        assert "Config Loaded: False" in output
        assert "0 AppImage files" in output
        assert "0 desktop files" in output

    @patch("appimage_fixer.cli.AppImageFixer")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_installed_apps_with_data(self, mock_stdout, mock_fixer_class):
        """Test list_installed_apps with data."""
        mock_fixer = mock_fixer_class.return_value
        mock_fixer.db.get_all_appimages.return_value = [
            {
                "name": "Test App 1",
                "version": "1.0.0",
                "last_scan": "2024-01-01 12:00:00",
            },
            {
                "name": "Test App 2",
                "version": "2.0.0",
                "last_scan": "2024-01-02 12:00:00",
            },
        ]

        list_installed_apps()
        output = mock_stdout.getvalue()

        assert "Test App 1" in output
        assert "Test App 2" in output
        assert "1.0.0" in output
        assert "2.0.0" in output

    @patch("appimage_fixer.cli.AppImageFixer")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_installed_apps_no_data(self, mock_stdout, mock_fixer_class):
        """Test list_installed_apps with no data."""
        mock_fixer = mock_fixer_class.return_value
        mock_fixer.db.get_all_appimages.return_value = []

        list_installed_apps()
        output = mock_stdout.getvalue()

        assert "No AppImage applications found in database." in output

    @patch("appimage_fixer.cli.AppImageFixer")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_versions_with_data(self, mock_stdout, mock_fixer_class):
        """Test check_versions with data."""
        mock_fixer = mock_fixer_class.return_value
        mock_fixer.scan_and_update_database.return_value = {"updated": 1}
        mock_fixer.find_appimage_files.return_value = [
            "/test/app1.desktop",
            "/test/app2.desktop",
        ]
        mock_fixer.extract_app_name.side_effect = ["Test App 1", "Test App 2"]
        mock_fixer.compare_versions_with_db.side_effect = [
            {
                "desktop_version": "1.0.0",
                "appimage_version": "1.0.0",
                "versions_match": True,
                "status": "match",
            },
            {
                "desktop_version": "2.0.0",
                "appimage_version": "1.0.0",
                "versions_match": False,
                "status": "mismatch",
            },
        ]

        check_versions()
        output = mock_stdout.getvalue()

        assert "Test App 1" in output
        assert "Test App 2" in output
        assert "✓ MATCH" in output
        assert "✗ MISMATCH" in output

    @patch("appimage_fixer.cli.AppImageFixer")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_versions_no_data(self, mock_stdout, mock_fixer_class):
        """Test check_versions with no data."""
        mock_fixer = mock_fixer_class.return_value
        mock_fixer.scan_and_update_database.return_value = {"updated": 0}
        mock_fixer.find_appimage_files.return_value = []

        check_versions()
        output = mock_stdout.getvalue()

        assert "No AppImage applications found." in output

    @patch("appimage_fixer.cli.AppImageFixer")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_fixer_success(self, mock_stdout, mock_fixer_class):
        """Test run_fixer success."""
        mock_fixer = mock_fixer_class.return_value
        mock_fixer.run.return_value = {
            "success": True,
            "files_found": 5,
            "files_fixed": 3,
            "db_scanned": 5,
            "db_updated": 3,
            "db_cleaned": 0,
        }

        args = MagicMock()
        args.dry_run = False
        args.home_dir = None
        args.log_file = None

        result = run_fixer(args)
        output = mock_stdout.getvalue()

        assert result == 0
        assert "Files found: 5" in output
        assert "Files fixed: 3" in output
        assert "Database scanned: 5" in output

    @patch("appimage_fixer.installer.install_systemd_service")
    @patch("sys.stdout", new_callable=StringIO)
    def test_install_service_success(self, mock_stdout, mock_install):
        """Test install_service success."""
        mock_install.return_value = True

        result = install_service()
        output = mock_stdout.getvalue()

        assert result == 0
        assert "✓ Systemd service installed successfully!" in output
        mock_install.assert_called_once()

    @patch("appimage_fixer.installer.uninstall_systemd_service")
    @patch("sys.stdout", new_callable=StringIO)
    def test_uninstall_service_success(self, mock_stdout, mock_uninstall):
        """Test uninstall_service success."""
        mock_uninstall.return_value = True

        result = uninstall_service()
        output = mock_stdout.getvalue()

        assert result == 0
        assert "✓ Systemd service uninstalled successfully!" in output
        mock_uninstall.assert_called_once()
