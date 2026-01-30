"""Organize task - Apply labels based on rules"""

import fnmatch
import re
from typing import Any, Dict, List, Optional

from ..gmail_client import GmailClient
from ..utils.logger import get_logger

logger = get_logger("organize")


class OrganizeTask:
    """Task to organize emails by applying labels based on rules"""

    def __init__(
        self,
        gmail_client: GmailClient,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize organize task.

        Args:
            gmail_client: Authenticated Gmail client
            config: Organization configuration with rules
        """
        self.gmail = gmail_client
        self.config = config or {}
        self.rules = self.config.get("rules", [])
        self._label_cache: Dict[str, str] = {}

    def run(self, dry_run: bool = False, max_emails: int = 500) -> Dict[str, Any]:
        """
        Run the organize task - apply labels based on rules.

        Args:
            dry_run: If True, don't actually apply labels
            max_emails: Maximum number of emails to process

        Returns:
            Dictionary with organization statistics
        """
        logger.info(f"Starting organize task (dry_run={dry_run})")

        if not self.rules:
            logger.warning("No organization rules configured")
            return {"emails_processed": 0, "labels_applied": 0}

        stats = {
            "emails_processed": 0,
            "labels_applied": 0,
            "rules_matched": {},
            "errors": 0,
        }

        # Pre-fetch/create all needed labels
        if not dry_run:
            self._ensure_labels_exist()

        # Process emails without labels (INBOX only for efficiency)
        page_token = None
        emails_processed = 0

        while emails_processed < max_emails:
            batch_size = min(100, max_emails - emails_processed)
            messages, page_token = self.gmail.list_emails(
                label_ids=["INBOX"],
                max_results=batch_size,
                page_token=page_token,
            )

            if not messages:
                break

            for msg in messages:
                stats["emails_processed"] += 1

                # Get full email to check rules
                email_data = self.gmail.get_email(msg["id"])
                if not email_data:
                    stats["errors"] += 1
                    continue

                # Check which rules match
                labels_to_apply = []
                for rule in self.rules:
                    if self._rule_matches(rule, email_data):
                        label_name = rule.get("label")
                        if label_name:
                            labels_to_apply.append(label_name)
                            rule_key = str(rule.get("match", {}))
                            stats["rules_matched"][rule_key] = (
                                stats["rules_matched"].get(rule_key, 0) + 1
                            )

                if labels_to_apply:
                    if dry_run:
                        logger.debug(
                            f"[DRY RUN] Would apply labels {labels_to_apply} to "
                            f"'{email_data.get('subject', '')[:40]}'"
                        )
                    else:
                        # Convert label names to IDs
                        label_ids = [
                            self._get_label_id(name) for name in labels_to_apply
                        ]
                        label_ids = [lid for lid in label_ids if lid]

                        if label_ids:
                            if self.gmail.modify_labels(
                                msg["id"], add_labels=label_ids
                            ):
                                stats["labels_applied"] += len(label_ids)
                            else:
                                stats["errors"] += 1

                emails_processed += 1
                if emails_processed >= max_emails:
                    break

            if not page_token:
                break

        logger.info(
            f"Organize complete: {stats['labels_applied']} labels applied "
            f"to {stats['emails_processed']} emails"
        )
        return stats

    def _rule_matches(self, rule: Dict[str, Any], email_data: Dict[str, Any]) -> bool:
        """
        Check if an email matches a rule.

        Args:
            rule: Rule definition with 'match' criteria
            email_data: Email data dictionary

        Returns:
            True if email matches the rule
        """
        match_criteria = rule.get("match", {})

        for field, pattern in match_criteria.items():
            email_value = self._get_email_field(email_data, field)
            if not email_value:
                return False

            # Support wildcard patterns
            if "*" in pattern:
                if not fnmatch.fnmatch(email_value.lower(), pattern.lower()):
                    return False
            # Support regex patterns (prefixed with 'regex:')
            elif pattern.startswith("regex:"):
                regex_pattern = pattern[6:]
                if not re.search(regex_pattern, email_value, re.IGNORECASE):
                    return False
            # Exact substring match (case-insensitive)
            else:
                if pattern.lower() not in email_value.lower():
                    return False

        return True

    def _get_email_field(self, email_data: Dict[str, Any], field: str) -> Optional[str]:
        """Get a field value from email data"""
        field_map = {
            "from": "sender_email",
            "sender": "sender_email",
            "to": "recipients",
            "subject": "subject",
            "body": "body_plain",
        }
        mapped_field = field_map.get(field.lower(), field)
        return email_data.get(mapped_field, "")

    def _ensure_labels_exist(self) -> None:
        """Create all labels needed by rules"""
        for rule in self.rules:
            label_name = rule.get("label")
            if label_name and label_name not in self._label_cache:
                label_id = self.gmail.get_or_create_label(label_name)
                if label_id:
                    self._label_cache[label_name] = label_id
                    logger.debug(f"Ensured label exists: {label_name}")

    def _get_label_id(self, label_name: str) -> Optional[str]:
        """Get label ID from cache or Gmail"""
        if label_name in self._label_cache:
            return self._label_cache[label_name]

        label_id = self.gmail.get_or_create_label(label_name)
        if label_id:
            self._label_cache[label_name] = label_id
        return label_id

    def test_rules(self, num_emails: int = 10) -> List[Dict[str, Any]]:
        """
        Test rules against recent emails without applying changes.

        Args:
            num_emails: Number of recent emails to test against

        Returns:
            List of matches showing which rules would apply to which emails
        """
        logger.info(f"Testing rules against {num_emails} recent emails")

        matches = []
        messages, _ = self.gmail.list_emails(max_results=num_emails)

        for msg in messages:
            email_data = self.gmail.get_email(msg["id"])
            if not email_data:
                continue

            email_matches = {
                "email_id": msg["id"],
                "subject": email_data.get("subject", "")[:60],
                "sender": email_data.get("sender_email", ""),
                "matching_rules": [],
            }

            for i, rule in enumerate(self.rules):
                if self._rule_matches(rule, email_data):
                    email_matches["matching_rules"].append(
                        {
                            "rule_index": i,
                            "match": rule.get("match"),
                            "label": rule.get("label"),
                        }
                    )

            if email_matches["matching_rules"]:
                matches.append(email_matches)

        return matches

    def list_rules(self) -> List[Dict[str, Any]]:
        """List all configured rules"""
        return self.rules
