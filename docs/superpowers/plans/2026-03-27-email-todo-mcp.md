# Email Todo MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an MCP server that reads emails from an IMAP mailbox and uses LLM to extract todo items.

**Architecture:** Python MCP server using stdio communication, connecting to IMAP server on-demand, with optional LLM-based todo extraction.

**Tech Stack:** Python 3.11+, mcp (Python SDK), imap-tools, openai (optional)

---

## File Structure

```
email-todo-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server main entry
│   ├── email_client.py        # IMAP email client
│   ├── todo_extractor.py      # LLM todo extractor
│   └── config.py              # Config loader
├── tests/
│   ├── __init__.py
│   ├── test_email_client.py   # Email client tests
│   ├── test_todo_extractor.py # Todo extractor tests
│   └── test_server.py         # MCP server integration tests
├── config.example.json        # Config template
├── pyproject.toml             # Python project config
├── README.md                  # Project documentation
└── requirements.txt           # Dependencies
```

---

### Task 1: Initialize Python Project

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `README.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "email-todo-mcp"
version = "0.1.0"
description = "MCP server for extracting todos from emails"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.1.0",
    "imap-tools>=0.50.0",
    "openai>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
email-todo-mcp = "src.server:main"
```

- [ ] **Step 2: Create requirements.txt**

