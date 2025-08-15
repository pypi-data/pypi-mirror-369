import logging
from typing import TypeVar

from liman_core.nodes.tool_node.node import ToolNode
from liman_core.registry import Registry
from openapi_core import OpenAPI

from liman_openapi.operation import OpenAPIOperation
from liman_openapi.parse import parse_endpoints, parse_refs

logger = logging.getLogger(__name__)


def create_tool_nodes(
    openapi_spec: OpenAPI,
    registry: Registry,
    prefix: str = "OpenAPI",
    base_url: str | None = None,
) -> list[ToolNode]:
    """
    Generate ToolNode instances based on OpenAPI endpoints.

    Args:
        openapi_spec (dict): The OpenAPI specification.

    Returns:
        List[ToolNode]: A list of ToolNode instances.
    """
    nodes = []
    spec_content = openapi_spec.spec.content()
    endpoints = parse_endpoints(spec_content)
    refs = parse_refs(spec_content)

    if not base_url:
        servers = spec_content.get("servers", [])
        if servers:
            base_url = servers[0].get("url")

    if not base_url:
        raise ValueError(
            "No base URL found in OpenAPI specification. "
            "Please ensure the 'servers' section is defined "
            "or pass a base_url argument."
        )

    for endpoint in endpoints:
        name = f"{prefix}__{endpoint.operation_id}"
        decl = {
            "kind": "ToolNode",
            "name": name,
            "description": endpoint.summary,
            "arguments": endpoint.get_tool_arguments_spec(refs),
        }

        node = ToolNode.from_dict(decl, registry)
        impl_func = OpenAPIOperation(endpoint, refs, base_url=base_url)
        node.set_func(impl_func)
        nodes.append(node)

    return nodes


R = TypeVar("R")
