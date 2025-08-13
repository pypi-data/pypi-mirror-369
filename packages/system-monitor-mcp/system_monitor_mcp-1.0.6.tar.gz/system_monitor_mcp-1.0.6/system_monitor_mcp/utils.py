#!/usr/bin/env python3
"""
System Monitor MCP Server - 工具函数模块
"""

import logging
import os
import sys
from typing import Dict, Any

def setup_logging(level=logging.INFO):
    """设置日志配置"""
    # 创建日志目录
    log_dir = os.path.join(os.path.expanduser("~"), ".system_monitor_mcp", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 创建日志处理器
    handlers = [
        logging.StreamHandler(sys.stderr)  # 标准错误输出
    ]
    
    # 配置日志
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("asyncio").setLevel(logging.WARNING)

def format_bytes(bytes_value: int) -> str:
    """将字节数格式化为人类可读的形式"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    elif bytes_value < 1024 ** 4:
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_value / (1024 ** 4):.2f} TB"

def format_uptime(seconds: float) -> str:
    """将秒数格式化为人类可读的运行时间"""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0 or days > 0:
        parts.append(f"{hours}小时")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}分钟")
    parts.append(f"{seconds}秒")
    
    return " ".join(parts)