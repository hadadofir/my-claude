"""SQLite database operations for Mail Maint"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from .utils.logger import get_logger

logger = get_logger("database")


class Database:
    """SQLite database handler for email backup and tracking"""

    def __init__(self, db_path: str = "data/mail_backup.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gmail_id TEXT UNIQUE NOT NULL,
                    thread_id TEXT,
                    subject TEXT,
                    sender TEXT,
                    sender_email TEXT,
                    recipients TEXT,
                    date TEXT,
                    body_plain TEXT,
                    body_html TEXT,
                    labels TEXT,
                    snippet TEXT,
                    backed_up_at TEXT NOT NULL
                )
            """)

            # Full-text search on emails
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
                    subject,
                    sender,
                    body_plain,
                    content='emails',
                    content_rowid='id'
                )
            """)

            # Triggers to keep FTS index in sync
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS emails_ai AFTER INSERT ON emails BEGIN
                    INSERT INTO emails_fts(rowid, subject, sender, body_plain)
                    VALUES (new.id, new.subject, new.sender, new.body_plain);
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS emails_ad AFTER DELETE ON emails BEGIN
                    INSERT INTO emails_fts(emails_fts, rowid, subject, sender, body_plain)
                    VALUES('delete', old.id, old.subject, old.sender, old.body_plain);
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS emails_au AFTER UPDATE ON emails BEGIN
                    INSERT INTO emails_fts(emails_fts, rowid, subject, sender, body_plain)
                    VALUES('delete', old.id, old.subject, old.sender, old.body_plain);
                    INSERT INTO emails_fts(rowid, subject, sender, body_plain)
                    VALUES (new.id, new.subject, new.sender, new.body_plain);
                END
            """)

            # Unsubscribe links table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unsubscribe_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER,
                    gmail_id TEXT,
                    sender TEXT,
                    sender_email TEXT,
                    unsubscribe_url TEXT,
                    unsubscribe_type TEXT,
                    status TEXT DEFAULT 'pending',
                    discovered_at TEXT NOT NULL,
                    processed_at TEXT,
                    FOREIGN KEY (email_id) REFERENCES emails(id)
                )
            """)

            # Cleanup log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cleanup_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    description TEXT,
                    count INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                )
            """)

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_emails_gmail_id ON emails(gmail_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_emails_sender_email ON emails(sender_email)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_unsubscribe_sender ON unsubscribe_links(sender_email)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_unsubscribe_status ON unsubscribe_links(status)"
            )

            logger.info(f"Database initialized at {self.db_path}")

    def email_exists(self, gmail_id: str) -> bool:
        """Check if an email already exists in the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM emails WHERE gmail_id = ?", (gmail_id,))
            return cursor.fetchone() is not None

    def insert_email(self, email_data: Dict[str, Any]) -> int:
        """
        Insert an email into the database.

        Args:
            email_data: Dictionary containing email fields

        Returns:
            ID of inserted row
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO emails (
                    gmail_id, thread_id, subject, sender, sender_email,
                    recipients, date, body_plain, body_html, labels, snippet, backed_up_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    email_data.get("gmail_id"),
                    email_data.get("thread_id"),
                    email_data.get("subject"),
                    email_data.get("sender"),
                    email_data.get("sender_email"),
                    email_data.get("recipients"),
                    email_data.get("date"),
                    email_data.get("body_plain"),
                    email_data.get("body_html"),
                    email_data.get("labels"),
                    email_data.get("snippet"),
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_backed_up_ids(self) -> set:
        """Get set of all backed up Gmail IDs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT gmail_id FROM emails")
            return {row["gmail_id"] for row in cursor.fetchall()}

    def insert_unsubscribe_link(self, link_data: Dict[str, Any]) -> int:
        """Insert an unsubscribe link record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO unsubscribe_links (
                    email_id, gmail_id, sender, sender_email,
                    unsubscribe_url, unsubscribe_type, status, discovered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    link_data.get("email_id"),
                    link_data.get("gmail_id"),
                    link_data.get("sender"),
                    link_data.get("sender_email"),
                    link_data.get("unsubscribe_url"),
                    link_data.get("unsubscribe_type"),
                    link_data.get("status", "pending"),
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_unsubscribe_links(
        self, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get unsubscribe links, optionally filtered by status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM unsubscribe_links WHERE status = ? ORDER BY discovered_at DESC",
                    (status,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM unsubscribe_links ORDER BY discovered_at DESC"
                )
            return [dict(row) for row in cursor.fetchall()]

    def update_unsubscribe_status(self, link_id: int, status: str) -> None:
        """Update the status of an unsubscribe link"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE unsubscribe_links
                SET status = ?, processed_at = ?
                WHERE id = ?
            """,
                (status, datetime.utcnow().isoformat(), link_id),
            )

    def unsubscribe_link_exists(self, sender_email: str, url: str) -> bool:
        """Check if an unsubscribe link already exists for a sender"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM unsubscribe_links
                WHERE sender_email = ? AND unsubscribe_url = ?
            """,
                (sender_email, url),
            )
            return cursor.fetchone() is not None

    def log_cleanup_action(
        self, action: str, description: str, count: int = 0
    ) -> None:
        """Log a cleanup action"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO cleanup_log (action, description, count, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (action, description, count, datetime.utcnow().isoformat()),
            )

    def search_emails(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Full-text search across emails.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching emails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT emails.*
                FROM emails
                JOIN emails_fts ON emails.id = emails_fts.rowid
                WHERE emails_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """,
                (query, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_email_count(self) -> int:
        """Get total number of backed up emails"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM emails")
            return cursor.fetchone()["count"]

    def get_cleanup_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cleanup statistics for the past N days"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT action, SUM(count) as total_count, COUNT(*) as times_run
                FROM cleanup_log
                WHERE timestamp >= datetime('now', ?)
                GROUP BY action
            """,
                (f"-{days} days",),
            )
            return [dict(row) for row in cursor.fetchall()]
