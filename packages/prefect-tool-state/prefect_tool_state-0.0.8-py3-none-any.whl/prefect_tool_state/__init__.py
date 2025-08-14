"""
Prefect Progress - High-throughput progress publisher for Prefect tools

This package provides optimized publishing capabilities for high-frequency tool state updates
in Prefect workflows, with automatic batching and background processing.
"""

from .tool_state import ToolState
from .tool_state_publisher import ToolStatePublisher, get_tool_state_publisher
from .tool_state_manager import ToolStateManager

__version__ = "0.1.0"
__all__ = [
    "ToolState",
    "ToolStatePublisher",
    "ToolStateManager",
    "get_tool_state_publisher",
]
