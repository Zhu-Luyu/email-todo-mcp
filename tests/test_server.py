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
