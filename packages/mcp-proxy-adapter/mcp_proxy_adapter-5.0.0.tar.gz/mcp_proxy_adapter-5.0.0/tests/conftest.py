"""
Configuration for pytest.
"""

import pytest

from mcp_proxy_adapter.commands import registry, container
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.dependency_container import DependencyContainer


@pytest.fixture(autouse=True)
def reset_registry_and_container():
    """
    Reset command registry and dependency container before each test.
    
    This fixture ensures that tests don't affect each other
    by having leftover commands or dependencies.
    """
    # Store the original registry state
    original_builtin = registry._builtin_commands.copy()
    original_custom = registry._custom_commands.copy()
    original_loaded = registry._loaded_commands.copy()
    original_instances = registry._instances.copy()
    
    # Reset for the test
    registry.clear()
    container.clear()
    
    # Run the test
    yield
    
    # Restore original state after test
    registry._builtin_commands = original_builtin
    registry._custom_commands = original_custom
    registry._loaded_commands = original_loaded
    registry._instances = original_instances
    container.clear()


@pytest.fixture
def empty_registry():
    """
    Provide a fresh, empty command registry.
    """
    return CommandRegistry()


@pytest.fixture
def empty_container():
    """
    Provide a fresh, empty dependency container.
    """
    return DependencyContainer() 