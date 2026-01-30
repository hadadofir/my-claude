"""Backup task - Archive emails to SQLite database"""

from typing import Any, Dict, Optional

from ..database import Database
from ..gmail_client import GmailClient
from ..utils.logger import get_logger

logger = get_logger("backup")


class BackupTask:
    """Task to incrementally backup emails to SQLite database"""

    def __init__(
        self,
        gmail_client: GmailClient,
        database: Database,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize backup task.

        Args:
            gmail_client: Authenticated Gmail client
            database: Database instance
            config: Backup configuration
        """
        self.gmail = gmail_client
        self.db = database
        self.config = config or {}

    def run(self, dry_run: bool = False, max_emails: int = 1000) -> Dict[str, Any]:
        """
        Run the backup task.

        Args:
            dry_run: If True, don't actually backup, just report what would be done
            max_emails: Maximum number of emails to backup in one run

        Returns:
            Dictionary with backup statistics
        """
        logger.info(f"Starting backup task (dry_run={dry_run})")

        stats = {
            "total_scanned": 0,
            "already_backed_up": 0,
            "newly_backed_up": 0,
            "errors": 0,
        }

        # Get already backed up IDs
        backed_up_ids = self.db.get_backed_up_ids()
        logger.info(f"Found {len(backed_up_ids)} emails already in database")

        # List emails from Gmail
        page_token = None
        emails_processed = 0

        while emails_processed < max_emails:
            batch_size = min(100, max_emails - emails_processed)
            messages, page_token = self.gmail.list_emails(
                max_results=batch_size, page_token=page_token
            )

            if not messages:
                break

            for msg in messages:
                stats["total_scanned"] += 1
                gmail_id = msg["id"]

                if gmail_id in backed_up_ids:
                    stats["already_backed_up"] += 1
                    continue

                if dry_run:
                    logger.debug(f"[DRY RUN] Would backup email {gmail_id}")
                    stats["newly_backed_up"] += 1
                    continue

                # Fetch full email
                email_data = self.gmail.get_email(gmail_id)
                if not email_data:
                    logger.warning(f"Could not fetch email {gmail_id}")
                    stats["errors"] += 1
                    continue

                # Store in database
                try:
                    self.db.insert_email(email_data)
                    stats["newly_backed_up"] += 1
                    logger.debug(f"Backed up email: {email_data.get('subject', '')[:50]}")
                except Exception as e:
                    logger.error(f"Error storing email {gmail_id}: {e}")
                    stats["errors"] += 1

                emails_processed += 1
                if emails_processed >= max_emails:
                    break

            if not page_token:
                break

        logger.info(
            f"Backup complete: {stats['newly_backed_up']} new, "
            f"{stats['already_backed_up']} existing, {stats['errors']} errors"
        )

        return stats

    def backup_by_query(
        self, query: str, dry_run: bool = False, max_emails: int = 500
    ) -> Dict[str, Any]:
        """
        Backup emails matching a specific query.

        Args:
            query: Gmail search query
            dry_run: If True, don't actually backup
            max_emails: Maximum number of emails to backup

        Returns:
            Dictionary with backup statistics
        """
        logger.info(f"Backing up emails matching query: {query}")

        stats = {
            "total_scanned": 0,
            "already_backed_up": 0,
            "newly_backed_up": 0,
            "errors": 0,
        }

        backed_up_ids = self.db.get_backed_up_ids()
        page_token = None
        emails_processed = 0

        while emails_processed < max_emails:
            batch_size = min(100, max_emails - emails_processed)
            messages, page_token = self.gmail.list_emails(
                query=query, max_results=batch_size, page_token=page_token
            )

            if not messages:
                break

            for msg in messages:
                stats["total_scanned"] += 1
                gmail_id = msg["id"]

                if gmail_id in backed_up_ids:
                    stats["already_backed_up"] += 1
                    continue

                if dry_run:
                    stats["newly_backed_up"] += 1
                    continue

                email_data = self.gmail.get_email(gmail_id)
                if not email_data:
                    stats["errors"] += 1
                    continue

                try:
                    self.db.insert_email(email_data)
                    stats["newly_backed_up"] += 1
                except Exception as e:
                    logger.error(f"Error storing email {gmail_id}: {e}")
                    stats["errors"] += 1

                emails_processed += 1
                if emails_processed >= max_emails:
                    break

            if not page_token:
                break

        logger.info(
            f"Query backup complete: {stats['newly_backed_up']} backed up "
            f"from {stats['total_scanned']} scanned"
        )

        return stats

    def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status"""
        db_count = self.db.get_email_count()
        gmail_count = self.gmail.get_email_count()

        return {
            "emails_in_database": db_count,
            "emails_in_gmail": gmail_count,
            "backup_percentage": (
                round(db_count / gmail_count * 100, 1) if gmail_count > 0 else 0
            ),
        }
