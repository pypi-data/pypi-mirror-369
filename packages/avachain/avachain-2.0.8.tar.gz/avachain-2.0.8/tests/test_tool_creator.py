"""
Unit tests for tool_creator module.

This module tests the tool creation and conversion utilities.
"""

import json
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import BaseModel, Field

from avachain import BaseTool
from avachain.tool_creator import (
    convert_tool_to_json,
    makePluginServerRequest,
    map_type_to_json,
)


class TestToolArgs(BaseModel):
    """Test tool arguments schema."""

    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Maximum results")
    category: str = Field(default="general", description="Search category")


class TestTool(BaseTool):
    """Test tool for conversion testing."""

    name: str = "test_search_tool"
    description: str = "A tool for searching information"
    args_schema: Optional[type] = TestToolArgs

    def _run(self, query: str, limit: int = 10, category: str = "general") -> str:
        """Execute the test tool."""
        return f"Search results for '{query}' (limit: {limit}, category: {category})"


class TestMapTypeToJson:
    """Test cases for map_type_to_json function."""

    def test_basic_types(self):
        """Test mapping of basic Python types."""
        assert map_type_to_json(int) == "number"
        assert map_type_to_json(float) == "number"
        assert map_type_to_json(str) == "string"
        assert map_type_to_json(bool) == "boolean"

    def test_unknown_types(self):
        """Test mapping of unknown types."""
        assert map_type_to_json(list) == "<class 'list'>"
        assert map_type_to_json(dict) == "<class 'dict'>"
        assert map_type_to_json(tuple) == "<class 'tuple'>"


class TestConvertToolToJson:
    """Test cases for convert_tool_to_json function."""

    @patch("avachain.tool_creator.inspect.getsource")
    @patch("avachain.tool_creator.print")
    def test_convert_tool_basic(self, mock_print, mock_getsource):
        """Test basic tool conversion to JSON."""
        mock_getsource.return_value = "def _run(self): return 'test'"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test_tool_v1",
            human_description="A test tool for searching",
            public_name="Test Search Tool",
        )

        # Check basic structure
        assert result["title"] == "test_tool_v1"
        assert result["name"] == "Test Search Tool"
        assert result["human_description"] == "A test tool for searching"
        assert result["ai_description"] == "A tool for searching information"

        # Check OS support
        assert len(result["os"]) == 1

        # Check parameters structure
        assert "parameters" in result
        assert "tool_extras" in result["parameters"]
        assert "tool_parameters" in result["parameters"]

        # Check tool extras
        extras = result["parameters"]["tool_extras"]
        assert extras["name"] == "test_search_tool"
        assert extras["isDirect"] is False

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_with_parameters(self, mock_getsource):
        """Test tool conversion with parameters."""
        mock_getsource.return_value = "def _run(self, query, limit=10): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test_tool",
            human_description="Test tool",
            public_name="Test Tool",
        )

        # Check that parameters were extracted
        tool_params = result["parameters"]["tool_parameters"]
        assert "query" in tool_params
        assert "limit" in tool_params
        assert "category" in tool_params

        # Check parameter types
        assert tool_params["query"]["type"] == "string"
        assert tool_params["limit"]["type"] == "number"
        assert tool_params["category"]["type"] == "string"

        # Check descriptions
        assert tool_params["query"]["description"] == "Search query"
        assert tool_params["limit"]["description"] == "Maximum results"
        assert tool_params["category"]["description"] == "Search category"

        # Check default values
        assert tool_params["limit"]["default"] == 10
        assert tool_params["category"]["default"] == "general"

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_os_support_validation(self, mock_getsource):
        """Test OS support validation."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()

        # Should raise error when no OS is supported
        with pytest.raises(ValueError, match="at least one of 'android', 'windows'"):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                supports_android=False,
                supports_windows=False,
            )

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_android_support(self, mock_getsource):
        """Test tool conversion with Android support."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            supports_android=True,
            supports_windows=False,
        )

        assert result["os"] == ["android"]

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_windows_support(self, mock_getsource):
        """Test tool conversion with Windows support."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            supports_android=False,
            supports_windows=True,
        )

        # Should contain the current OS name
        import os

        assert os.name in result["os"]

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_all_options(self, mock_getsource):
        """Test tool conversion with all optional parameters."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        tool.return_direct = True  # Set return_direct for testing

        result = convert_tool_to_json(
            tool=tool,
            tool_id="advanced_tool",
            human_description="Advanced test tool",
            public_name="Advanced Tool",
            logo="https://example.com/logo.png",
            isAnonymous=True,
            authentication_required=True,
            connection_url="https://api.example.com",
            isAuthenticated=True,
            isPublic=False,
            isMain=True,
            tags=["search", "utility"],
            supports_android=True,
            supports_windows=True,
        )

        # Check all options
        assert result["logo"] == "https://example.com/logo.png"
        assert result["isAnonymous"] is True
        assert result["authentication_required"] is True
        assert result["connection_url"] == "https://api.example.com"
        assert result["isAuthenticated"] is True
        assert result["isPublic"] is False
        assert result["tags"] == ["search", "utility"]
        assert result["parameters"]["tool_extras"]["isMain"] is True
        assert result["parameters"]["tool_extras"]["isDirect"] is True