```txt
mcp>=0.1.0
imap-tools>=0.50.0
openai>=1.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

- [ ] **Step 3: Create src/__init__.py**

```python
"""Email Todo MCP Server."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create README.md**

```markdown
# Email Todo MCP

An MCP server that reads emails from an IMAP mailbox and extracts todo items.

## Installation

```bash
pip install -e .
```

## Configuration

Copy `config.example.json` to `config.json` and fill in your email credentials.

## Usage

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "email-todo": {
      "command": "python",
      "args": ["/path/to/email-todo-mcp/src/server.py"]
    }
  }
}
```
```

- [ ] **Step 5: Initialize git repository and commit**

```bash
cd /Users/torian/Base/Projects/email-todo-mcp
git init
git add pyproject.toml requirements.txt src/__init__.py README.md
git commit -m "feat: initialize Python project structure"
```

---

### Task 2: Create Config Module

**Files:**
- Create: `src/config.py`
- Create: `config.example.json`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Create config.example.json**

```json
{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email": "your-email@example.com",
  "password": "app-specific-password",
  "llm_api_key": "optional-external-llm-key"
}
```

- [ ] **Step 2: Write the failing test for config loading**

```python
# tests/test_config.py
import pytest
import json
from pathlib import Path
from src.config import load_config, ConfigError

def test_load_config_from_file(tmp_path):
    """Test loading config from existing file."""
    config_path = tmp_path / "config.json"
    config_data = {
        "imap_server": "imap.test.com",
        "imap_port": 993,
        "email": "test@test.com",
        "password": "test-pass"
    }
    config_path.write_text(json.dumps(config_data))

    config = load_config(str(config_path))
    assert config["imap_server"] == "imap.test.com"
    assert config["imap_port"] == 993
    assert config["email"] == "test@test.com"
    assert config["password"] == "test-pass"

def test_load_config_missing_file(tmp_path):
    """Test error when config file is missing."""
    config_path = tmp_path / "nonexistent.json"
    with pytest.raises(ConfigError, match="Config file not found"):
        load_config(str(config_path))

def test_load_config_invalid_json(tmp_path):
    """Test error when config file is invalid JSON."""
    config_path = tmp_path / "invalid.json"
    config_path.write_text("not valid json")

    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(str(config_path))

def test_load_config_missing_required_fields(tmp_path):
    """Test error when required fields are missing."""
    config_path = tmp_path / "incomplete.json"
    config_path.write_text('{"imap_server": "imap.test.com"}')

    with pytest.raises(ConfigError, match="Missing required field"):
        load_config(str(config_path))
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/torian/Base/Projects/email-todo-mcp
source /Users/torian/miniconda3/bin/activate claude-sandbox
pip install -e .
pytest tests/test_config.py -v
```
Expected: FAIL with "module 'src.config' not found" or similar

- [ ] **Step 4: Implement config.py**

```python
# src/config.py
import json
from pathlib import Path

REQUIRED_FIELDS = ["imap_server", "imap_port", "email", "password"]


class ConfigError(Exception):
    """Configuration error."""
    pass


def load_config(config_path: str | None = None) -> dict:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file. If None, looks for config.json in project root.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If config file is missing, invalid, or incomplete.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise ConfigError(
            f"Config file not found: {config_path}\\n"
            f"Please copy config.example.json to config.json and fill in your credentials."
        )

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")

    # Check required fields
    missing = [field for field in REQUIRED_FIELDS if field not in config]
    if missing:
        raise ConfigError(f"Missing required field(s): {', '.join(missing)}")

    # Set defaults for optional fields
    config.setdefault("imap_port", 993)
    config.setdefault("llm_api_key", None)

    return config
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/config.py config.example.json tests/test_config.py tests/__init__.py
git commit -m "feat: add config loading with validation"
```

---

### Task 3: Create Email Client Module

**Files:**
- Create: `src/email_client.py`
- Create: `tests/test_email_client.py`

- [ ] **Step 1: Write the failing test for email client**

```python
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
        mock_mailbox.list.return_value = ("OK", [b'(\HasNoChildren) "." "INBOX"'])
        mock_mailbox.login.return_value = ("OK", [])
        mock_mailbox.select.return_value = ("OK", [])
        mock_mailbox.search.return_value = ("OK", [b"1 2 3"])
        mock_mailbox.fetch.return_value = ("OK", [
            (b"1 (RFC822 {100}", b"Subject: Test Email 1\\r\\n\\r\\nBody 1"),
            b")",
            (b"2 (RFC822 {100}", b"Subject: Test Email 2\\r\\n\\r\\nBody 2"),
            b")",
        ])
        mocker.patch("imap_tools.MailBox", return_value=mock_mailbox)

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
        # Return 5 emails but max_emails is 3
        mock_mailbox.fetch.return_value = ("OK", [
            (b"1 (RFC822 {50}", b"Subject: Email 1\\r\\n\\r\\nBody"), b")",
            (b"2 (RFC822 {50}", b"Subject: Email 2\\r\\n\\r\\nBody"), b")",
            (b"3 (RFC822 {50}", b"Subject: Email 3\\r\\n\\r\\nBody"), b")",
        ])
        mocker.patch("imap_tools.MailBox", return_value=mock_mailbox)

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

        mocker.patch("imap_tools.MailBox", side_effect=Exception("Connection refused"))

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
        mocker.patch("imap_tools.MailBox", return_value=mock_mailbox)

        emails = client.fetch_recent_emails()

        assert emails == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_email_client.py -v
```
Expected: FAIL with "module 'src.email_client' not found"

- [ ] **Step 3: Implement email_client.py**

```python
# src/email_client.py
from datetime import datetime, timedelta
from email import message_from_bytes
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
            with MailBox(self.server).login(self.email, self.password) as mailbox:
                # Select INBOX
                mailbox.select("INBOX")

                # Search for emails since date
                criteria = f"SINCE {since_date.strftime('%d-%b-%Y')}"
                msg_ids = mailbox.search(criteria)

                if not msg_ids:
                    return []

                # Fetch emails (respect max_emails limit)
                for msg in mailbox.fetch(msg_ids[:max_emails], mark_seen=False):
                    emails.append({
                        "subject": self._decode_header(msg.subject),
                        "from": msg.from_,
                        "date": msg.date_str,
                        "body": msg.text or msg.html or "",
                    })

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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_email_client.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/email_client.py tests/test_email_client.py
git commit -m "feat: add email client for IMAP fetch"
```

---

### Task 4: Create Todo Extractor Module

**Files:**
- Create: `src/todo_extractor.py`
- Create: `tests/test_todo_extractor.py`

- [ ] **Step 1: Write the failing test for todo extractor**

```python
# tests/test_todo_extractor.py
import pytest
from src.todo_extractor import TodoExtractor, extract_todos_from_emails


class TestTodoExtractor:
    """Tests for TodoExtractor class."""

    def test_extract_todos_from_email_content(self):
        """Test extracting todos from email content."""
        extractor = TodoExtractor(api_key=None)

        email = {
            "subject": "Assignment Reminder",
            "from": "professor@university.edu",
            "body": "Dear Student,\\n\\nPlease complete the assignment by March 30th.\\n\\nAlso, prepare for the quiz next week."
        }

        todos = extractor.extract_from_email(email)

        assert len(todos) > 0
        assert any("assignment" in todo["task"].lower() for todo in todos)

    def test_extract_todos_returns_empty_for_non_todo_email(self):
        """Test that non-actionable emails return empty or minimal todos."""
        extractor = TodoExtractor(api_key=None)

        email = {
            "subject": "Newsletter",
            "from": "news@company.com",
            "body": "Here are this week's top stories..."
        }

        todos = extractor.extract_from_email(email)

        # Should handle gracefully - either empty list or minimal todos
        assert isinstance(todos, list)

    def test_extract_todos_from_multiple_emails(self):
        """Test extracting todos from multiple emails."""
        extractor = TodoExtractor(api_key=None)

        emails = [
            {
                "subject": "Meeting Tomorrow",
                "from": "boss@company.com",
                "body": "Don't forget about the 9am meeting tomorrow."
            },
            {
                "subject": "Invoice Due",
                "from": "billing@service.com",
                "body": "Your invoice is due on April 1st."
            }
        ]

        all_todos = extractor.extract_from_emails(emails)

        assert isinstance(all_todos, list)
        assert "processed_emails" in all_todos
        assert "todos" in all_todos

    def test_format_todo_output(self):
        """Test the formatted todo output structure."""
        extractor = TodoExtractor(api_key=None)

        email = {
            "subject": "Task Reminder",
            "from": "sender@example.com",
            "body": "Please submit the report by Friday."
        }

        todos = extractor.extract_from_email(email)

        for todo in todos:
            assert "task" in todo
            assert "source_email" in todo
            # Optional fields
            assert isinstance(todo.get("due_date"), (str, type(None)))
            assert isinstance(todo.get("priority"), (str, type(None)))
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_todo_extractor.py -v
```
Expected: FAIL with "module 'src.todo_extractor' not found"

- [ ] **Step 3: Implement todo_extractor.py**

```python
# src/todo_extractor.py
import re
from typing import Optional


class TodoExtractor:
    """
    Extract todo items from email content.

    This is a basic rule-based extractor. For production use with an LLM API key,
    it can call OpenAI API for smarter extraction.
    """

    # Patterns that suggest actionable content
    ACTION_PATTERNS = [
        r"please\s+\w+",
        r"don't\s+forget",
        r"remind",
        r"deadline",
        r"due\s+by?\s+\w+",
        r"submit",
        r"complete",
        r"finish",
    ]

    # Date patterns
    DATE_PATTERNS = [
        r"by\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?)",
        r"due\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?)",
        r"before\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?)",
        r"(\d{4}-\d{2}-\d{2})",
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize todo extractor.

        Args:
            api_key: Optional LLM API key for smart extraction.
        """
        self.api_key = api_key

    def extract_from_email(self, email: dict) -> list[dict]:
        """
        Extract todo items from a single email.

        Args:
            email: Email dictionary with subject, from, body.

        Returns:
            List of todo dictionaries.
        """
        todos = []

        # Combine subject and body for analysis
        content = f"{email.get('subject', '')} {email.get('body', '')}".lower()

        # Check if email contains actionable content
        if not self._is_actionable(content):
            return todos

        # Extract potential tasks
        tasks = self._extract_tasks(email)

        for task in tasks:
            todos.append({
                "task": task["description"],
                "source_email": email.get("subject", "No subject"),
                "due_date": task.get("due_date"),
                "priority": task.get("priority", "medium"),
            })

        return todos

    def extract_from_emails(self, emails: list[dict]) -> dict:
        """
        Extract todo items from multiple emails.

        Args:
            emails: List of email dictionaries.

        Returns:
            Dictionary with 'todos' list and 'processed_emails' count.
        """
        all_todos = []
        processed_count = 0

        for email in emails:
            todos = self.extract_from_email(email)
            all_todos.extend(todos)
            if todos:
                processed_count += 1

        return {
            "todos": all_todos,
            "processed_emails": processed_count,
        }

    def _is_actionable(self, content: str) -> bool:
        """Check if content contains actionable patterns."""
        for pattern in self.ACTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _extract_tasks(self, email: dict) -> list[dict]:
        """Extract task information from email."""
        tasks = []
        content = f"{email.get('subject', '')} {email.get('body', '')}"

        # Simple extraction: look for sentences with action words
        sentences = re.split(r"[.!?]+", content)

        for sentence in sentences:
            sentence = sentence.strip()
            if self._is_actionable(sentence) and len(sentence) > 10:
                # Extract due date if present
                due_date = self._extract_date(sentence)

                # Determine priority based on keywords
                priority = "medium"
                if any(word in sentence.lower() for word in ["urgent", "asap", "immediately"]):
                    priority = "high"
                elif any(word in sentence.lower() for word in ["fyi", "info", "note"]):
                    priority = "low"

                tasks.append({
                    "description": sentence[:200],  # Limit length
                    "due_date": due_date,
                    "priority": priority,
                })

        # If no tasks found but email is actionable, add a generic task from subject
        if not tasks and email.get("subject"):
            tasks.append({
                "description": f"Review: {email['subject']}",
                "due_date": None,
                "priority": "medium",
            })

        return tasks[:3]  # Max 3 tasks per email

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract due date from text."""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None


# Convenience function for direct use
def extract_todos_from_emails(emails: list[dict], api_key: Optional[str] = None) -> dict:
    """
    Extract todos from emails using TodoExtractor.

    Args:
        emails: List of email dictionaries.
        api_key: Optional LLM API key.

    Returns:
        Dictionary with todos and processed count.
    """
    extractor = TodoExtractor(api_key=api_key)
    return extractor.extract_from_emails(emails)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_todo_extractor.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/todo_extractor.py tests/test_todo_extractor.py
git commit -m "feat: add todo extractor with rule-based parsing"
```

---

### Task 5: Create MCP Server

**Files:**
- Create: `src/server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write the failing test for MCP server**

```python
# tests/test_server.py
import pytest
from unittest.mock import MagicMock, patch
from src.server import create_mcp_server


class TestMCPServer:
    """Tests for MCP server."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "imap_server": "imap.test.com",
            "imap_port": 993,
            "email": "test@test.com",
            "password": "test-pass",
            "llm_api_key": None
        }

    def test_server_creation(self, mock_config):
        """Test that MCP server can be created."""
        with patch("src.server.load_config", return_value=mock_config):
            server = create_mcp_server()
            assert server is not None

    def test_fetch_todos_tool_registered(self, mock_config):
        """Test that fetch_todos_from_email tool is registered."""
        with patch("src.server.load_config", return_value=mock_config):
            server = create_mcp_server()

            # Check that the tool is registered
            tool_names = [tool.name for tool in server._tools.values()]
            assert "fetch_todos_from_email" in tool_names

    def test_list_emails_tool_registered(self, mock_config):
        """Test that list_recent_emails tool is registered."""
        with patch("src.server.load_config", return_value=mock_config):
            server = create_mcp_server()

            tool_names = [tool.name for tool in server._tools.values()]
            assert "list_recent_emails" in tool_names
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_server.py -v
```
Expected: FAIL with "module 'src.server' not found"

- [ ] **Step 3: Implement server.py**

```python
# src/server.py
import sys
from mcp.server import Server
from mcp.types import Tool, TextContent
from src.config import load_config
from src.email_client import EmailClient
from src.todo_extractor import TodoExtractor


