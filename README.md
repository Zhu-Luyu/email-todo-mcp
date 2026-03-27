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
