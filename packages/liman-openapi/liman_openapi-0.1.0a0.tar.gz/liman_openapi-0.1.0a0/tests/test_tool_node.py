from typing import Any
from unittest.mock import Mock, patch

import pytest
from jsonschema_path.typing import Schema
from liman_core.nodes.tool_node.node import ToolNode
from liman_core.registry import Registry

from liman_openapi.operation import OpenAPIOperation
from liman_openapi.schemas import Endpoint
from liman_openapi.tool_node import create_tool_nodes


@pytest.fixture
def registry() -> Registry:
    return Registry()


def test_create_tool_nodes_empty_spec(registry: Registry) -> None:
    empty_spec: Schema = {
        "openapi": "3.0.0",
        "info": {"title": "Empty API", "version": "1.0.0"},
        "paths": {},
        "servers": [{"url": "https://api.example.com"}],
    }

    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
    ):
        mock_parse_endpoints.return_value = []
        mock_parse_refs.return_value = {}

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = empty_spec

        nodes = create_tool_nodes(mock_openapi, registry)

        assert nodes == []
        mock_parse_endpoints.assert_called_once_with(empty_spec)
        mock_parse_refs.assert_called_once_with(empty_spec)


def test_create_tool_nodes_single_endpoint(
    simple_openapi_schema: dict[str, Any], registry: Registry
) -> None:
    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
        patch("liman_openapi.tool_node.ToolNode.from_dict") as mock_from_dict,
    ):
        endpoint = Endpoint.model_validate(
            {
                "operationId": "get_user",
                "summary": "Get user by ID",
                "method": "GET",
                "path": "/users/{user_id}",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "description": "User ID",
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User found",
                        "content": {"application/json": {"schema": {"type": "string"}}},
                    }
                },
            }
        )

        mock_parse_endpoints.return_value = [endpoint]
        mock_parse_refs.return_value = {}

        mock_node = Mock(spec=ToolNode)
        mock_from_dict.return_value = mock_node

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = simple_openapi_schema

        nodes = create_tool_nodes(
            mock_openapi, registry, base_url="https://api.example.com"
        )

        assert len(nodes) == 1
        assert nodes[0] == mock_node

        mock_from_dict.assert_called_once_with(
            {
                "kind": "ToolNode",
                "name": "OpenAPI__get_user",
                "description": "Get user by ID",
                "arguments": [
                    {
                        "name": "user_id",
                        "type": "string",
                        "description": "User ID",
                        "optional": False,
                    }
                ],
            },
            registry,
        )

        mock_node.set_func.assert_called_once()
        call_args = mock_node.set_func.call_args[0][0]
        assert isinstance(call_args, OpenAPIOperation)


def test_create_tool_nodes_custom_prefix(
    simple_openapi_schema: dict[str, Any], registry: Registry
) -> None:
    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
        patch("liman_openapi.tool_node.ToolNode.from_dict") as mock_from_dict,
    ):
        endpoint = Endpoint.model_validate(
            {
                "operationId": "get_user",
                "summary": "Get user by ID",
                "method": "GET",
                "path": "/users/{user_id}",
                "responses": {
                    "200": {
                        "description": "User found",
                        "content": {"application/json": {"schema": {"type": "string"}}},
                    }
                },
            }
        )

        mock_parse_endpoints.return_value = [endpoint]
        mock_parse_refs.return_value = {}

        mock_node = Mock(spec=ToolNode)
        mock_from_dict.return_value = mock_node

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = simple_openapi_schema

        nodes = create_tool_nodes(
            mock_openapi,
            registry,
            prefix="CustomAPI",
            base_url="https://api.example.com",
        )

        mock_from_dict.assert_called_once_with(
            {
                "kind": "ToolNode",
                "name": "CustomAPI__get_user",
                "description": "Get user by ID",
                "arguments": None,
            },
            registry,
        )
        assert len(nodes) == 1


def test_create_tool_nodes_with_base_url(
    complex_openapi_schema: dict[str, Any], registry: Registry
) -> None:
    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
        patch("liman_openapi.tool_node.ToolNode.from_dict") as mock_from_dict,
    ):
        endpoint = Endpoint.model_validate(
            {
                "operationId": "create_user",
                "summary": "Create user",
                "method": "POST",
                "path": "/users",
                "responses": {
                    "201": {
                        "description": "User created",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        )

        mock_parse_endpoints.return_value = [endpoint]
        mock_parse_refs.return_value = {}

        mock_node = Mock(spec=ToolNode)
        mock_from_dict.return_value = mock_node

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = complex_openapi_schema

        nodes = create_tool_nodes(mock_openapi, registry)

        mock_node.set_func.assert_called_once()
        call_args = mock_node.set_func.call_args[0][0]
        assert isinstance(call_args, OpenAPIOperation)
        assert call_args.base_url == "https://api.example.com"
        assert len(nodes) == 1


def test_create_tool_nodes_multiple_endpoints(
    complex_openapi_schema: dict[str, Any], registry: Registry
) -> None:
    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
        patch("liman_openapi.tool_node.ToolNode.from_dict") as mock_from_dict,
    ):
        from liman_openapi.schemas import Endpoint

        endpoints = [
            Endpoint.model_validate(
                {
                    "operationId": "create_user",
                    "summary": "Create user",
                    "method": "POST",
                    "path": "/users",
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }
                    },
                }
            ),
            Endpoint.model_validate(
                {
                    "operationId": "get_user_by_id",
                    "summary": "Get user by ID",
                    "method": "GET",
                    "path": "/users/{user_id}",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "description": "User ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User found",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }
                    },
                }
            ),
        ]

        mock_parse_endpoints.return_value = endpoints
        mock_parse_refs.return_value = {}

        mock_nodes = [Mock(spec=ToolNode), Mock(spec=ToolNode)]
        mock_from_dict.side_effect = mock_nodes

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = complex_openapi_schema

        nodes = create_tool_nodes(mock_openapi, registry)

        assert len(nodes) == 2
        assert nodes == mock_nodes

        assert mock_from_dict.call_count == 2

        calls = mock_from_dict.call_args_list
        assert calls[0][0][0]["name"] == "OpenAPI__create_user"
        assert calls[1][0][0]["name"] == "OpenAPI__get_user_by_id"


def test_create_tool_nodes_no_parameters(registry: Registry) -> None:
    with (
        patch("liman_openapi.tool_node.parse_endpoints") as mock_parse_endpoints,
        patch("liman_openapi.tool_node.parse_refs") as mock_parse_refs,
        patch("liman_openapi.tool_node.ToolNode.from_dict") as mock_from_dict,
    ):
        endpoint = Endpoint.model_validate(
            {
                "operationId": "health_check",
                "summary": "Health check",
                "method": "GET",
                "path": "/health",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"type": "string"}}},
                    }
                },
            }
        )

        mock_parse_endpoints.return_value = [endpoint]
        mock_parse_refs.return_value = {}

        mock_node = Mock(spec=ToolNode)
        mock_from_dict.return_value = mock_node

        mock_openapi = Mock()
        mock_openapi.spec.content.return_value = {}

        nodes = create_tool_nodes(
            mock_openapi, registry, base_url="https://api.example.com"
        )

        mock_from_dict.assert_called_once_with(
            {
                "kind": "ToolNode",
                "name": "OpenAPI__health_check",
                "description": "Health check",
                "arguments": None,
            },
            registry,
        )
        assert len(nodes) == 1
