# tests/test_email_client.py
import pytest
from datetime import datetime, timedelta
from src.email_client import EmailClient, EmailClientError
from src.config import ConfigError


class TestEmailClient:
    """Tests for EmailClient class."""

    def test_init_with_config(self):
        """Test initializing email client with config."""
        config = {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass"
        }
        client = EmailClient(config)
        assert client.server == "imap.test.com"
        assert client.port == 993
        assert client.email == "test@test.com"

    def test_fetch_recent_emails_missing_days_param(self, mocker):
        """Test fetching emails with default days parameter."""
        config = {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass"
        }
        client = EmailClient(config)

        # Mock the IMAP connection
        mock_mailbox = mocker.MagicMock()
        mock_mailbox.list.return_value = ("OK", [br'(\HasNoChildren) "." "INBOX"'])
        mock_mailbox.login.return_value = ("OK", [])
        mock_mailbox.select.return_value = ("OK", [])
        mock_mailbox.search.return_value = ("OK", [b"1 2 3"])

        # Create mock email message objects
        mock_msg1 = mocker.MagicMock()
        mock_msg1.subject = "Test Email 1"
        mock_msg1.from_ = "sender1@test.com"
        mock_msg1.date_str = "Mon, 27 Mar 2026 10:00:00"
        mock_msg1.text = "Body 1"
        mock_msg1.html = None

        mock_msg2 = mocker.MagicMock()
        mock_msg2.subject = "Test Email 2"
        mock_msg2.from_ = "sender2@test.com"
        mock_msg2.date_str = "Mon, 27 Mar 2026 11:00:00"
        mock_msg2.text = "Body 2"
        mock_msg2.html = None

        mock_mailbox.fetch.return_value = [mock_msg1, mock_msg2]
        mock_mailbox.logout.return_value = ("OK", [])
        mocker.patch("src.email_client.MailBox", return_value=mock_mailbox)

        emails = client.fetch_recent_emails(days_ago=1, max_emails=10)

        assert len(emails) == 2
        assert emails[0]["subject"] == "Test Email 1"
        assert emails[0]["body"] == "Body 1"
        assert emails[1]["subject"] == "Test Email 2"

    def test_fetch_recent_emails_max_limit(self, mocker):
        """Test that max_emails parameter limits results."""
        config = {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass"
        }
        client = EmailClient(config)

        mock_mailbox = mocker.MagicMock()
        mock_mailbox.list.return_value = ("OK", [])
        mock_mailbox.login.return_value = ("OK", [])
        mock_mailbox.select.return_value = ("OK", [])
        mock_mailbox.search.return_value = ("OK", [b"1 2 3 4 5"])

        # Create mock email message objects
        mock_emails = []
        for i in range(1, 4):
            mock_msg = mocker.MagicMock()
            mock_msg.subject = f"Email {i}"
            mock_msg.from_ = f"sender{i}@test.com"
            mock_msg.date_str = f"Mon, 27 Mar 2026 {10+i}:00:00"
            mock_msg.text = f"Body {i}"
            mock_msg.html = None
            mock_emails.append(mock_msg)

        mock_mailbox.fetch.return_value = mock_emails
        mock_mailbox.logout.return_value = ("OK", [])
        mocker.patch("src.email_client.MailBox", return_value=mock_mailbox)

        emails = client.fetch_recent_emails(days_ago=1, max_emails=3)

        assert len(emails) == 3

    def test_fetch_recent_emails_connection_error(self, mocker):
        """Test handling of IMAP connection errors."""
        config = {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass"
        }
        client = EmailClient(config)

        mocker.patch("src.email_client.MailBox", side_effect=Exception("Connection refused"))

        with pytest.raises(EmailClientError, match="Failed to connect"):
            client.fetch_recent_emails()

    def test_fetch_recent_emails_empty_mailbox(self, mocker):
        """Test handling of empty mailbox."""
        config = {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass"
        }
        client = EmailClient(config)

        mock_mailbox = mocker.MagicMock()
        mock_mailbox.list.return_value = ("OK", [])
        mock_mailbox.login.return_value = ("OK", [])
        mock_mailbox.select.return_value = ("OK", [])
        mock_mailbox.search.return_value = ("OK", [b""])  # No emails
        mock_mailbox.logout.return_value = ("OK", [])
        mocker.patch("src.email_client.MailBox", return_value=mock_mailbox)

        emails = client.fetch_recent_emails()

        assert emails == []
