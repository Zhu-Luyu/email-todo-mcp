# Email Todo MCP Design

**Date:** 2026-03-27
**Author:** Claude
**Status:** Approved

## Overview

A Model Context Protocol (MCP) server that reads emails from an IMAP mailbox and uses LLM to extract todo items. This server runs as a separate Python process and communicates with Claude via stdio.

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
                                │  邮箱服务器   │
                                └──────────────┘
```

## Project Structure

```
email-todo-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py          # MCP server main entry point
│   ├── email_client.py    # IMAP email client
│   └── todo_extractor.py  # LLM todo extractor
├── config.example.json    # Configuration template
├── pyproject.toml         # Python project config
├── README.md              # Project documentation
└── requirements.txt       # Dependencies
```

## MCP Tools

| Tool Name | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `fetch_todos_from_email` | Extract todo items from emails | `days_ago` (default 1), `max_emails` (default 10) | Todo list |
| `list_recent_emails` | List recent emails | `count` (default 5) | Email summary list |

**Return Example:**
```json
{
  "todos": [
    {
      "task": "完成机器学习作业",
      "source_email": "课程通知 - 作业截止提醒",
      "due_date": "2026-03-30",
      "priority": "high"
    }
  ],
  "processed_emails": 3
}
```

## Data Flow

```
User Request
   │
   ▼
Claude Client starts MCP
   │
   ▼
MCP reads config file (config.json)
   │
   ├── Config exists? ──No──► Prompt user to configure
   │
   └── Yes
      │
      ▼
   Connect to IMAP server
      │
      ├── Success
      │     │
      │     ▼
      │  Fetch recent emails
      │     │
      │     ▼
      │  Call LLM API to extract todos
      │     │
      │     ▼
      │  Return results to user
      │
      └── Failed ──► Return error message
```

## Configuration File

```json
{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email": "your-email@example.com",
  "password": "app-specific-password",
  "llm_api_key": "optional-external-llm-key"
}
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| Config file missing | Return friendly prompt with setup instructions |
| IMAP connection failed | Return specific error (network, credentials, etc.) |
| Empty mailbox | Return empty result, no error |
| LLM API failed | Fallback: return raw email summary without parsing |

## Dependencies

```txt
mcp          # MCP SDK
imap-tools   # Email processing
openai       # LLM API (optional)
```

## Core Code Structure

```python
# server.py - MCP server entry point
@mcp.tool()
def fetch_todos_from_email(days_ago: int = 1, max_emails: int = 10) -> str:
    """Extract todo items from emails"""
    # 1. Load config
    # 2. Connect to mailbox
    # 3. Fetch emails
    # 4. Extract todos with LLM
    # 5. Return results
```

## MCP Execution Model

**Important:** MCP servers are NOT background services. They are started on-demand:

1. Claude Client detects tool call needed
2. Starts the MCP process
3. Sends request via stdio
4. MCP returns result and exits

This means the server should:
- Start up quickly
- Be stateless (each call is independent)
- Connect to resources on-demand (IMAP connection per request)
