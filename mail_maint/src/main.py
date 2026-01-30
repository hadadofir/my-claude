"""Mail Maint - Gmail Maintenance Tool

Entry point with scheduler and CLI commands.
"""

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import schedule
import yaml
from dotenv import load_dotenv

from .database import Database
from .gmail_client import GmailClient
from .tasks import BackupTask, CleanupTask, OrganizeTask, UnsubscribeTask
from .utils.logger import get_logger, setup_logger

# Load environment variables
load_dotenv()


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Config file not found: {config_path}")
        print("Creating default config.yaml...")
        return get_default_config()

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def get_default_config() -> Dict[str, Any]:
    """Return default configuration"""
    return {
        "gmail": {
            "credentials_file": "credentials.json",
            "token_file": "token.json",
            "scopes": [
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.readonly",
            ],
        },
        "schedule": {
            "cleanup": "daily at 02:00",
            "organize": "every 6 hours",
            "backup": "daily at 03:00",
            "unsubscribe_scan": "weekly on monday",
        },
        "cleanup": {
            "delete_older_than_days": 90,
            "empty_spam": True,
            "empty_trash": True,
            "sender_blacklist": [],
        },
        "organize": {"rules": []},
        "backup": {
            "database_path": "data/mail_backup.db",
            "include_attachments": False,
        },
        "unsubscribe": {
            "auto_unsubscribe": False,
            "report_path": "data/unsubscribe_report.txt",
        },
        "logging": {
            "level": "INFO",
            "file": "logs/mail_maint.log",
            "max_size_mb": 10,
            "backup_count": 5,
        },
    }


