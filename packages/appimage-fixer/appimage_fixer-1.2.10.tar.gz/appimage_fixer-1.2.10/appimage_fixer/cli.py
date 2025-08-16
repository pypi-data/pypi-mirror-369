"""
Command-line interface for AppImage Fixer.
"""

import argparse
import sys
from pathlib import Path

from .core import AppImageFixer

from . import __version__


def list_installed_apps():
    """List installed AppImage applications from database."""
    fixer = AppImageFixer()
    appimages = fixer.db.get_all_appimages()

    if not appimages:
        print("No AppImage applications found in database.")
        return

    print("Installed AppImage Applications:")
    print("=" * 80)
    print(f"{'Application':<25} {'Version':<15} {'Status':<15} {'Last Scan'}")
    print("-" * 80)

    for app in appimages:
        status = "OK" if app["version"] else "NO VERSION"
        # Show full datetime if available, otherwise just date
        if app["last_scan"]:
            try:
                # Try to show HH:MM format
                last_scan = (
                    app["last_scan"][:16]
                    if len(app["last_scan"]) >= 16
                    else app["last_scan"][:10]
                )
            except BaseException:
                last_scan = app["last_scan"][:10]
        else:
            last_scan = "N/A"
        print(
            f"{app['name']:<25} {app['version'] or 'N/A':<15} {status:<15} {last_scan}"
        )

    print(f"\nTotal: {len(appimages)} AppImage application(s) in database")


def check_versions():
    """Check version consistency between desktop files and AppImage files using database."""
    fixer = AppImageFixer()

    # First update database
    db_result = fixer.scan_and_update_database()
    print(f"Database updated: {db_result['updated']} records")

    desktop_files = fixer.find_appimage_files()

    if not desktop_files:
        print("No AppImage applications found.")
        return

    print("Version Consistency Check:")
    print("=" * 80)
    print(
        f"{'Application':<25} {'Desktop Version':<15} "
        f"{'AppImage Version':<15} {'Status'}"
    )
    print("-" * 80)

    total_files = 0
    matching_versions = 0

    for file_path in desktop_files:
        app_name = fixer.extract_app_name(file_path)
        if not app_name:
            continue

        total_files += 1
        result = fixer.compare_versions_with_db(file_path)

        desktop_version = result["desktop_version"] or "N/A"
        appimage_version = result["appimage_version"] or "N/A"

        if result["versions_match"]:
            status = "✓ MATCH"
            matching_versions += 1
        elif result["status"] == "mismatch":
            status = "✗ MISMATCH"
        elif result["status"] == "no_version":
            status = "? NO VERSION"
        elif result["status"] == "appimage_not_found":
            status = "? APPIMAGE NOT FOUND"
        else:
            status = "? UNKNOWN"

        print(f"{app_name:<25} {desktop_version:<15} {appimage_version:<15} {status}")

    print("-" * 80)
    print(f"Total: {total_files} applications checked")
    print(f"Matching versions: {matching_versions}")
    print(f"Mismatched versions: {total_files - matching_versions}")

    if matching_versions == total_files:
        print("✅ All versions match!")
    else:
        print("⚠️  Some version mismatches detected")