class TestMakePluginServerRequest:
    """Test cases for makePluginServerRequest function."""

    @patch("avachain.tool_creator.requests.request")
    @patch("avachain.tool_creator.print")
    def test_create_request(self, mock_print, mock_request):
        """Test making a create request to plugin server."""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/create"
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        payload = {"title": "test_plugin", "description": "Test plugin"}
        token = "test_token_123"

        result = makePluginServerRequest("create", payload, token)

        # Check that request was made correctly
        mock_request.assert_called_once_with(
            "POST",
            "https://avaai.pathor.in/api/v1/plugin/createGlobalPlugin",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token_123",
            },
            data=json.dumps(payload),
        )

        assert result == mock_response

    @patch("avachain.tool_creator.requests.request")
    @patch("avachain.tool_creator.print")
    def test_update_request(self, mock_print, mock_request):
        """Test making an update request to plugin server."""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/update"
        mock_response.json.return_value = {"status": "updated"}
        mock_request.return_value = mock_response

        payload = {"title": "test_plugin", "description": "Updated plugin"}
        token = "test_token_123"

        result = makePluginServerRequest("update", payload, token)

        # Check that request was made correctly
        mock_request.assert_called_once_with(
            "PUT",
            "https://avaai.pathor.in/api/v1/plugin/updateGlobalPlugin",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token_123",
            },
            data=json.dumps(payload),
        )

        assert result == mock_response

    @patch("avachain.tool_creator.requests.request")
    @patch("avachain.tool_creator.print")
    def test_delete_request(self, mock_print, mock_request):
        """Test making a delete request to plugin server."""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/delete"
        mock_response.json.return_value = {"status": "deleted"}
        mock_request.return_value = mock_response

        payload = {"title": "test_plugin", "extra_data": "should_be_removed"}
        token = "test_token_123"

        result = makePluginServerRequest("delete", payload, token)

        # Check that request was made correctly with only title
        expected_payload = {"title": "test_plugin"}
        mock_request.assert_called_once_with(
            "DELETE",
            "https://avaai.pathor.in/api/v1/plugin/deleteGlobalPlugin",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token_123",
            },
            data=json.dumps(expected_payload),
        )

        assert result == mock_response

    @patch("avachain.tool_creator.requests.request")
    @patch("avachain.tool_creator.print")
    def test_unknown_action(self, mock_print, mock_request):
        """Test making request with unknown action (defaults to create)."""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/create"
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        payload = {"title": "test_plugin"}
        token = "test_token_123"

        result = makePluginServerRequest("unknown_action", payload, token)

        # Should default to CREATE (POST) request
        mock_request.assert_called_once_with(
            "POST",
            "https://avaai.pathor.in/api/v1/plugin/createGlobalPlugin",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token_123",
            },
            data=json.dumps(payload),
        )

        assert result == mock_response