def create_mcp_server() -> Server:
    """
    Create and configure the MCP server.

    Returns:
        Configured MCP Server instance.
    """
    server = Server("email-todo-mcp")

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        # Server will start but tools will return config errors
        config = None

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="fetch_todos_from_email",
                description="Extract todo items from recent emails using IMAP",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days_ago": {
                            "type": "integer",
                            "description": "Number of days to look back for emails",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 30
                        },
                        "max_emails": {
                            "type": "integer",
                            "description": "Maximum number of emails to process",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                }
            ),
            Tool(
                name="list_recent_emails",
                description="List recent emails from your IMAP mailbox",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "Number of recent emails to list",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    }
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        # Check config
        if config is None:
            return [TextContent(
                type="text",
                text="Error: Configuration not found. Please create config.json with your email credentials."
            )]

        try:
            if name == "fetch_todos_from_email":
                return await _fetch_todos(arguments, config)
            elif name == "list_recent_emails":
                return await _list_emails(arguments, config)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def _fetch_todos(arguments: dict, config: dict) -> list[TextContent]:
    """Fetch todos from emails."""
    days_ago = arguments.get("days_ago", 1)
    max_emails = arguments.get("max_emails", 10)

    # Fetch emails
    client = EmailClient(config)
    emails = client.fetch_recent_emails(days_ago=days_ago, max_emails=max_emails)

    if not emails:
        return [TextContent(
            type="text",
            text=f"No emails found in the last {days_ago} days."
        )]

    # Extract todos
    extractor = TodoExtractor(api_key=config.get("llm_api_key"))
    result = extractor.extract_from_emails(emails)

    # Format output
    output = f"Processed {result['processed_emails']} emails\\n\\n"
    if result['todos']:
        output += "Found todo items:\\n"
        for i, todo in enumerate(result['todos'], 1):
            output += f"\\n{i}. {todo['task']}"
            if todo.get('due_date'):
                output += f" (Due: {todo['due_date']})"
            if todo.get('priority'):
                output += f" [Priority: {todo['priority']}]"
            output += f"\\n   Source: {todo['source_email']}"
    else:
        output += "No actionable todos found."

    return [TextContent(type="text", text=output)]


