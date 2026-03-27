# src/email_client.py
from datetime import datetime, timedelta
from email.header import decode_header
from imap_tools import MailBox


class EmailClientError(Exception):
    """Email client error."""
    pass


class EmailClient:
    """IMAP email client for fetching recent emails."""

    def __init__(self, config: dict):
        """
        Initialize email client.

        Args:
            config: Configuration dictionary with imap_server, imap_port, email, password.
        """
        self.server = config["imap_server"]
        self.port = config.get("imap_port", 993)
        self.email = config["email"]
        self.password = config["password"]

    def fetch_recent_emails(self, days_ago: int = 1, max_emails: int = 10) -> list[dict]:
        """
        Fetch recent emails from INBOX.

        Args:
            days_ago: Number of days to look back (default: 1).
            max_emails: Maximum number of emails to fetch (default: 10).

        Returns:
            List of email dictionaries with 'subject', 'from', 'date', 'body' keys.

        Raises:
            EmailClientError: If connection or fetch fails.
        """
        emails = []
        since_date = datetime.now() - timedelta(days=days_ago)

        try:
            mailbox = MailBox(self.server)
            mailbox.login(self.email, self.password)
            # Select INBOX
            mailbox.select("INBOX")

            # Search for emails since date
            criteria = f"SINCE {since_date.strftime('%d-%b-%Y')}"
            msg_ids = mailbox.search(criteria)

            if not msg_ids:
                mailbox.logout()
                return []

            # Fetch emails (respect max_emails limit)
            for msg in mailbox.fetch(msg_ids[:max_emails], mark_seen=False):
                emails.append({
                    "subject": self._decode_header(msg.subject),
                    "from": msg.from_,
                    "date": msg.date_str,
                    "body": msg.text or msg.html or "",
                })

            mailbox.logout()

        except Exception as e:
            raise EmailClientError(f"Failed to connect or fetch emails: {e}")

        return emails

    def _decode_header(self, header: str) -> str:
        """
        Decode email header.

        Args:
            header: Raw header string.

        Returns:
            Decoded header string.
        """
        if header is None:
            return ""

        decoded = []
        for content, encoding in decode_header(header):
            if isinstance(content, bytes):
                decoded.append(content.decode(encoding or "utf-8", errors="ignore"))
            else:
                decoded.append(content)

        return "".join(decoded)
