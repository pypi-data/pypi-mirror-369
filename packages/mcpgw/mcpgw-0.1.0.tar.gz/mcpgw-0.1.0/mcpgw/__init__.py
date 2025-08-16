"""
MCP Gateway - A lightweight, security-focused FastAPI gateway for Model Context Protocol (MCP) servers

This package provides a secure intermediary service that sits between MCP clients and servers,
offering authentication, authorization, rate limiting, request validation, and audit logging.
"""

__version__ = "0.1.0"
__author__ = "Mark Lechner"
__email__ = "hello@marklechner.dev"
__description__ = "A lightweight, security-focused FastAPI gateway for Model Context Protocol (MCP) servers"

from .main import app, security_manager, server_manager

__all__ = [
    "app",
    "security_manager", 
    "server_manager",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
