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
