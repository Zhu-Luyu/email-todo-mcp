# Email Todo MCP

A Model Context Protocol (MCP) server that reads emails from an IMAP mailbox and intelligently extracts todo items, action items, and tasks from email content.

## Features

- **IMAP Email Integration**: Connects to any IMAP email server (Gmail, Outlook, Yahoo, etc.)
- **Intelligent Todo Extraction**: Uses Claude AI to extract and categorize action items from emails
- **Batch Processing**: Processes multiple emails efficiently
- **Full-text Search**: Search emails by sender, subject, date range, and content
- **Secure Authentication**: Supports app-specific passwords and OAuth tokens
- **Flexible Querying**: Filter emails by read/unread status, date ranges, and more
- **MCP Compliant**: Fully compatible with Claude Desktop and other MCP clients

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- An email account with IMAP access enabled

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/email-todo-mcp.git
cd email-todo-mcp
```

### Step 2: Create Virtual Environment

Using venv (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -e .
```

This will install the package in development mode along with all required dependencies:
- `mcp`: Model Context Protocol SDK
- `mcp-cli`: MCP command-line tools
- `pydantic`: Data validation
- `anthropic`: Claude AI integration

## Configuration

### Step 1: Create Configuration File

Copy the example configuration file:

```bash
cp config.example.json config.json
```

### Step 2: Edit Configuration

Edit `config.json` with your email credentials:

```json
{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email": "your-email@example.com",
  "password": "your-app-specific-password",
  "llm_api_key": "optional-external-llm-api-key"
}
```

### Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `imap_server` | string | Yes | IMAP server hostname |
| `imap_port` | integer | Yes | IMAP port (usually 993 for SSL) |
| `email` | string | Yes | Your email address |
| `password` | string | Yes | App-specific password or OAuth token |
| `llm_api_key` | string | Optional | External LLM API key (optional) |

### Email-Specific Setup

#### Gmail

1. Enable 2-Factor Authentication
2. Generate an App-Specific Password:
   - Go to Google Account > Security
   - Select "App passwords"
   - Generate a new password for "Mail"
3. Use the app password in `config.json`

#### Outlook/Office 365

1. IMAP server: `outlook.office365.com`
2. Port: `993`
3. Use your Microsoft account password or app password

#### Yahoo Mail

1. IMAP server: `imap.mail.yahoo.com`
2. Port: `993`
3. Generate an app password in Yahoo Account Security

### Security Note

**Never commit `config.json` to version control!** It contains sensitive credentials.

The `.gitignore` file is configured to exclude `config.json` by default.

## Setup with Claude Desktop

### macOS

1. Open Claude Desktop
2. Go to **Settings** > **Developer**
3. Edit the MCP servers configuration file:
   - Location: `~/Library/Application Support/Claude/claude_desktop_config.json`
4. Add the following configuration:

```json
{
  "mcpServers": {
    "email-todo": {
      "command": "/Users/torian/Base/Projects/email-todo-mcp/venv/bin/python",
      "args": ["/Users/torian/Base/Projects/email-todo-mcp/src/server.py"],
      "cwd": "/Users/torian/Base/Projects/email-todo-mcp"
    }
  }
}
```

### Windows

1. Open Claude Desktop
2. Go to **Settings** > **Developer**
3. Edit the MCP servers configuration file:
   - Location: `%APPDATA%\Claude\claude_desktop_config.json`
4. Add the following configuration:

```json
{
  "mcpServers": {
    "email-todo": {
      "command": "python",
      "args": ["C:\\path\\to\\email-todo-mcp\\src\\server.py"],
      "cwd": "C:\\path\\to\\email-todo-mcp",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\email-todo-mcp"
      }
    }
  }
}
```

5. Restart Claude Desktop

## Usage Examples

### Example 1: Check Recent Emails

**User**: "Check my recent emails and extract any todo items"

**Claude**: [Calls `list_emails` tool]
```
Found 5 recent emails. Let me check them for action items...

[Analyzes emails with `extract_todos` tool]
```

**Result**:
- "Meeting with John tomorrow at 2pm" (from email)
- "Submit quarterly report by Friday" (from email)
- "Review the attached proposal" (from email)

