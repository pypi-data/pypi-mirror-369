"""
Avachain Tool Creator - Tool management and conversion utilities.

This module provides utilities for creating, converting, and managing AI agent tools.
It includes functions for converting BaseTool objects to JSON format compatible with
various AI platforms and APIs, as well as plugin server integration capabilities.
"""

import inspect
import json
import os
import textwrap
from typing import Any, Dict, Optional

import requests
from print_color import print
from pydantic_core import PydanticUndefined

from .avachain import BaseTool


def map_type_to_json(type_info):
    """
    Map Python types to JSON schema type strings.

    This function converts Python built-in types to their corresponding
    JSON schema type representations for API compatibility.

    Args:
        type_info: Python type object (int, float, str, bool, etc.)

    Returns:
        str: JSON schema type string ("number", "string", "boolean", etc.)

    Example:
        >>> map_type_to_json(int)
        'number'
        >>> map_type_to_json(str)
        'string'
    """
    type_mappings = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
    }
    return type_mappings.get(type_info, str(type_info))


def convert_tool_to_json(
    tool: BaseTool,
    tool_id: str,
    human_description: str,
    public_name: str,
    logo: str = None,
    isAnonymous: bool = False,
    authentication_required: Optional[bool] = False,
    connection_url: Optional[str] = "",
    isAuthenticated: bool = False,
    isPublic: bool = True,
    isMain: bool = False,
    tags: Optional[list] = None,
    supports_android: bool = False,
    supports_windows: bool = True,
) -> Dict[str, Any]:
    """
    Convert a BaseTool object into a comprehensive JSON representation for plugin systems.

    This function transforms a BaseTool instance into a detailed JSON schema format
    suitable for plugin marketplaces and tool registries. It extracts the tool's
    source code, metadata, and parameter schema to create a complete tool specification.

    Args:
        tool (BaseTool): The tool object to convert
        tool_id (str): Unique identifier for the tool in the plugin system
        human_description (str): Human-readable description for end users
        public_name (str): Display name for the tool
        logo (str, optional): URL or path to the tool's logo/icon
        isAnonymous (bool): Whether the tool can be used anonymously
        authentication_required (bool): Whether authentication is required
        connection_url (str): URL for establishing connections if needed
        isAuthenticated (bool): Current authentication status
        isPublic (bool): Whether the tool is publicly available
        isMain (bool): Whether this is the main/primary tool
        tags (list): List of tags for categorization
        supports_android (bool): Android platform support
        supports_windows (bool): Windows platform support

    Returns:
        Dict[str, Any]: Comprehensive JSON representation of the tool

    Raises:
        ValueError: If neither android nor windows support is specified

    Example:
        >>> tool = MyTool(name="search", description="Search the web")
        >>> json_tool = convert_tool_to_json(
        ...     tool, "search_v1", "Web Search Tool", "Search"
        ... )
    """
    # Extract the source code of the tool's _run method for inspection/execution
    run_method_source = inspect.getsource(tool._run)
    run_method_source = textwrap.dedent(run_method_source)
    print(run_method_source)

    # Validate platform support - at least one platform must be supported
    if not supports_android and not supports_windows:
        raise ValueError(
            "You must specify at least one of 'android', 'windows' as the os"
        )

    # Build supported OS list
    os_support = []
    if supports_windows:
        os_support.append(os.name)
    if supports_android:
        os_support = ["android"]

    # Create the comprehensive JSON representation
    json_representation = {
        "title": tool_id,
        "os": os_support,
        "human_description": human_description,
        "name": public_name,
        "ai_description": tool.description,
        "logo": logo,
        "isAnonymous": isAnonymous,
        "authentication_required": authentication_required,
        "connection_url": connection_url,
        "isAuthenticated": isAuthenticated,
        "isPublic": isPublic,
        "tags": tags if tags is not None else [],
        "func_run": run_method_source,
        "func_schema": {},
        "parameters": {
            "tool_extras": {
                "isMain": isMain,
                "isDirect": tool.return_direct,
                "name": tool.name,
            },
            "tool_parameters": {},
        },
    }

    # Build required arguments list and parameter schema
    required_args = []

    if tool.args_schema:
        # Process each field in the tool's argument schema
        for field_name, field_info in tool.args_schema.__annotations__.items():
            # Get field description from the Pydantic model field
            field_description = getattr(
                tool.args_schema.model_fields[field_name],
                "description",
                "No description available",
            )

            # Create field properties for JSON schema
            field_properties = {
                "type": map_type_to_json(field_info),
                "description": field_description,
            }

            # Check if field is required (repr=True in Pydantic)
            if tool.args_schema.model_fields[field_name].repr:
                required_args.append(str(field_name))

            # Handle default values
            default_value = tool.args_schema.model_fields[field_name].default
            field_properties["default"] = ""
            if default_value is not None and default_value is not PydanticUndefined:
                field_properties["default"] = default_value

            # Handle enum values if present
            enums_present = tool.args_schema.model_fields[field_name].json_schema_extra
            field_properties["enum"] = []
            if enums_present:
                enum_values = enums_present.get("enumerate", None)
                if enum_values is not None:
                    field_properties["enum"] = enum_values

            # Add field to the parameters schema
            json_representation["parameters"]["tool_parameters"][
                field_name
            ] = field_properties

    return json_representation


def makePluginServerRequest(action: str, payload_data: dict, token: str):
    """
    Make authenticated requests to the plugin server API.

    This function handles CREATE, UPDATE, and DELETE operations for plugins
    on the Avachain plugin server. It automatically configures the appropriate
    HTTP method and endpoint based on the action type.

    Args:
        action (str): Type of action - "create", "update", or "delete"
        payload_data (dict): Data to send in the request body
        token (str): Authentication Bearer token

    Returns:
        requests.Response: The HTTP response from the server

    Example:
        >>> response = makePluginServerRequest(
        ...     "create",
        ...     {"title": "my_tool", "description": "My awesome tool"},
        ...     "your_auth_token"
        ... )
    """
    # Default configuration for create action
    url = "https://avaai.pathor.in/api/v1/plugin/createGlobalPlugin"
    method = "POST"

    # Configure URL and method based on action type
    if action == "update":
        url = "https://avaai.pathor.in/api/v1/plugin/updateGlobalPlugin"
        method = "PUT"
    elif action == "delete":
        url = "https://avaai.pathor.in/api/v1/plugin/deleteGlobalPlugin"
        method = "DELETE"
        # For delete operations, only send the title identifier
        payload_data = {"title": payload_data.get("title")}

    # Prepare request payload and headers
    payload = json.dumps(payload_data)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # Make the HTTP request
    response = requests.request(method, url, headers=headers, data=payload)

    # Log the response for debugging
    print(response.url, " : ", response.json())
    return response
