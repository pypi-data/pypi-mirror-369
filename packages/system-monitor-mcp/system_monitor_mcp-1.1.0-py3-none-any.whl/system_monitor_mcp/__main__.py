#!/usr/bin/env python3
"""
System Monitor MCP Server - 包入口点
"""

import asyncio
import sys
import os

def main():
    """Entry point for the package"""
    try:
        # 导入服务器模块
        from .server import main as async_main
        
        # 运行异步主函数
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("服务器已停止", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
