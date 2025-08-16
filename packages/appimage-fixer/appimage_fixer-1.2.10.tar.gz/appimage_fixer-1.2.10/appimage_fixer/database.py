"""
Database module for AppImage Fixer

Handles SQLite database operations for storing AppImage metadata.
"""

import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AppImageDatabase:
    """SQLite database handler for AppImage metadata."""

    def __init__(self, db_path: str = "~/.local/share/appimage-fixer/appimages.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create database table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS appimage_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT,
                    checksum TEXT NOT NULL,
                    file_path TEXT UNIQUE NOT NULL,
                    desktop_file TEXT,
                    appimage_id TEXT,
                    last_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def add_or_update_appimage(self, data: Dict) -> bool:
        """Add or update AppImage record in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO appimage_registry
                    (name, version, checksum, file_path, desktop_file, appimage_id, last_scan)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["name"],
                        data["version"],
                        data["checksum"],
                        data["file_path"],
                        data["desktop_file"],
                        data["appimage_id"],
                        datetime.now(),
                    ),
                )
            return True
        except Exception:
            return False

    def get_by_checksum(self, checksum: str) -> Optional[Dict]:
        """Find record by checksum."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM appimage_registry WHERE checksum = ?", (checksum,)
            )
            row = cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
        return None

    def get_all_appimages(self) -> List[Dict]:
        """Get all AppImage records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM appimage_registry ORDER BY name")
            return [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]

    def cleanup_orphaned(self, existing_paths: List[Path]) -> int:
        """Remove records for non-existent files."""
        existing_paths_str = [str(p) for p in existing_paths]
        if not existing_paths_str:
            return 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM appimage_registry WHERE file_path NOT IN ({})".format(
                    ",".join("?" * len(existing_paths_str))
                ),
                existing_paths_str,
            )
            return cursor.rowcount
