# src/todo_extractor.py
import re
import json
from typing import Optional


class TodoExtractor:
    """
    Extract todo items from email content.

    Supports both rule-based extraction and LLM-powered extraction using APIs.
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

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize todo extractor.

        Args:
            api_key: Optional LLM API key for smart extraction.
            api_base: Optional API base URL (e.g., "https://api.siliconflow.cn/v1").
            model: Optional model name (e.g., "deepseek-ai/DeepSeek-R1").
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

    def extract_from_email(self, email: dict) -> list[dict]:
        """
        Extract todo items from a single email.

        Args:
            email: Email dictionary with subject, from, body.

        Returns:
            List of todo dictionaries.
        """
        # Use LLM extraction if API key is available
        if self.api_key and self.api_base and self.model:
            return self._extract_with_llm(email)

        # Fall back to rule-based extraction
        todos = []
        content = f"{email.get('subject', '')} {email.get('body', '')}".lower()

        if not self._is_actionable(content):
            return todos

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

    def _extract_with_llm(self, email: dict) -> list[dict]:
        """
        Extract todo items using LLM API.

        Args:
            email: Email dictionary with subject, from, body.

        Returns:
            List of todo dictionaries.
        """
        import requests

        subject = email.get("subject", "")
        body = email.get("body", "")
        sender = email.get("from", "")

        prompt = f"""请分析以下邮件内容，提取出需要采取行动的待办事项（Todo items）。

邮件信息：
- 发件人: {sender}
- 主题: {subject}
- 正文: {body}

请以JSON格式返回待办事项列表，每个待办事项包含：
- task: 待办事项描述（简洁明了）
- due_date: 截止日期（如果邮件中提到，否则为null）
- priority: 优先级（high/medium/low，根据邮件内容判断）

返回格式示例：
[
  {{"task": "完成作业", "due_date": "3月30日", "priority": "high"}},
  {{"task": "准备会议材料", "due_date": null, "priority": "medium"}}
]

如果邮件中没有需要采取行动的内容，请返回空数组 []。

只返回JSON数组，不要包含其他解释文字。"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse the JSON response
            # Handle potential markdown code blocks
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            todos_data = json.loads(content)

            # Convert to our format
            todos = []
            for item in todos_data:
                todos.append({
                    "task": item.get("task", ""),
                    "source_email": subject or "No subject",
                    "due_date": item.get("due_date"),
                    "priority": item.get("priority", "medium"),
                })

            return todos

        except Exception as e:
            # Fall back to rule-based extraction on error
            print(f"Warning: LLM extraction failed ({e}), falling back to rule-based extraction")
            todos = []
            content = f"{subject} {body}".lower()

            if not self._is_actionable(content):
                return todos

            tasks = self._extract_tasks(email)
            for task in tasks:
                todos.append({
                    "task": task["description"],
                    "source_email": subject or "No subject",
                    "due_date": task.get("due_date"),
                    "priority": task.get("priority", "medium"),
                })

            return todos


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
