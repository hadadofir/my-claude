"""Unsubscribe task - Find and extract unsubscribe opportunities"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from bs4 import BeautifulSoup

from ..database import Database
from ..gmail_client import GmailClient
from ..utils.logger import get_logger

logger = get_logger("unsubscribe")


class UnsubscribeTask:
    """Task to find unsubscribe opportunities in emails"""

    # Common unsubscribe link patterns
    UNSUBSCRIBE_PATTERNS = [
        r"unsubscribe",
        r"opt[-_]?out",
        r"remove[-_]?me",
        r"stop[-_]?emails",
        r"email[-_]?preferences",
        r"manage[-_]?subscriptions?",
        r"notification[-_]?settings?",
    ]

    def __init__(
        self,
        gmail_client: GmailClient,
        database: Database,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize unsubscribe task.

        Args:
            gmail_client: Authenticated Gmail client
            database: Database instance
            config: Unsubscribe configuration
        """
        self.gmail = gmail_client
        self.db = database
        self.config = config or {}

    def run(
        self, dry_run: bool = False, max_emails: int = 500
    ) -> Dict[str, Any]:
        """
        Scan emails for unsubscribe opportunities.

        Args:
            dry_run: If True, don't store to database
            max_emails: Maximum number of emails to scan

        Returns:
            Dictionary with scan statistics
        """
        logger.info(f"Starting unsubscribe scan (dry_run={dry_run})")

        stats = {
            "emails_scanned": 0,
            "unsubscribe_found": 0,
            "new_links": 0,
            "duplicate_links": 0,
            "senders_with_unsubscribe": set(),
        }

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
                stats["emails_scanned"] += 1

                email_data = self.gmail.get_email(msg["id"])
                if not email_data:
                    continue

                # Extract unsubscribe links
                links = self._extract_unsubscribe_links(email_data)

                if links:
                    stats["unsubscribe_found"] += 1
                    stats["senders_with_unsubscribe"].add(
                        email_data.get("sender_email", "")
                    )

                    for link_info in links:
                        # Check if already tracked
                        if self.db.unsubscribe_link_exists(
                            email_data.get("sender_email", ""),
                            link_info["url"],
                        ):
                            stats["duplicate_links"] += 1
                            continue

                        if not dry_run:
                            self.db.insert_unsubscribe_link(
                                {
                                    "gmail_id": email_data.get("gmail_id"),
                                    "sender": email_data.get("sender"),
                                    "sender_email": email_data.get("sender_email"),
                                    "unsubscribe_url": link_info["url"],
                                    "unsubscribe_type": link_info["type"],
                                    "status": "pending",
                                }
                            )

                        stats["new_links"] += 1

                emails_processed += 1
                if emails_processed >= max_emails:
                    break

            if not page_token:
                break

        stats["unique_senders"] = len(stats["senders_with_unsubscribe"])
        stats["senders_with_unsubscribe"] = list(stats["senders_with_unsubscribe"])

        logger.info(
            f"Unsubscribe scan complete: found {stats['new_links']} new links "
            f"from {stats['unique_senders']} senders"
        )

        return stats

    def _extract_unsubscribe_links(
        self, email_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extract unsubscribe links from email.

        Args:
            email_data: Parsed email data

        Returns:
            List of dictionaries with 'url' and 'type' keys
        """
        links = []

        # Check List-Unsubscribe header first (most reliable)
        list_unsubscribe = email_data.get("list_unsubscribe", "")
        if list_unsubscribe:
            header_links = self._parse_list_unsubscribe_header(list_unsubscribe)
            links.extend(header_links)

        # Parse HTML body for unsubscribe links
        body_html = email_data.get("body_html", "")
        if body_html:
            html_links = self._extract_links_from_html(body_html)
            links.extend(html_links)

        # Parse plain text body
        body_plain = email_data.get("body_plain", "")
        if body_plain:
            text_links = self._extract_links_from_text(body_plain)
            links.extend(text_links)

        # Deduplicate
        seen_urls = set()
        unique_links = []
        for link in links:
            url = link["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique_links.append(link)

        return unique_links

    def _parse_list_unsubscribe_header(
        self, header_value: str
    ) -> List[Dict[str, str]]:
        """Parse List-Unsubscribe header value"""
        links = []

        # Header format: <mailto:unsubscribe@example.com>, <https://example.com/unsub>
        matches = re.findall(r"<([^>]+)>", header_value)

        for match in matches:
            if match.startswith("mailto:"):
                links.append({"url": match, "type": "mailto"})
            elif match.startswith("http"):
                links.append({"url": match, "type": "http_header"})

        return links

    def _extract_links_from_html(self, html: str) -> List[Dict[str, str]]:
        """Extract unsubscribe links from HTML body"""
        links = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find all anchor tags
            for a_tag in soup.find_all("a", href=True):
                href = a_tag.get("href", "")
                text = a_tag.get_text().lower()
                href_lower = href.lower()

                # Check if link text or URL contains unsubscribe keywords
                is_unsubscribe = False
                for pattern in self.UNSUBSCRIBE_PATTERNS:
                    if re.search(pattern, text) or re.search(pattern, href_lower):
                        is_unsubscribe = True
                        break

                if is_unsubscribe and href.startswith("http"):
                    links.append({"url": unquote(href), "type": "http_body"})

        except Exception as e:
            logger.debug(f"Error parsing HTML: {e}")

        return links

    def _extract_links_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract unsubscribe links from plain text body"""
        links = []

        # Find URLs near unsubscribe keywords
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Check if line contains unsubscribe keyword
            has_keyword = False
            for pattern in self.UNSUBSCRIBE_PATTERNS:
                if re.search(pattern, line_lower):
                    has_keyword = True
                    break

            if has_keyword:
                # Extract URLs from this line and adjacent lines
                context = " ".join(lines[max(0, i - 1) : i + 2])
                url_matches = re.findall(
                    r"https?://[^\s<>\"']+", context
                )
                for url in url_matches:
                    # Clean URL
                    url = url.rstrip(".,;:)")
                    links.append({"url": url, "type": "text_body"})

        return links

    def get_pending_unsubscribes(self) -> List[Dict[str, Any]]:
        """Get all pending unsubscribe links"""
        return self.db.get_unsubscribe_links(status="pending")

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a report of unsubscribe opportunities.

        Args:
            output_path: Path to save report (optional)

        Returns:
            Report content as string
        """
        links = self.db.get_unsubscribe_links()

        # Group by sender
        senders: Dict[str, List[Dict[str, Any]]] = {}
        for link in links:
            sender = link.get("sender_email", "unknown")
            if sender not in senders:
                senders[sender] = []
            senders[sender].append(link)

        # Build report
        report_lines = [
            "=" * 60,
            "UNSUBSCRIBE OPPORTUNITIES REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total senders: {len(senders)}",
            f"Total links: {len(links)}",
            "=" * 60,
            "",
        ]

        for sender, sender_links in sorted(senders.items()):
            report_lines.append(f"\n--- {sender} ---")
            for link in sender_links:
                status = link.get("status", "unknown")
                link_type = link.get("unsubscribe_type", "unknown")
                url = link.get("unsubscribe_url", "")

                report_lines.append(f"  [{status}] ({link_type})")
                report_lines.append(f"  {url}")
                report_lines.append("")

        report = "\n".join(report_lines)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")

        return report

    def mark_as_processed(self, link_id: int, status: str = "completed") -> None:
        """Mark an unsubscribe link as processed"""
        self.db.update_unsubscribe_status(link_id, status)

    def get_stats(self) -> Dict[str, Any]:
        """Get unsubscribe tracking statistics"""
        all_links = self.db.get_unsubscribe_links()

        stats = {
            "total_links": len(all_links),
            "pending": 0,
            "completed": 0,
            "failed": 0,
            "unique_senders": len(set(l.get("sender_email") for l in all_links)),
        }

        for link in all_links:
            status = link.get("status", "pending")
            if status in stats:
                stats[status] += 1

        return stats