### Example 2: Search Specific Emails

**User**: "Find emails from john@example.com about the project"

**Claude**: [Calls `search_emails` with sender filter]
```
Found 3 emails from john@example.com matching "project" in the subject.
```

### Example 3: Process Unread Emails

**User**: "Go through my unread emails and create a todo list"

**Claude**:
1. [Calls `list_emails` with `unread_only=true`]
2. [Calls `extract_todos` on each unread email]
3. Organizes results by priority and category

### Example 4: Date-Range Search

**User**: "What action items came in last week?"

**Claude**: [Calls `search_emails` with date range]
```
Searching emails from 2024-01-15 to 2024-01-22...

Found 12 emails. Extracting todos...
```

## Available Tools

The Email Todo MCP server provides the following tools:

### `list_emails`
List recent emails from your inbox.

**Parameters:**
- `limit` (integer): Maximum number of emails to retrieve (default: 10)
- `unread_only` (boolean): Only retrieve unread emails (default: false)

**Returns:**
- List of emails with subject, sender, date, and body preview

### `search_emails`
Search emails by various criteria.

**Parameters:**
- `query` (string): Search query for subject/body
- `sender` (string, optional): Filter by sender email
- `since_date` (string, optional): ISO date string (e.g., "2024-01-01")
- `until_date` (string, optional): ISO date string (e.g., "2024-01-31")
- `limit` (integer): Maximum results (default: 10)

**Returns:**
- Filtered list of emails matching criteria

### `extract_todos`
Extract todo items from email content.

**Parameters:**
- `email_body` (string): Full email body text
- `sender` (string, optional): Sender email for context
- `subject` (string, optional): Email subject for context

**Returns:**
- Structured list of extracted todos with:
  - Description
  - Priority (high/medium/low)
  - Category (work/personal/finance/etc.)
  - Due date (if mentioned)

## Development

### Project Structure

```
email-todo-mcp/
├── src/
│   ├── server.py          # MCP server implementation
│   ├── email_client.py    # IMAP email client
│   ├── todo_extractor.py  # Todo extraction logic
│   └── config.py          # Configuration management
├── tests/
│   ├── test_server.py
│   ├── test_email_client.py
│   ├── test_todo_extractor.py
│   └── test_config.py
├── config.example.json    # Example configuration
├── README.md              # This file
└── pyproject.toml         # Package configuration
```

### Architecture Diagram

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────────────────────┐
│       MCP Server (server.py)     │
│  - Tool registration             │
│  - Request handling              │
│  - Response formatting           │
└────────┬────────────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌───────────┐
│ EmailClient │  │ TodoExtractor│  │  Config   │
│  (IMAP)     │  │  (Claude AI) │  │ Manager   │
└─────────────┘  └──────────────┘  └───────────┘
     │
     ▼
┌─────────────────┐
│  IMAP Server    │
│  (Gmail/Outlook)│
└─────────────────┘
```

### Running Tests

Run all tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_email_client.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Adding New Features

1. **New Email Providers**: Extend `EmailClient` class
2. **Custom Todo Formats**: Modify `TodoExtractor` prompts
3. **Additional Filters**: Add parameters to `search_emails`
4. **New Tools**: Register in `create_mcp_server()`

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public functions
- Keep functions focused and modular

## Troubleshooting

### Issue: "Authentication failed"

**Solution**:
- Verify your email and password are correct
- For Gmail, ensure you're using an app-specific password
- Check that IMAP is enabled in your email settings

### Issue: "Connection timeout"

**Solution**:
- Check your internet connection
- Verify the IMAP server and port are correct
- Some networks block IMAP ports (contact your network admin)

### Issue: "No emails found"

**Solution**:
- Verify your inbox has emails
- Check that you're looking in the right folder (INBOX)
- Try increasing the `limit` parameter

### Issue: "Claude Desktop can't connect"

**Solution**:
- Verify the path to `server.py` is correct in the config
- Ensure the virtual environment Python is being used
- Check Claude Desktop logs for error messages
- Restart Claude Desktop after updating the config

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- Powered by [Anthropic Claude](https://www.anthropic.com/claude)