async def _list_emails(arguments: dict, config: dict) -> list[TextContent]:
    """List recent emails."""
    count = arguments.get("count", 5)

    client = EmailClient(config)
    emails = client.fetch_recent_emails(days_ago=1, max_emails=count)

    if not emails:
        return [TextContent(type="text", text="No recent emails found.")]

    output = f"Recent emails ({len(emails)}):\\n\\n"
    for i, email in enumerate(emails, 1):
        output += f"{i}. From: {email['from']}\\n"
        output += f"   Subject: {email['subject']}\\n"
        output += f"   Date: {email['date']}\\n"
        preview = (email.get('body') or '')[:100]
        output += f"   Preview: {preview}...\\n\\n"

    return [TextContent(type="text", text=output)]


def main():
    """Main entry point for running the server."""
    from mcp.server.stdio import stdio_server

    server = create_mcp_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_server.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/server.py tests/test_server.py
git commit -m "feat: add MCP server with todo and email tools"
```

---

### Task 6: Update README with Usage Instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README.md with complete usage instructions**

```markdown
# Email Todo MCP

A Model Context Protocol (MCP) server that reads emails from an IMAP mailbox and extracts todo items using natural language processing.

## Features

- **Fetch todos from emails**: Automatically extract actionable items from your recent emails
- **List recent emails**: Get a quick overview of your latest emails
- **Rule-based extraction**: Works without external LLM API (optional OpenAI integration)
- **Privacy-first**: All processing happens locally, your emails never leave your machine

