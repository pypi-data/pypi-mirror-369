"""
MCP Gateway Service Module
==========================

This module provides the Model Context Protocol (MCP) gateway implementation for Claude MPM.
It enables integration with MCP-compatible tools and services through a standardized interface.

Part of ISS-0034: Infrastructure Setup - MCP Gateway Project Foundation

The MCP Gateway follows the claude-mpm service-oriented architecture with:
- Interface-based contracts for all components
- Dependency injection for service resolution
- Lazy loading for performance optimization
- Comprehensive error handling and logging

Structure:
- core/: Core interfaces and base classes for MCP services
- server/: MCP server implementation and lifecycle management
- tools/: Tool registry and tool adapter implementations
- config/: Configuration management for MCP Gateway
- registry/: Service discovery and registration
"""

# Version information
__version__ = "0.1.0"

# Lazy imports to prevent circular dependencies and improve startup performance
def __getattr__(name):
    """Lazy import mechanism for MCP Gateway components."""
    
    # Core interfaces and base classes
    if name == "IMCPServer":
        from .core.interfaces import IMCPServer
        return IMCPServer
    elif name == "IMCPToolRegistry":
        from .core.interfaces import IMCPToolRegistry
        return IMCPToolRegistry
    elif name == "IMCPConfiguration":
        from .core.interfaces import IMCPConfiguration
        return IMCPConfiguration
    elif name == "IMCPToolAdapter":
        from .core.interfaces import IMCPToolAdapter
        return IMCPToolAdapter
    elif name == "BaseMCPService":
        from .core.base import BaseMCPService
        return BaseMCPService
    
    # Server implementations
    elif name == "MCPServer":
        from .server.mcp_server import MCPServer
        return MCPServer
    elif name == "MCPServerManager":
        from .server.server_manager import MCPServerManager
        return MCPServerManager
    
    # Tool registry and adapters
    elif name == "MCPToolRegistry":
        from .tools.tool_registry import MCPToolRegistry
        return MCPToolRegistry
    elif name == "ToolAdapter":
        from .tools.tool_adapter import ToolAdapter
        return ToolAdapter
    
    # Configuration management
    elif name == "MCPConfiguration":
        from .config.configuration import MCPConfiguration
        return MCPConfiguration
    elif name == "MCPConfigLoader":
        from .config.config_loader import MCPConfigLoader
        return MCPConfigLoader
    
    # Service registry
    elif name == "MCPServiceRegistry":
        from .registry.service_registry import MCPServiceRegistry
        return MCPServiceRegistry
    
    # Exceptions
    elif name == "MCPException":
        from .core.exceptions import MCPException
        return MCPException
    elif name == "MCPConfigurationError":
        from .core.exceptions import MCPConfigurationError
        return MCPConfigurationError
    elif name == "MCPToolNotFoundError":
        from .core.exceptions import MCPToolNotFoundError
        return MCPToolNotFoundError
    elif name == "MCPServerError":
        from .core.exceptions import MCPServerError
        return MCPServerError
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Public API exports
__all__ = [
    # Core interfaces
    "IMCPServer",
    "IMCPToolRegistry",
    "IMCPConfiguration",
    "IMCPToolAdapter",
    "BaseMCPService",
    
    # Server implementations
    "MCPServer",
    "MCPServerManager",
    
    # Tool management
    "MCPToolRegistry",
    "ToolAdapter",
    
    # Configuration
    "MCPConfiguration",
    "MCPConfigLoader",
    
    # Service registry
    "MCPServiceRegistry",
    
    # Exceptions
    "MCPException",
    "MCPConfigurationError",
    "MCPToolNotFoundError",
    "MCPServerError",
]