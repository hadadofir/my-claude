"""Gmail API client wrapper with OAuth 2.0 authentication"""

import base64
import email
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .utils.logger import get_logger

logger = get_logger("gmail_client")


class RateLimiter:
    """Simple rate limiter for Gmail API calls"""

    def __init__(self, calls_per_second: float = 10):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


class GmailClient:
    """Gmail API client with OAuth 2.0 authentication and rate limiting"""

    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        scopes: Optional[List[str]] = None,
    ):
        """
        Initialize Gmail client.

        Args:
            credentials_file: Path to OAuth credentials file
            token_file: Path to store/load OAuth token
            scopes: Gmail API scopes to request
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.scopes = scopes or self.DEFAULT_SCOPES
        self.service = None
        self.rate_limiter = RateLimiter(calls_per_second=10)

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0.

        Returns:
            True if authentication successful
        """
        creds = None

        # Load existing token
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), self.scopes)
            logger.info("Loaded existing credentials from token file")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                if not self.credentials_file.exists():
                    logger.error(
                        f"Credentials file not found: {self.credentials_file}"
                    )
                    logger.error(
                        "Please download credentials.json from Google Cloud Console"
                    )
                    return False

                logger.info("Starting OAuth flow - browser will open for authorization")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), self.scopes
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {self.token_file}")

        # Build service
        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API client authenticated successfully")
        return True

    def _execute_with_retry(
        self, request: Callable, max_retries: int = 3
    ) -> Optional[Any]:
        """Execute API request with rate limiting and retry logic"""
        self.rate_limiter.wait()

        for attempt in range(max_retries):
            try:
                return request.execute()
            except HttpError as e:
                if e.resp.status == 429:  # Rate limit exceeded
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif e.resp.status in (500, 503):  # Server error
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

        return None

    def list_emails(
        self,
        query: str = "",
        max_results: int = 100,
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        List emails matching query.

        Args:
            query: Gmail search query (same syntax as Gmail search box)
            max_results: Maximum number of results to return
            label_ids: Filter by label IDs
            page_token: Token for pagination

        Returns:
            Tuple of (list of email metadata, next page token)
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            request_params = {
                "userId": "me",
                "maxResults": min(max_results, 500),  # Gmail API limit
            }
            if query:
                request_params["q"] = query
            if label_ids:
                request_params["labelIds"] = label_ids
            if page_token:
                request_params["pageToken"] = page_token

            result = self._execute_with_retry(
                self.service.users().messages().list(**request_params)
            )

            if not result:
                return [], None

            messages = result.get("messages", [])
            next_token = result.get("nextPageToken")

            logger.debug(f"Listed {len(messages)} emails")
            return messages, next_token

        except HttpError as e:
            logger.error(f"Error listing emails: {e}")
            return [], None

    def get_email(
        self, email_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Get full email details.

        Args:
            email_id: Gmail message ID
            format: Response format (minimal, full, raw, metadata)

        Returns:
            Email data dictionary or None
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            result = self._execute_with_retry(
                self.service.users()
                .messages()
                .get(userId="me", id=email_id, format=format)
            )
            return self._parse_email(result) if result else None

        except HttpError as e:
            logger.error(f"Error getting email {email_id}: {e}")
            return None

    def _parse_email(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API message into structured data"""
        headers = {
            h["name"].lower(): h["value"]
            for h in message.get("payload", {}).get("headers", [])
        }

        # Extract sender email from "From" header
        sender = headers.get("from", "")
        sender_email = ""
        email_match = re.search(r"<([^>]+)>", sender)
        if email_match:
            sender_email = email_match.group(1)
        elif "@" in sender:
            sender_email = sender.strip()

        # Get body content
        body_plain, body_html = self._extract_body(message.get("payload", {}))

        return {
            "gmail_id": message.get("id"),
            "thread_id": message.get("threadId"),
            "subject": headers.get("subject", "(No Subject)"),
            "sender": sender,
            "sender_email": sender_email.lower(),
            "recipients": headers.get("to", ""),
            "date": headers.get("date", ""),
            "body_plain": body_plain,
            "body_html": body_html,
            "labels": ",".join(message.get("labelIds", [])),
            "snippet": message.get("snippet", ""),
            "list_unsubscribe": headers.get("list-unsubscribe", ""),
        }

    def _extract_body(
        self, payload: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract plain text and HTML body from email payload"""
        body_plain = None
        body_html = None

        def process_part(part: Dict[str, Any]) -> None:
            nonlocal body_plain, body_html

            mime_type = part.get("mimeType", "")
            body = part.get("body", {})

            if body.get("data"):
                decoded = base64.urlsafe_b64decode(body["data"]).decode(
                    "utf-8", errors="replace"
                )
                if mime_type == "text/plain" and not body_plain:
                    body_plain = decoded
                elif mime_type == "text/html" and not body_html:
                    body_html = decoded

            # Process nested parts
            for sub_part in part.get("parts", []):
                process_part(sub_part)

        process_part(payload)
        return body_plain, body_html

    def delete_email(self, email_id: str, permanent: bool = False) -> bool:
        """
        Delete an email.

        Args:
            email_id: Gmail message ID
            permanent: If True, permanently delete. If False, move to trash.

        Returns:
            True if successful
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            if permanent:
                self._execute_with_retry(
                    self.service.users().messages().delete(userId="me", id=email_id)
                )
            else:
                self._execute_with_retry(
                    self.service.users().messages().trash(userId="me", id=email_id)
                )
            logger.debug(f"Deleted email {email_id} (permanent={permanent})")
            return True

        except HttpError as e:
            logger.error(f"Error deleting email {email_id}: {e}")
            return False

    def modify_labels(
        self,
        email_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        """
        Modify labels on an email.

        Args:
            email_id: Gmail message ID
            add_labels: Label IDs to add
            remove_labels: Label IDs to remove

        Returns:
            True if successful
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            self._execute_with_retry(
                self.service.users()
                .messages()
                .modify(userId="me", id=email_id, body=body)
            )
            logger.debug(f"Modified labels on {email_id}")
            return True

        except HttpError as e:
            logger.error(f"Error modifying labels on {email_id}: {e}")
            return False

    def batch_delete(
        self, email_ids: List[str], permanent: bool = False
    ) -> Tuple[int, int]:
        """
        Delete multiple emails.

        Args:
            email_ids: List of Gmail message IDs
            permanent: If True, permanently delete

        Returns:
            Tuple of (success count, failure count)
        """
        success = 0
        failed = 0

        for email_id in email_ids:
            if self.delete_email(email_id, permanent):
                success += 1
            else:
                failed += 1

        logger.info(f"Batch delete: {success} succeeded, {failed} failed")
        return success, failed

    def batch_modify_labels(
        self,
        email_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Tuple[int, int]:
        """
        Modify labels on multiple emails.

        Args:
            email_ids: List of Gmail message IDs
            add_labels: Label IDs to add
            remove_labels: Label IDs to remove

        Returns:
            Tuple of (success count, failure count)
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            body = {"ids": email_ids}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            self._execute_with_retry(
                self.service.users().messages().batchModify(userId="me", body=body)
            )
            logger.info(f"Batch modified labels on {len(email_ids)} emails")
            return len(email_ids), 0

        except HttpError as e:
            logger.error(f"Error in batch modify: {e}")
            return 0, len(email_ids)

    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all labels in the mailbox"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            result = self._execute_with_retry(
                self.service.users().labels().list(userId="me")
            )
            return result.get("labels", []) if result else []

        except HttpError as e:
            logger.error(f"Error getting labels: {e}")
            return []

    def create_label(self, name: str) -> Optional[str]:
        """
        Create a new label.

        Args:
            name: Label name (can include / for nested labels)

        Returns:
            Label ID if created successfully
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            label_body = {
                "name": name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }
            result = self._execute_with_retry(
                self.service.users().labels().create(userId="me", body=label_body)
            )
            if result:
                logger.info(f"Created label: {name}")
                return result.get("id")
            return None

        except HttpError as e:
            if e.resp.status == 409:  # Label already exists
                # Find and return existing label ID
                labels = self.get_labels()
                for label in labels:
                    if label.get("name") == name:
                        return label.get("id")
            logger.error(f"Error creating label {name}: {e}")
            return None

    def get_or_create_label(self, name: str) -> Optional[str]:
        """Get label ID, creating it if it doesn't exist"""
        labels = self.get_labels()
        for label in labels:
            if label.get("name") == name:
                return label.get("id")
        return self.create_label(name)

    def empty_trash(self) -> bool:
        """Empty the trash folder"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            self._execute_with_retry(
                self.service.users().messages().delete(userId="me", id="me/trash")
            )
            # Note: The above doesn't work - need to use different approach
            # List all trash messages and delete them
            messages, _ = self.list_emails(label_ids=["TRASH"], max_results=500)
            if messages:
                for msg in messages:
                    self.delete_email(msg["id"], permanent=True)
            logger.info("Emptied trash")
            return True
        except HttpError as e:
            logger.error(f"Error emptying trash: {e}")
            return False

    def empty_spam(self) -> bool:
        """Empty the spam folder"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            messages, _ = self.list_emails(label_ids=["SPAM"], max_results=500)
            if messages:
                for msg in messages:
                    self.delete_email(msg["id"], permanent=True)
            logger.info("Emptied spam")
            return True
        except HttpError as e:
            logger.error(f"Error emptying spam: {e}")
            return False

    def get_email_count(self, query: str = "") -> int:
        """Get count of emails matching query"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            result = self._execute_with_retry(
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=1)
            )
            return result.get("resultSizeEstimate", 0) if result else 0
        except HttpError as e:
            logger.error(f"Error getting email count: {e}")
            return 0