class MailMaint:
    """Main application class"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize Mail Maint application"""
        self.config = load_config(config_path)
        self.config_path = config_path

        # Setup logging
        log_config = self.config.get("logging", {})
        self.logger = setup_logger(
            name="mail_maint",
            log_file=log_config.get("file", "logs/mail_maint.log"),
            level=log_config.get("level", "INFO"),
            max_size_mb=log_config.get("max_size_mb", 10),
            backup_count=log_config.get("backup_count", 5),
        )

        # Initialize components (lazy loaded)
        self._gmail: Optional[GmailClient] = None
        self._db: Optional[Database] = None
        self._tasks: Dict[str, Any] = {}

    @property
    def gmail(self) -> GmailClient:
        """Get Gmail client (lazy loaded)"""
        if self._gmail is None:
            gmail_config = self.config.get("gmail", {})
            self._gmail = GmailClient(
                credentials_file=gmail_config.get("credentials_file", "credentials.json"),
                token_file=gmail_config.get("token_file", "token.json"),
                scopes=gmail_config.get("scopes"),
            )
        return self._gmail

    @property
    def db(self) -> Database:
        """Get database (lazy loaded)"""
        if self._db is None:
            backup_config = self.config.get("backup", {})
            self._db = Database(
                db_path=backup_config.get("database_path", "data/mail_backup.db")
            )
        return self._db

    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        self.logger.info("Starting authentication...")
        if self.gmail.authenticate():
            self.logger.info("Authentication successful!")
            return True
        self.logger.error("Authentication failed")
        return False

    def get_task(self, task_name: str) -> Optional[Any]:
        """Get a task instance by name"""
        if task_name not in self._tasks:
            if task_name == "backup":
                self._tasks[task_name] = BackupTask(
                    self.gmail, self.db, self.config.get("backup", {})
                )
            elif task_name == "cleanup":
                self._tasks[task_name] = CleanupTask(
                    self.gmail, self.db, self.config.get("cleanup", {})
                )
            elif task_name == "organize":
                self._tasks[task_name] = OrganizeTask(
                    self.gmail, self.config.get("organize", {})
                )
            elif task_name == "unsubscribe":
                self._tasks[task_name] = UnsubscribeTask(
                    self.gmail, self.db, self.config.get("unsubscribe", {})
                )
            else:
                return None
        return self._tasks.get(task_name)

    def run_task(self, task_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Run a specific task"""
        task = self.get_task(task_name)
        if not task:
            self.logger.error(f"Unknown task: {task_name}")
            return {"error": f"Unknown task: {task_name}"}

        self.logger.info(f"Running task: {task_name} (dry_run={dry_run})")
        return task.run(dry_run=dry_run)

    def setup_schedule(self) -> None:
        """Set up scheduled tasks based on configuration"""
        schedule_config = self.config.get("schedule", {})

        for task_name, schedule_str in schedule_config.items():
            task_name_normalized = task_name.replace("_scan", "")
            self._schedule_task(task_name_normalized, schedule_str)

    def _schedule_task(self, task_name: str, schedule_str: str) -> None:
        """Parse schedule string and set up task"""
        schedule_str = schedule_str.lower()

        def task_runner():
            try:
                self.run_task(task_name)
            except Exception as e:
                self.logger.error(f"Error running scheduled task {task_name}: {e}")

        # Parse different schedule formats
        if "every" in schedule_str:
            # "every 6 hours", "every 30 minutes", "every day"
            match = re.search(r"every\s+(\d+)?\s*(hour|minute|day|week)", schedule_str)
            if match:
                amount = int(match.group(1)) if match.group(1) else 1
                unit = match.group(2)

                if unit == "minute":
                    schedule.every(amount).minutes.do(task_runner)
                elif unit == "hour":
                    schedule.every(amount).hours.do(task_runner)
                elif unit == "day":
                    schedule.every(amount).days.do(task_runner)
                elif unit == "week":
                    schedule.every(amount).weeks.do(task_runner)

                self.logger.info(f"Scheduled {task_name}: every {amount} {unit}(s)")

        elif "daily at" in schedule_str:
            # "daily at 02:00"
            match = re.search(r"daily at (\d{1,2}:\d{2})", schedule_str)
            if match:
                time_str = match.group(1)
                schedule.every().day.at(time_str).do(task_runner)
                self.logger.info(f"Scheduled {task_name}: daily at {time_str}")

        elif "weekly on" in schedule_str:
            # "weekly on monday"
            match = re.search(
                r"weekly on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                schedule_str,
            )
            if match:
                day = match.group(1)
                getattr(schedule.every(), day).do(task_runner)
                self.logger.info(f"Scheduled {task_name}: weekly on {day}")

    def run_scheduler(self) -> None:
        """Run the scheduler in a loop"""
        self.logger.info("Starting scheduler...")
        self.setup_schedule()

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def status(self) -> Dict[str, Any]:
        """Get current status of all tasks"""
        backup_task = self.get_task("backup")
        unsubscribe_task = self.get_task("unsubscribe")

        return {
            "backup": backup_task.get_backup_status() if backup_task else {},
            "unsubscribe": unsubscribe_task.get_stats() if unsubscribe_task else {},
            "database": {
                "emails_backed_up": self.db.get_email_count(),
                "cleanup_stats": self.db.get_cleanup_stats(),
            },
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Mail Maint - Gmail Maintenance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --setup              Complete OAuth setup
  python -m src.main --task backup        Run backup task
  python -m src.main --task cleanup --dry-run   Preview cleanup
  python -m src.main                      Start scheduler
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run OAuth setup to authenticate with Gmail",
    )

    parser.add_argument(
        "--task",
        "-t",
        choices=["backup", "cleanup", "organize", "unsubscribe"],
        help="Run a specific task",
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview actions without making changes",
    )

    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Show current status",
    )

    parser.add_argument(
        "--unsubscribe-report",
        action="store_true",
        help="Generate unsubscribe opportunities report",
    )

    args = parser.parse_args()

    # Change to script directory for relative paths
    script_dir = Path(__file__).parent.parent
    if script_dir.exists():
        import os
        os.chdir(script_dir)

    # Initialize app
    app = MailMaint(config_path=args.config)

    # Handle commands
    if args.setup:
        if app.authenticate():
            print("Setup complete! Gmail API authenticated.")
            print("\nYou can now run tasks:")
            print("  python -m src.main --task backup --dry-run")
            print("  python -m src.main --task cleanup --dry-run")
            sys.exit(0)
        else:
            print("Setup failed. Check credentials.json and try again.")
            sys.exit(1)

    if args.status:
        if not app.authenticate():
            sys.exit(1)

        status = app.status()
        print("\n=== Mail Maint Status ===")
        print(f"\nBackup:")
        print(f"  Emails in database: {status['backup'].get('emails_in_database', 'N/A')}")
        print(f"  Emails in Gmail: {status['backup'].get('emails_in_gmail', 'N/A')}")
        print(f"  Backup coverage: {status['backup'].get('backup_percentage', 0)}%")
        print(f"\nUnsubscribe tracking:")
        print(f"  Total links found: {status['unsubscribe'].get('total_links', 0)}")
        print(f"  Pending: {status['unsubscribe'].get('pending', 0)}")
        print(f"  Unique senders: {status['unsubscribe'].get('unique_senders', 0)}")
        sys.exit(0)

    if args.unsubscribe_report:
        if not app.authenticate():
            sys.exit(1)

        unsub_task = app.get_task("unsubscribe")
        report_path = app.config.get("unsubscribe", {}).get(
            "report_path", "data/unsubscribe_report.txt"
        )
        report = unsub_task.generate_report(report_path)
        print(report)
        sys.exit(0)

    if args.task:
        if not app.authenticate():
            sys.exit(1)

        result = app.run_task(args.task, dry_run=args.dry_run)
        print(f"\nTask '{args.task}' completed:")
        for key, value in result.items():
            if not isinstance(value, (list, set)):
                print(f"  {key}: {value}")
        sys.exit(0)

    # Default: run scheduler
    if not app.authenticate():
        sys.exit(1)

    print("Starting Mail Maint scheduler...")
    print("Press Ctrl+C to stop")
    try:
        app.run_scheduler()
    except KeyboardInterrupt:
        print("\nScheduler stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
