"""Cleanup task - Delete old and unwanted emails"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..database import Database
from ..gmail_client import GmailClient
from ..utils.logger import get_logger

logger = get_logger("cleanup")


class CleanupTask:
    """Task to clean up old and unwanted emails"""

    def __init__(
        self,
        gmail_client: GmailClient,
        database: Database,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize cleanup task.

        Args:
            gmail_client: Authenticated Gmail client
            database: Database instance
            config: Cleanup configuration
        """
        self.gmail = gmail_client
        self.db = database
        self.config = config or {}

    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Run the cleanup task based on configuration.

        Args:
            dry_run: If True, don't actually delete, just report what would be done

        Returns:
            Dictionary with cleanup statistics
        """
        logger.info(f"Starting cleanup task (dry_run={dry_run})")

        stats = {
            "old_emails_deleted": 0,
            "blacklist_deleted": 0,
            "spam_emptied": 0,
            "trash_emptied": 0,
            "errors": 0,
        }

        # Delete old emails
        delete_older_than = self.config.get("delete_older_than_days", 90)
        if delete_older_than:
            result = self.delete_old_emails(delete_older_than, dry_run)
            stats["old_emails_deleted"] = result.get("deleted", 0)
            stats["errors"] += result.get("errors", 0)

        # Delete emails from blacklisted senders
        blacklist = self.config.get("sender_blacklist", [])
        if blacklist:
            result = self.delete_from_senders(blacklist, dry_run)
            stats["blacklist_deleted"] = result.get("deleted", 0)
            stats["errors"] += result.get("errors", 0)

        # Empty spam
        if self.config.get("empty_spam", True):
            result = self.empty_spam(dry_run)
            stats["spam_emptied"] = result.get("deleted", 0)

        # Empty trash
        if self.config.get("empty_trash", True):
            result = self.empty_trash(dry_run)
            stats["trash_emptied"] = result.get("deleted", 0)

        # Log action to database
        if not dry_run:
            total_deleted = (
                stats["old_emails_deleted"]
                + stats["blacklist_deleted"]
                + stats["spam_emptied"]
                + stats["trash_emptied"]
            )
            self.db.log_cleanup_action(
                "cleanup_run",
                f"Deleted {total_deleted} emails",
                total_deleted,
            )

        logger.info(f"Cleanup complete: {stats}")
        return stats

    def delete_old_emails(
        self, days: int, dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Delete emails older than specified days.

        Args:
            days: Delete emails older than this many days
            dry_run: If True, don't actually delete

        Returns:
            Dictionary with deleted count and errors
        """
        logger.info(f"Deleting emails older than {days} days")

        # Gmail search query for old emails
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
        query = f"before:{cutoff_date}"

        deleted = 0
        errors = 0
        page_token = None

        while True:
            messages, page_token = self.gmail.list_emails(
                query=query, max_results=100, page_token=page_token
            )

            if not messages:
                break

            for msg in messages:
                if dry_run:
                    logger.debug(f"[DRY RUN] Would delete old email {msg['id']}")
                    deleted += 1
                else:
                    if self.gmail.delete_email(msg["id"], permanent=False):
                        deleted += 1
                    else:
                        errors += 1

            if not page_token:
                break

        logger.info(f"Deleted {deleted} old emails ({errors} errors)")
        return {"deleted": deleted, "errors": errors}

    def delete_from_senders(
        self, senders: List[str], dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Delete emails from blacklisted senders.

        Args:
            senders: List of sender email addresses or patterns
            dry_run: If True, don't actually delete

        Returns:
            Dictionary with deleted count and errors
        """
        logger.info(f"Deleting emails from {len(senders)} blacklisted senders")

        deleted = 0
        errors = 0

        for sender in senders:
            # Build query for this sender
            query = f"from:{sender}"
            page_token = None

            while True:
                messages, page_token = self.gmail.list_emails(
                    query=query, max_results=100, page_token=page_token
                )

                if not messages:
                    break

                for msg in messages:
                    if dry_run:
                        logger.debug(
                            f"[DRY RUN] Would delete email from {sender}: {msg['id']}"
                        )
                        deleted += 1
                    else:
                        if self.gmail.delete_email(msg["id"], permanent=False):
                            deleted += 1
                        else:
                            errors += 1

                if not page_token:
                    break

        logger.info(f"Deleted {deleted} emails from blacklisted senders")
        return {"deleted": deleted, "errors": errors}

    def empty_spam(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Empty the spam folder.

        Args:
            dry_run: If True, don't actually delete

        Returns:
            Dictionary with deleted count
        """
        logger.info("Emptying spam folder")

        messages, _ = self.gmail.list_emails(label_ids=["SPAM"], max_results=500)

        if dry_run:
            logger.info(f"[DRY RUN] Would delete {len(messages)} spam emails")
            return {"deleted": len(messages)}

        deleted = 0
        for msg in messages:
            if self.gmail.delete_email(msg["id"], permanent=True):
                deleted += 1

        logger.info(f"Emptied spam: {deleted} emails deleted")
        return {"deleted": deleted}

    def empty_trash(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Empty the trash folder.

        Args:
            dry_run: If True, don't actually delete

        Returns:
            Dictionary with deleted count
        """
        logger.info("Emptying trash folder")

        messages, _ = self.gmail.list_emails(label_ids=["TRASH"], max_results=500)

        if dry_run:
            logger.info(f"[DRY RUN] Would delete {len(messages)} trash emails")
            return {"deleted": len(messages)}

        deleted = 0
        for msg in messages:
            if self.gmail.delete_email(msg["id"], permanent=True):
                deleted += 1

        logger.info(f"Emptied trash: {deleted} emails deleted")
        return {"deleted": deleted}

    def preview_cleanup(self) -> Dict[str, Any]:
        """
        Preview what would be cleaned up without making changes.

        Returns:
            Dictionary with counts of emails that would be affected
        """
        preview = {
            "old_emails": 0,
            "blacklist_emails": 0,
            "spam_emails": 0,
            "trash_emails": 0,
        }

        # Count old emails
        delete_older_than = self.config.get("delete_older_than_days", 90)
        if delete_older_than:
            cutoff_date = (datetime.now() - timedelta(days=delete_older_than)).strftime(
                "%Y/%m/%d"
            )
            preview["old_emails"] = self.gmail.get_email_count(f"before:{cutoff_date}")

        # Count blacklist emails
        blacklist = self.config.get("sender_blacklist", [])
        for sender in blacklist:
            preview["blacklist_emails"] += self.gmail.get_email_count(f"from:{sender}")

        # Count spam and trash
        messages, _ = self.gmail.list_emails(label_ids=["SPAM"], max_results=1)
        preview["spam_emails"] = self.gmail.get_email_count("in:spam")

        messages, _ = self.gmail.list_emails(label_ids=["TRASH"], max_results=1)
        preview["trash_emails"] = self.gmail.get_email_count("in:trash")

        preview["total"] = sum(preview.values())
        return preview
