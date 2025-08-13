#!/usr/bin/env python3
"""
Test the specific user scenario that was failing
"""

import os
import sys
from pathlib import Path

import pytest

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import ErrorResponse


@pytest.fixture(autouse=True)
def setup_environment():
    """Set up environment variables for testing."""
    os.environ["USE_OLLAMA"] = "true"
    os.environ["OLLAMA_BASE_URL"] = (
        "https://admin_h4LRCjFgJoGKuBrj:gQoNCBMom6v6HHQ7aTVJCLXZxUEdWFt7@ollama.montesmakes.co/v1"
    )
    os.environ["OLLAMA_LLM_MODEL"] = "deepseek-r1:7b"
    os.environ["OLLAMA_EMBEDDING_MODEL"] = "nomic-embed-text"
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "password"


class TestUserScenario:
    """Test the specific scenario that was failing for the user."""

    @pytest.mark.asyncio
    async def test_search_memory_nodes_user_payload(self):
        """Test the exact payload that was causing the -32602 error."""
        from src.graphiti_mcp_server import search_memory_nodes

        # The exact payload from the user's error
        user_payload = {
            "query": "ActionCable WebSocket infinite loop subscription guarantor"
        }

        # This should now work without parameter validation errors
        result = await search_memory_nodes(**user_payload)

        # Should return error about server not being initialized (expected)
        assert isinstance(result, ErrorResponse)
        assert "Server initialization has not started" in result.error

    @pytest.mark.asyncio
    async def test_search_memory_nodes_minimal_payload(self):
        """Test with minimal payload to ensure basic functionality works."""
        from src.graphiti_mcp_server import search_memory_nodes

        # Minimal payload with just the required query parameter
        minimal_payload = {"query": "test query"}

        result = await search_memory_nodes(**minimal_payload)

        # Should return error about server not being initialized (expected)
        assert isinstance(result, ErrorResponse)
        assert "Server initialization has not started" in result.error

    @pytest.mark.asyncio
    async def test_search_memory_nodes_with_optional_params(self):
        """Test with optional parameters to ensure they work correctly."""
        from src.graphiti_mcp_server import search_memory_nodes

        # Test with various optional parameters
        test_cases = [
            {"query": "test query", "max_nodes": 5},
            {"query": "test query", "entity": "Preference"},
            {"query": "test query", "group_ids": ["group1", "group2"]},
            {
                "query": "test query",
                "center_node_uuid": "123e4567-e89b-12d3-a456-426614174000",
            },
            {
                "query": "test query",
                "max_nodes": 10,
                "entity": "Procedure",
                "group_ids": ["group1"],
            },
        ]

        for test_case in test_cases:
            result = await search_memory_nodes(**test_case)

            # Should return error about server not being initialized (expected)
            assert isinstance(result, ErrorResponse)
            assert "Server initialization has not started" in result.error

    def test_function_signature_compatibility(self):
        """Test that the function signature is compatible with MCP framework."""
        import inspect

        from src.graphiti_mcp_server import search_memory_nodes

        sig = inspect.signature(search_memory_nodes)

        # Check that the signature matches what we expect
        assert "query" in sig.parameters
        assert "group_ids" in sig.parameters
        assert "max_nodes" in sig.parameters
        assert "center_node_uuid" in sig.parameters
        assert "entity" in sig.parameters

        # Check parameter types
        query_param = sig.parameters["query"]
        assert query_param.annotation is str
        assert query_param.default == inspect.Parameter.empty  # Required parameter

        group_ids_param = sig.parameters["group_ids"]
        param_str = str(group_ids_param.annotation)
        assert "Optional" in param_str or "Union" in param_str or "| None" in param_str
        assert group_ids_param.default is None

        max_nodes_param = sig.parameters["max_nodes"]
        assert max_nodes_param.annotation is int
        assert max_nodes_param.default == 10

        center_node_uuid_param = sig.parameters["center_node_uuid"]
        param_str = str(center_node_uuid_param.annotation)
        assert "Optional" in param_str or "Union" in param_str or "| None" in param_str
        assert center_node_uuid_param.default is None

        entity_param = sig.parameters["entity"]
        assert entity_param.annotation is str
        assert entity_param.default == ""

    def test_parameter_binding(self):
        """Test that parameters bind correctly to the function signature."""
        import inspect

        from src.graphiti_mcp_server import search_memory_nodes

        sig = inspect.signature(search_memory_nodes)

        # Test the user's exact payload
        user_payload = {
            "query": "ActionCable WebSocket infinite loop subscription guarantor"
        }

        # This should bind without errors
        bound_args = sig.bind(**user_payload)
        assert bound_args is not None
        assert (
            bound_args.arguments["query"]
            == "ActionCable WebSocket infinite loop subscription guarantor"
        )

        # Test with all parameters
        full_payload = {
            "query": "test query",
            "group_ids": ["group1"],
            "max_nodes": 5,
            "center_node_uuid": "test-uuid",
            "entity": "Preference",
        }

        bound_args = sig.bind(**full_payload)
        assert bound_args is not None
        assert bound_args.arguments["query"] == "test query"
        assert bound_args.arguments["group_ids"] == ["group1"]
        assert bound_args.arguments["max_nodes"] == 5
        assert bound_args.arguments["center_node_uuid"] == "test-uuid"
        assert bound_args.arguments["entity"] == "Preference"

    def test_type_annotations(self):
        """Test that type annotations are correct and compatible."""
        import inspect
        from typing import get_args, get_origin

        from src.graphiti_mcp_server import search_memory_nodes

        sig = inspect.signature(search_memory_nodes)

        # Check that Optional types are properly defined
        group_ids_param = sig.parameters["group_ids"]
        group_ids_type = group_ids_param.annotation

        # Should be Optional[List[str]] or list[str] | None
        assert get_origin(group_ids_type) is not None
        group_ids_str = str(group_ids_type)
        assert (
            "Optional" in group_ids_str
            or "Union" in group_ids_str
            or "| None" in group_ids_str
        )

        # Check List type
        args = get_args(group_ids_type)
        assert len(args) == 2  # Union with None
        list_type = args[0] if args[0] is not type(None) else args[1]
        list_type_str = str(list_type)
        # Accept either List[str] or list[str] (modern Python syntax)
        assert "List" in list_type_str or "list[str]" in list_type_str

        # Check center_node_uuid type
        center_node_uuid_param = sig.parameters["center_node_uuid"]
        center_node_uuid_type = center_node_uuid_param.annotation

        assert get_origin(center_node_uuid_type) is not None
        center_node_uuid_str = str(center_node_uuid_type)
        assert (
            "Optional" in center_node_uuid_str
            or "Union" in center_node_uuid_str
            or "| None" in center_node_uuid_str
        )


class TestErrorHandling:
    """Test error handling for the user scenario."""

    @pytest.mark.asyncio
    async def test_error_response_structure(self):
        """Test that error responses have the correct structure."""
        from src.graphiti_mcp_server import search_memory_nodes

        user_payload = {
            "query": "ActionCable WebSocket infinite loop subscription guarantor"
        }

        result = await search_memory_nodes(**user_payload)

        # Check error response structure
        assert isinstance(result, ErrorResponse)
        assert isinstance(result.error, str)
        assert len(result.error) > 0

    @pytest.mark.asyncio
    async def test_error_message_content(self):
        """Test that error messages are informative."""
        from src.graphiti_mcp_server import search_memory_nodes

        user_payload = {
            "query": "ActionCable WebSocket infinite loop subscription guarantor"
        }

        result = await search_memory_nodes(**user_payload)

        # Check that error message is informative
        error_message = result.error
        assert "Server initialization has not started" in error_message
        assert len(error_message) > 20  # Should be descriptive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
