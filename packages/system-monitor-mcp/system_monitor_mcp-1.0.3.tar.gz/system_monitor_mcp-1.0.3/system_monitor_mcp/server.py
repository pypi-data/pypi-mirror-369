#!/usr/bin/env python3
"""
System Monitor MCP Server - 主服务器模块
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional

from .collectors import (
    collect_system_info,
    collect_cpu_info,
    collect_memory_info,
    collect_disk_info,
    collect_network_info,
    collect_processes_info
)
from .utils import setup_logging

# 设置日志
logger = logging.getLogger("system_monitor_mcp")

class MCPServer:
    """MCP服务器实现"""
    
    def __init__(self):
        """初始化MCP服务器"""
        self.tools = {
            "get_system_info": {
                "description": "获取系统基本信息，包括CPU、内存、操作系统等",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_cpu_info": {
                "description": "获取CPU详细信息，包括使用率、频率等",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_memory_info": {
                "description": "获取内存详细信息，包括物理内存和交换内存",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_disk_info": {
                "description": "获取磁盘详细信息，包括分区和I/O统计",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_network_info": {
                "description": "获取网络详细信息，包括接口和流量统计",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_processes_info": {
                "description": "获取进程详细信息，包括CPU使用率、内存使用率等",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "返回的进程数量限制，默认为50",
                            "default": 50
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "排序字段，可选值：cpu_percent, memory_percent, pid, name",
                            "enum": ["cpu_percent", "memory_percent", "pid", "name"],
                            "default": "cpu_percent"
                        },
                        "sort_desc": {
                            "type": "boolean",
                            "description": "是否降序排序",
                            "default": True
                        }
                    },
                    "required": []
                }
            },
            "monitor_resource": {
                "description": "监控系统资源使用情况，定期返回资源数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "要监控的资源类型",
                            "enum": ["cpu", "memory", "disk", "network", "all"],
                            "default": "all"
                        },
                        "interval": {
                            "type": "integer",
                            "description": "监控间隔（秒），默认为5秒",
                            "default": 5
                        },
                        "duration": {
                            "type": "integer",
                            "description": "监控持续时间（秒），默认为60秒",
                            "default": 60
                        }
                    },
                    "required": ["resource_type"]
                }
            }
        }
        
        self.resources = []
        
    async def get_system_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取系统基本信息"""
        return await collect_system_info()
    
    async def get_cpu_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取CPU详细信息"""
        return await collect_cpu_info()
    
    async def get_memory_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取内存详细信息"""
        return await collect_memory_info()
    
    async def get_disk_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取磁盘详细信息"""
        return await collect_disk_info()
    
    async def get_network_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取网络详细信息"""
        return await collect_network_info()
    
    async def get_processes_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取进程详细信息"""
        limit = args.get("limit", 50)
        sort_by = args.get("sort_by", "cpu_percent")
        sort_desc = args.get("sort_desc", True)
        
        processes_info = await collect_processes_info()
        
        # 排序进程
        processes = processes_info["processes"]
        processes.sort(key=lambda x: x.get(sort_by, 0), reverse=sort_desc)
        
        # 限制返回数量
        processes_info["processes"] = processes[:limit]
        
        return processes_info
    
    async def monitor_resource(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """监控系统资源使用情况"""
        resource_type = args.get("resource_type", "all")
        interval = args.get("interval", 5)
        duration = args.get("duration", 60)
        
        # 计算需要监控的次数
        count = max(1, duration // interval)
        
        # 初始化结果
        result = {
            "resource_type": resource_type,
            "interval": interval,
            "duration": duration,
            "data": []
        }
        
        # 根据资源类型选择监控函数
        monitor_functions = {}
        if resource_type == "all" or resource_type == "cpu":
            monitor_functions["cpu"] = collect_cpu_info
        if resource_type == "all" or resource_type == "memory":
            monitor_functions["memory"] = collect_memory_info
        if resource_type == "all" or resource_type == "disk":
            monitor_functions["disk"] = collect_disk_info
        if resource_type == "all" or resource_type == "network":
            monitor_functions["network"] = collect_network_info
        
        # 开始监控
        for i in range(count):
            data_point = {"timestamp": None}
            
            # 收集各类资源数据
            for res_type, func in monitor_functions.items():
                res_data = await func()
                data_point["timestamp"] = res_data["timestamp"]
                data_point[res_type] = res_data
            
            result["data"].append(data_point)
            
            # 如果不是最后一次，则等待间隔时间
            if i < count - 1:
                await asyncio.sleep(interval)
        
        return result
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理JSON-RPC请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                # 初始化响应
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": self.tools,
                            "resources": self.resources
                        },
                        "serverInfo": {
                            "name": "system-monitor-mcp",
                            "version": "0.1.1"
                        }
                    }
                }
            
            elif method == "tools/call":
                # 工具调用
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                try:
                    # 调用对应的工具函数
                    if tool_name == "get_system_info":
                        result = await self.get_system_info(tool_args)
                    elif tool_name == "get_cpu_info":
                        result = await self.get_cpu_info(tool_args)
                    elif tool_name == "get_memory_info":
                        result = await self.get_memory_info(tool_args)
                    elif tool_name == "get_disk_info":
                        result = await self.get_disk_info(tool_args)
                    elif tool_name == "get_network_info":
                        result = await self.get_network_info(tool_args)
                    elif tool_name == "get_processes_info":
                        result = await self.get_processes_info(tool_args)
                    elif tool_name == "monitor_resource":
                        result = await self.monitor_resource(tool_args)
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2, ensure_ascii=False)
                                }
                            ]
                        }
                    }
                    
                except Exception as e:
                    logger.exception(f"Error executing tool {tool_name}")
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
            
            elif method == "tools/list":
                # 列出可用工具
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": info["description"],
                                "inputSchema": info["inputSchema"]
                            }
                            for name, info in self.tools.items()
                        ]
                    }
                }
            
            elif method == "resources/list":
                # 列出可用资源
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "resources": self.resources
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            logger.exception("Error handling request")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """运行MCP服务器"""
        logger.info("System Monitor MCP Server starting...")
        
        # 使用标准输入/输出进行通信
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
        
        logger.info("MCP Server ready to receive messages")
        
        while True:
            try:
                # 读取一行JSON消息
                line = await asyncio.get_event_loop().run_in_executor(
                    None, stdin.readline
                )
                
                if not line:
                    logger.info("Connection closed")
                    break
                
                # 解析JSON请求
                try:
                    request = json.loads(line.decode('utf-8').strip())
                    logger.debug(f"Received request: {request}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                
                # 处理请求
                response = await self.handle_request(request)
                logger.debug(f"Sending response: {response}")
                
                # 发送响应
                response_line = json.dumps(response) + '\n'
                stdout.write(response_line.encode('utf-8'))
                stdout.flush()
                
            except Exception as e:
                logger.exception("Error processing message")
                # 发送错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                error_line = json.dumps(error_response) + '\n'
                stdout.write(error_line.encode('utf-8'))
                stdout.flush()

async def main():
    """主函数"""
    # 设置日志
    setup_logging(logging.DEBUG)
    
    # 创建并运行MCP服务器
    server = MCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())