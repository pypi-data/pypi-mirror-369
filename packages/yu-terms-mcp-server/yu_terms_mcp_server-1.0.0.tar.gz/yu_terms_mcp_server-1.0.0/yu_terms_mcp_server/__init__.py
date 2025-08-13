"""
Yu Terms MCP Server

A Python implementation of MCP (Model Context Protocol) server 
for terms management functionality.

This package provides tools for updating and managing terms elements,
equivalent to the Java Spring AI implementation.
"""

__version__ = "1.0.0"
__author__ = "YuPi"
__email__ = "your-email@example.com"

from .server import TermsMcpServer
from .tools import TermsUpdatedTool

__all__ = ["TermsMcpServer", "TermsUpdatedTool"]
