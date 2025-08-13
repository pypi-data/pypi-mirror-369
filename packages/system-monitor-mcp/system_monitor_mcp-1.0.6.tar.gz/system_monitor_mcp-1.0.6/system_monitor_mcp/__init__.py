#!/usr/bin/env python3
"""
System Monitor MCP Server - 包初始化文件
"""

__version__ = "1.0.6"
__author__ = "Undoom"
__description__ = "System Monitor MCP Server - 系统监控MCP服务器"

from .server import MCPServer, main

# 为了兼容性，也导出SystemMonitorMCP别名
SystemMonitorMCP = MCPServer