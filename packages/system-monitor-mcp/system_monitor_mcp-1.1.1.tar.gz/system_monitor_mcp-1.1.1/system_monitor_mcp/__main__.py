#!/usr/bin/env python3
"""
System Monitor MCP Server - 包入口点
"""

import asyncio
import sys
import os
import argparse

def main():
    """Entry point for the package"""
    parser = argparse.ArgumentParser(description='System Monitor MCP Server')
    parser.add_argument('--version', action='version', version='system-monitor-mcp 1.1.0')
    parser.add_argument('--help-mcp', action='store_true', help='显示MCP服务器帮助信息')
    
    args = parser.parse_args()
    
    if args.help_mcp:
        print("System Monitor MCP Server")
        print("提供系统监控功能的MCP服务器")
        print("支持的工具: get_system_info, get_cpu_info, get_memory_info, get_disk_info, get_network_info, get_processes_info, monitor_resource")
        return
    
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
