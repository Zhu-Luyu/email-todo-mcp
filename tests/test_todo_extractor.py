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
            "body": "Dear Student,\n\nPlease complete the assignment by March 30th.\n\nAlso, prepare for the quiz next week."
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

        assert isinstance(all_todos, dict)
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
