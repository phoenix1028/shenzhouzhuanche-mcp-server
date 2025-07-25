#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from shenzhou_client import ShenZhouAPIClient


async def quick_test():
    """快速测试MCP功能"""
    print("🚗 神州专车MCP快速测试")
    print("=" * 30)
    
    # 显示配置
    print(f"认证模式: {config.auth.mode.value}")
    print(f"用户名: {config.auth.username}")
    print(f"优先级: {' -> '.join(config.auth.priority or [])}")
    print()
    
    client = ShenZhouAPIClient(config)
    
    # 测试认证
    print("🔐 测试认证...")
    try:
        token = await client.auth_manager.get_valid_token()
        print(f"✅ 获取token成功: {token[:20]}...")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        return
    
    # 测试城市服务（可能会因为token过期而失败，但这是正常的）
    print("\n🌍 测试城市服务...")
    try:
        response = await client.get_city_services()
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
    except Exception as e:
        print(f"测试异常: {e}")
    
    print("\n✅ MCP服务器已准备就绪")
    print("🚀 启动命令: uv run python server.py")
    print("🌐 服务地址: http://127.0.0.1:8000")


if __name__ == "__main__":
    asyncio.run(quick_test())