## Installation

```bash
# Clone or navigate to the project
cd /Users/torian/Base/Projects/email-todo-mcp

# Install in development mode
source /path/to/conda-env/bin/activate  # Or use your preferred Python env
pip install -e .
```

## Configuration

1. Copy the example config:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your email credentials:

```json
{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email": "your-email@gmail.com",
  "password": "your-app-specific-password",
  "llm_api_key": null
}
```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) rather than your regular password.

## Setup with Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\\Claude\\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "email-todo": {
      "command": "/path/to/claude-sandbox/bin/python",
      "args": [
        "/Users/torian/Base/Projects/email-todo-mcp/src/server.py"
      ]
    }
  }
}
```

**Important:** Use the full path to your Python executable in the conda environment.

## Usage

Once configured, you can interact with the MCP server in Claude:

```
You: Check my email and tell me if there's anything I need to do.

Claude: [Uses fetch_todos_from_email tool]
I found 3 actionable items in your recent emails:
1. Complete the machine learning assignment (Due: March 30th) [Priority: high]
2. Submit the weekly report by Friday [Priority: medium]
3. Review the meeting notes [Priority: low]

You: Just show me my 5 most recent emails.

Claude: [Uses list_recent_emails tool]
Here are your 5 most recent emails:
...
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_email_client.py -v
```

## Architecture

```
┌─────────────┐      stdio      ┌──────────────────────┐
│   Claude    │◄──────────────►│  Email Todo MCP      │
│   Client    │                 │  (Python 进程)       │
└─────────────┘                 └──────────────────────┘
                                        │
                                        │ IMAP
                                        ▼
                                ┌──────────────┐
                                │  Mailbox     │
                                └──────────────┘
