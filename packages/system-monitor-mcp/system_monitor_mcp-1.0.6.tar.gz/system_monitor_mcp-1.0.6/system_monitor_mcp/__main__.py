#!/usr/bin/env python3
"""
System Monitor MCP Server - 包入口点
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from .server import main as async_main

def main():
    """Entry point for the package"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("服务器已停止", file=sys.stderr)

if __name__ == "__main__":
    main()
        sys.exit(0)