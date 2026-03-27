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

    # Define tools for testing purposes
    server._tools = {
        "fetch_todos_from_email": Tool(
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
        "list_recent_emails": Tool(
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
    }

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return list(server._tools.values())

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
    output = f"Processed {result['processed_emails']} emails\n\n"
    if result['todos']:
        output += "Found todo items:\n"
        for i, todo in enumerate(result['todos'], 1):
            output += f"\n{i}. {todo['task']}"
            if todo.get('due_date'):
                output += f" (Due: {todo['due_date']})"
            if todo.get('priority'):
                output += f" [Priority: {todo['priority']}]"
            output += f"\n   Source: {todo['source_email']}"
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

    output = f"Recent emails ({len(emails)}):\n\n"
    for i, email in enumerate(emails, 1):
        output += f"{i}. From: {email['from']}\n"
        output += f"   Subject: {email['subject']}\n"
        output += f"   Date: {email['date']}\n"
        preview = (email.get('body') or '')[:100]
        output += f"   Preview: {preview}...\n\n"

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