def check_appimaged_integration():
    """Check AppImageD integration and show status."""
    from .appimaged_integration import get_appimaged_integration

    integration = get_appimaged_integration()
    status = integration.get_appimaged_status()

    print("AppImageD Integration Status:")
    print("=" * 50)
    print(f"Daemon Running: {status['running']}")
    print(f"Daemon Enabled: {status['enabled']}")
    print(f"Config Loaded: {status['config_loaded']}")

    print("\nAppImage Directories:")
    for directory in status["appimage_directories"]:
        print(f"  - {directory}")

    print("\nDesktop File Directories:")
    for directory in status["desktop_directories"]:
        print(f"  - {directory}")

    print("\nMonitoring Directories:")
    monitoring_dirs = integration.get_monitoring_directories()
    for directory in monitoring_dirs:
        print(f"  - {directory}")

    print("\nAppImage Files Found:")
    appimage_files = integration.find_appimage_files()
    print(f"  - {len(appimage_files)} AppImage files")

    print("\nDesktop Files Found:")
    desktop_files = integration.find_desktop_files()
    print(f"  - {len(desktop_files)} desktop files")

    print("\nAppImage-Desktop Mapping:")
    mapping = integration.get_appimage_desktop_mapping()
    for appimage_path, desktop_path in mapping.items():
        status = "✓" if desktop_path else "✗"
        desktop_name = desktop_path.name if desktop_path else "No desktop file"
        print(f"  {status} {appimage_path.name} -> {desktop_name}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fix AppImageLauncher desktop files automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  appimage-fixer run                    # Fix all AppImage desktop files
  appimage-fixer run --dry-run          # Show what would be fixed without making changes
  appimage-fixer list                   # List installed AppImage applications
  appimage-fixer check-versions         # Check version consistency
  appimage-fixer check-appimaged        # Check AppImageD integration
  appimage-fixer install-service       # Install systemd service
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"AppImage Fixer v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Fix AppImage desktop files")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    run_parser.add_argument("--log-file", type=Path, help="Custom log file path")
    run_parser.add_argument("--home-dir", type=Path, help="Custom home directory")

    # List command
    subparsers.add_parser("list", help="List installed AppImage applications")

    # Check versions command
    subparsers.add_parser(
        "check-versions",
        help="Check version consistency between desktop files and AppImage files",
    )

    # AppImageD integration command
    subparsers.add_parser(
        "check-appimaged", help="Check AppImageD integration and show status"
    )

    # Install service command
    subparsers.add_parser("install-service", help="Install systemd user service")
    subparsers.add_parser("uninstall-service", help="Uninstall systemd user service")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "run":
            return run_fixer(args)
        elif args.command == "list":
            list_installed_apps()
            return 0
        elif args.command == "check-versions":
            check_versions()
            return 0
        elif args.command == "check-appimaged":
            check_appimaged_integration()
            return 0
        elif args.command == "install-service":
            return install_service()
        elif args.command == "uninstall-service":
            return uninstall_service()
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_fixer(args):
    """Run the AppImage fixer."""
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("-" * 40)

    fixer = AppImageFixer(home_dir=args.home_dir, log_file=args.log_file)

    if args.dry_run:
        # For dry run, we'll just list what would be fixed
        desktop_files = fixer.find_appimage_files()
        if not desktop_files:
            print("No AppImageLauncher desktop files found.")
            return 0

        print(f"Found {len(desktop_files)} AppImageLauncher desktop files:")
        for file_path in desktop_files:
            app_name = fixer.extract_app_name(file_path)
            if app_name:
                from .config import get_app_config

                config = get_app_config(app_name)
                needs_fixing = fixer.needs_fixing(
                    file_path, config["icon"], config["needs_no_sandbox"]
                )
                status = "NEEDS FIXING" if needs_fixing else "OK"
                print(f"  {file_path.name} ({app_name}) - {status}")
        return 0

    # Actually run the fixer
    result = fixer.run()

    if result["success"]:
        print("\\nSummary:")
        print(f"  Files found: {result['files_found']}")
        print(f"  Files fixed: {result['files_fixed']}")
        print(f"  Database scanned: {result['db_scanned']}")
        print(f"  Database updated: {result['db_updated']}")
        print(f"  Database cleaned: {result['db_cleaned']}")
        return 0
    else:
        print("Fixer execution failed!")
        return 1


def install_service():
    """Install systemd user service."""
    from .installer import install_systemd_service

    try:
        install_systemd_service()
        print("✓ Systemd service installed successfully!")
        print("  Service will run every 30 seconds automatically.")
        print("  Use 'systemctl --user status appimage-fixer.timer' to check status.")
        return 0
    except Exception as e:
        print(f"Failed to install service: {e}")
        return 1


def uninstall_service():
    """Uninstall systemd user service."""
    from .installer import uninstall_systemd_service

    try:
        uninstall_systemd_service()
        print("✓ Systemd service uninstalled successfully!")
        return 0
    except Exception as e:
        print(f"Failed to uninstall service: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
