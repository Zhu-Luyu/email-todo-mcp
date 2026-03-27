#!/usr/bin/env python3
"""Test script for email-todo MCP server"""

import sys
sys.path.insert(0, '/Users/torian/Base/Projects/email-todo-mcp/src')

from config import load_config
from email_client import EmailClient
from todo_extractor import TodoExtractor

# Load config
print("Loading config...")
config = load_config()
print(f"✓ Config loaded for: {config['email']}")
print(f"  IMAP Server: {config['imap_server']}:{config['imap_port']}")
print(f"  LLM Model: {config.get('llm_model', 'None (rule-based only)')}")

# Test email client
print("\nFetching recent emails...")
client = EmailClient(config)
emails = client.fetch_recent_emails(days_ago=1, max_emails=3)
print(f"✓ Found {len(emails)} recent emails")

# Show email previews
for i, email in enumerate(emails, 1):
    print(f"\n{i}. From: {email['from']}")
    print(f"   Subject: {email['subject']}")

# Test todo extraction
print("\nExtracting todos from emails...")
extractor = TodoExtractor(
    api_key=config.get("llm_api_key"),
    api_base=config.get("llm_api_base"),
    model=config.get("llm_model")
)
result = extractor.extract_from_emails(emails)

print(f"✓ Processed {result['processed_emails']} emails with actionable content")

if result['todos']:
    print(f"\n📋 Found {len(result['todos'])} todo items:")
    for i, todo in enumerate(result['todos'], 1):
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get('priority', 'medium'), '⚪')
        print(f"\n{i}. {todo['task']}")
        if todo.get('due_date'):
            print(f"   📅 Due: {todo['due_date']}")
        print(f"   {priority_emoji} Priority: {todo.get('priority', 'medium')}")
        print(f"   📧 Source: {todo['source_email']}")
else:
    print("\n✓ No actionable todos found in recent emails")

print("\n✅ MCP server test completed successfully!")
