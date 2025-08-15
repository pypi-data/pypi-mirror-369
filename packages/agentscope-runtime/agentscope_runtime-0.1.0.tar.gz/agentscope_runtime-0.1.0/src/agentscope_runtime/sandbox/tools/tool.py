# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from ..enums import SandboxType


class Tool(ABC):
    """Abstract base class for all tools.

    This abstract class defines the common interface that all tool
    implementations must follow, including both SandboxTool and FunctionTool.

    Key responsibilities:
    - Define the standard tool interface
    - Ensure consistent behavior across different tool types
    - Provide common functionality where applicable
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        tool_type: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the tool with basic parameters.

        Args:
            name: Tool name
            tool_type: Tool type identifier
            **kwargs: Additional tool-specific parameters
        """
        self._name = name
        self._tool_type = tool_type

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the tool name."""

    @property
    @abstractmethod
    def tool_type(self) -> str:
        """Get the tool type."""

    @property
    @abstractmethod
    def schema(self) -> Dict:
        """Get the tool schema in OpenAI function calling format."""

    @property
    @abstractmethod
    def sandbox_type(self) -> SandboxType:
        """Get the required sandbox type for this tool."""

    @property
    @abstractmethod
    def sandbox(self) -> Optional[Any]:
        """Get the current sandbox instance (if any)."""

    def __call__(self, *, sandbox: Optional[Any] = None, **kwargs):
        """Call the tool with optional sandbox override.

        This is a convenience method that delegates to the call() method.

        Args:
            sandbox: Optional sandbox to use for this call
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        return self.call(sandbox=sandbox, **kwargs)

    @abstractmethod
    def call(self, *, sandbox: Optional[Any] = None, **kwargs) -> Dict:
        """Execute the tool call.

        This is the core method that each tool implementation must provide.

        Args:
            sandbox: Optional sandbox to use for this call
            **kwargs: Tool parameters

        Returns:
            Tool execution result in standardized format:
            {
                "meta": Optional[Dict],
                "content": List[Dict],
                "isError": bool
            }
        """

    @abstractmethod
    def bind(self, *args, **kwargs) -> "Tool":
        """Bind parameters or context to create a new tool instance.

        The specific binding behavior depends on the tool type:
        - SandboxTool: binds to a sandbox
        - FunctionTool: binds function parameters

        Returns:
            New tool instance with bound parameters/context
        """

    def __str__(self) -> str:
        """String representation of the tool."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', type="
            f"'{self.tool_type}')"
        )

    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"tool_type='{self.tool_type}', "
            f"sandbox_type='{self.sandbox_type}'"
            f")"
        )
