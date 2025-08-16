import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from appimage_fixer.database import AppImageDatabase


class TestAppImageDatabase:
    """Test AppImageDatabase functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = AppImageDatabase(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()
        if self.temp_dir and os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_init(self):
        """Test database initialization."""
        assert self.db is not None
        assert self.db.db_path == self.db_path
        assert self.db_path.exists()

    def test_create_tables(self):
        """Test table creation."""
        # Tables should be created during init
        import sqlite3

        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            assert "appimage_registry" in tables

    def test_add_or_update_appimage_new(self):
        """Test adding new AppImage record."""
        data = {
            "name": "Test App",
            "version": "1.0.0",
            "checksum": "abc123",
            "file_path": "/test/app.AppImage",
            "desktop_file": "/test/app.desktop",
            "appimage_id": "test-id",
        }

        result = self.db.add_or_update_appimage(data)
        assert result is True

        # Verify record was added
        import sqlite3

        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM appimage_registry WHERE checksum = ?", ("abc123",)
            )
            row = cursor.fetchone()

            assert row is not None
            assert row[1] == "Test App"  # name
            assert row[2] == "1.0.0"  # version
            assert row[3] == "abc123"  # checksum

    def test_add_or_update_appimage_existing(self):
        """Test updating existing AppImage record."""
        # Add initial record
        data1 = {
            "name": "Test App",
            "version": "1.0.0",
            "checksum": "abc123",
            "file_path": "/test/app.AppImage",
            "desktop_file": "/test/app.desktop",
            "appimage_id": "test-id",
        }
        self.db.add_or_update_appimage(data1)

        # Update record
        data2 = {
            "name": "Test App Updated",
            "version": "2.0.0",
            "checksum": "abc123",  # Same checksum
            "file_path": "/test/app.AppImage",  # Same file_path for REPLACE to work
            "desktop_file": "/test/app_v2.desktop",
            "appimage_id": "test-id-v2",
        }
        result = self.db.add_or_update_appimage(data2)
        assert result is True

        # Verify record was updated
        import sqlite3

        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM appimage_registry WHERE checksum = ?", ("abc123",)
            )
            row = cursor.fetchone()

            assert row is not None
            assert row[1] == "Test App Updated"  # name updated
            assert row[2] == "2.0.0"  # version updated

    def test_get_by_checksum_found(self):
        """Test getting record by checksum when found."""
        data = {
            "name": "Test App",
            "version": "1.0.0",
            "checksum": "abc123",
            "file_path": "/test/app.AppImage",
            "desktop_file": "/test/app.desktop",
            "appimage_id": "test-id",
        }
        self.db.add_or_update_appimage(data)

        result = self.db.get_by_checksum("abc123")
        assert result is not None
        assert result["name"] == "Test App"
        assert result["version"] == "1.0.0"
        assert result["checksum"] == "abc123"

    def test_get_by_checksum_not_found(self):
        """Test getting record by checksum when not found."""
        result = self.db.get_by_checksum("nonexistent")
        assert result is None

    def test_get_all_appimages(self):
        """Test getting all AppImage records."""
        data1 = {
            "name": "Test App 1",
            "version": "1.0.0",
            "checksum": "abc123",
            "file_path": "/test/app1.AppImage",
            "desktop_file": "/test/app1.desktop",
            "appimage_id": "test-id-1",
        }
        data2 = {
            "name": "Test App 2",
            "version": "2.0.0",
            "checksum": "def456",
            "file_path": "/test/app2.AppImage",
            "desktop_file": "/test/app2.desktop",
            "appimage_id": "test-id-2",
        }

        self.db.add_or_update_appimage(data1)
        self.db.add_or_update_appimage(data2)

        results = self.db.get_all_appimages()
        assert len(results) == 2

        names = [r["name"] for r in results]
        assert "Test App 1" in names
        assert "Test App 2" in names

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_file = f.name

        try:
            checksum = self.db.calculate_checksum(Path(temp_file))
            assert len(checksum) == 64  # SHA256 hash length
            assert checksum.isalnum()  # Should be alphanumeric
        finally:
            os.unlink(temp_file)

    def test_cleanup_orphaned(self):
        """Test cleanup of orphaned records."""
        # Add some records
        data1 = {
            "name": "Test App 1",
            "version": "1.0.0",
            "checksum": "abc123",
            "file_path": "/test/app1.AppImage",
            "desktop_file": "/test/app1.desktop",
            "appimage_id": "test-id-1",
        }
        data2 = {
            "name": "Test App 2",
            "version": "2.0.0",
            "checksum": "def456",
            "file_path": "/test/app2.AppImage",
            "desktop_file": "/test/app2.desktop",
            "appimage_id": "test-id-2",
        }

        self.db.add_or_update_appimage(data1)
        self.db.add_or_update_appimage(data2)

        # Verify both records exist
        assert len(self.db.get_all_appimages()) == 2

        # Cleanup with only one existing path
        existing_paths = [Path("/test/app1.AppImage")]  # Only app1 exists
        cleaned_count = self.db.cleanup_orphaned(existing_paths)

        assert cleaned_count == 1  # app2 should be cleaned up

        # Verify only app1 remains
        remaining = self.db.get_all_appimages()
        assert len(remaining) == 1
        assert remaining[0]["name"] == "Test App 1"