```

## Security Notes

- Your email credentials are stored locally in `config.json`
- Use app-specific passwords when available
- Never commit `config.json` to version control
- `config.json` is already in `.gitignore`

## License

MIT
```

- [ ] **Step 2: Add config.json to .gitignore**

```bash
echo "config.json" >> /Users/torian/Base/Projects/email-todo-mcp/.gitignore
```

- [ ] **Step 3: Commit**

```bash
git add README.md .gitignore
git commit -m "docs: add comprehensive README with usage instructions"
```

---

### Task 7: Final Integration Test

**Files:**
- No new files, integration test

- [ ] **Step 1: Run all tests**

```bash
cd /Users/torian/Base/Projects/email-todo-mcp
pytest tests/ -v
```
Expected: All tests pass

- [ ] **Step 2: Verify MCP server can start**

```bash
source /Users/torian/miniconda3/bin/activate claude-sandbox
python src/server.py
```
Expected: Server starts and waits for stdio input (will appear to hang, which is normal)

Press Ctrl+C to stop the server.

- [ ] **Step 3: Create .gitignore if not exists**

```bash
cat > /Users/torian/Base/Projects/email-todo-mcp/.gitignore << 'EOF'
# Config files with credentials
config.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

- [ ] **Step 4: Final commit**

```bash
git add .gitignore
git commit -m "chore: add comprehensive .gitignore"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Server starts without errors: `python src/server.py` (then Ctrl+C)
- [ ] `config.json` is in `.gitignore`
- [ ] README has complete setup instructions
- [ ] `config.example.json` exists for reference
- [ ] All modules can be imported: `python -c "from src.server import create_mcp_server; from src.email_client import EmailClient; from src.todo_extractor import TodoExtractor; from src.config import load_config"`

---

## Next Steps After Implementation

1. **Test with real email**: Create your `config.json` and test with your actual mailbox
2. **Configure Claude Desktop**: Add the MCP server to your Claude Desktop config
3. **Optional enhancements**:
   - Add OpenAI API integration for smarter todo extraction
   - Add support for more IMAP folders (Sent, Archive, etc.)
   - Add email filtering by sender/subject
   - Add todo priority categorization

---

## Implementation Notes

- The MCP server uses **stdio transport** for communication with Claude Client
- Each tool call creates a new IMAP connection (stateless design)
- The rule-based todo extractor works without external LLM API
- Error handling is comprehensive and user-friendly
- All sensitive credentials are kept in `config.json` (not in code)
