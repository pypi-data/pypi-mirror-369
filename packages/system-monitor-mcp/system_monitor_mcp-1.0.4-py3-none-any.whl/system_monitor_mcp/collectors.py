#!/usr/bin/env python3
"""
System Monitor MCP Server - 数据收集模块
"""

import platform
import time
from typing import Dict, Any

import psutil

from .utils import format_uptime

async def collect_system_info() -> Dict[str, Any]:
    """收集系统基本信息"""
    # CPU信息
    cpu_freq = psutil.cpu_freq()
    cpu_info = {
        'physical_cores': psutil.cpu_count(logical=False),
        'logical_cores': psutil.cpu_count(logical=True),
        'current_freq': cpu_freq.current if cpu_freq else 0,
        'max_freq': cpu_freq.max if cpu_freq else 0,
        'min_freq': cpu_freq.min if cpu_freq else 0,
        'usage': psutil.cpu_percent(interval=1)
    }
    
    # 内存信息
    mem = psutil.virtual_memory()
    memory_info = {
        'total': mem.total,
        'available': mem.available,
        'used': mem.used,
        'free': mem.free,
        'percent': mem.percent
    }
    
    # 系统信息
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    return {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'node': platform.node()
        },
        'cpu': cpu_info,
        'memory': memory_info,
        'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time)),
        'uptime': format_uptime(uptime_seconds)
    }

async def collect_cpu_info() -> Dict[str, Any]:
    """收集CPU信息"""
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()
    
    return {
        'timestamp': time.time(),
        'usage_total': sum(cpu_percent) / len(cpu_percent),
        'usage_per_cpu': cpu_percent,
        'frequency': {
            'current': cpu_freq.current if cpu_freq else 0,
            'max': cpu_freq.max if cpu_freq else 0,
            'min': cpu_freq.min if cpu_freq else 0
        },
        'cores': {
            'physical': psutil.cpu_count(logical=False),
            'logical': psutil.cpu_count(logical=True)
        }
    }

async def collect_memory_info() -> Dict[str, Any]:
    """收集内存信息"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'timestamp': time.time(),
        'virtual': {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'cached': mem.cached,
            'buffers': mem.buffers
        },
        'swap': {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        }
    }

async def collect_disk_info() -> Dict[str, Any]:
    """收集磁盘信息"""
    partitions = psutil.disk_partitions()
    disk_info = {
        'timestamp': time.time(),
        'partitions': [],
        'io_counters': None
    }
    
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info['partitions'].append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            })
        except PermissionError:
            disk_info['partitions'].append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'error': 'Permission denied'
            })
    
    # 磁盘I/O统计
    disk_io = psutil.disk_io_counters()
    if disk_io:
        disk_info['io_counters'] = {
            'read_count': disk_io.read_count,
            'write_count': disk_io.write_count,
            'read_bytes': disk_io.read_bytes,
            'write_bytes': disk_io.write_bytes,
            'read_time': disk_io.read_time,
            'write_time': disk_io.write_time
        }
    
    return disk_info

async def collect_network_info() -> Dict[str, Any]:
    """收集网络信息"""
    net_io = psutil.net_io_counters()
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    
    network_info = {
        'timestamp': time.time(),
        'io_counters': {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        },
        'interfaces': {}
    }
    
    for interface, addrs in net_if_addrs.items():
        stats = net_if_stats.get(interface)
        interface_info = {
            'addresses': [],
            'stats': {}
        }
        
        if stats:
            interface_info['stats'] = {
                'isup': stats.isup,
                'duplex': stats.duplex,
                'speed': stats.speed,
                'mtu': stats.mtu
            }
        
        for addr in addrs:
            addr_info = {
                'family': addr.family,
                'address': addr.address
            }
            if addr.netmask:
                addr_info['netmask'] = addr.netmask
            if addr.broadcast:
                addr_info['broadcast'] = addr.broadcast
            
            interface_info['addresses'].append(addr_info)
        
        network_info['interfaces'][interface] = interface_info
    
    return network_info

async def collect_processes_info() -> Dict[str, Any]:
    """收集进程信息"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'create_time', 'cmdline']):
        try:
            pinfo = proc.info
            processes.append({
                'pid': pinfo['pid'],
                'name': pinfo['name'],
                'cpu_percent': pinfo['cpu_percent'],
                'memory_percent': pinfo['memory_percent'],
                'status': pinfo['status'],
                'username': pinfo['username'] or 'N/A',
                'create_time': pinfo['create_time'],
                'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # 按CPU使用率排序
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    
    return {
        'timestamp': time.time(),
        'total_processes': len(processes),
        'processes': processes[:50]  # 只返回前50个进程
    }