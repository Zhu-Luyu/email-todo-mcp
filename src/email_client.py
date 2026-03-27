# src/email_client.py
from datetime import datetime, timedelta
from email.header import decode_header
import imaplib
import email
from email.message import Message


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
            # Connect to IMAP server over SSL
            mail = imaplib.IMAP4_SSL(self.server, self.port)

            # Login
            mail.login(self.email, self.password)

            # Select INBOX
            status, data = mail.select("INBOX")
            if status != "OK":
                mail.close()
                mail.logout()
                raise EmailClientError(f"Failed to select INBOX: {data}")

            # Search for emails since date
            criteria = f'(SINCE "{since_date.strftime("%d-%b-%Y")}")'
            status, messages = mail.search(None, criteria)

            if status != "OK" or not messages[0]:
                mail.close()
                mail.logout()
                return []

            # Get message IDs
            msg_ids = messages[0].split()

            # Limit to max_emails
            msg_ids = msg_ids[-max_emails:]  # Get most recent

            # Fetch each email
            for msg_id in msg_ids:
                # Fetch the email body
                status, msg_data = mail.fetch(msg_id, '(RFC822)')

                if status == "OK":
                    # Parse the email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract email data
                    email_subject = msg.get("Subject", "")
                    email_subject = self._decode_header(email_subject)

                    email_from = msg.get("From", "")
                    email_date = msg.get("Date", "")

                    # Extract body
                    email_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition", ""))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    email_body = part.get_payload(decode=True)
                                    if isinstance(email_body, bytes):
                                        email_body = email_body.decode('utf-8', errors='ignore')
                                except:
                                    pass
                                break
                    else:
                        try:
                            email_body = msg.get_payload(decode=True)
                            if isinstance(email_body, bytes):
                                email_body = email_body.decode('utf-8', errors='ignore')
                        except:
                            email_body = str(msg.get_payload())

                    emails.append({
                        "subject": email_subject,
                        "from": email_from,
                        "date": email_date,
                        "body": email_body[:5000],  # Limit body size
                    })

            # Close connection
            mail.close()
            mail.logout()

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
