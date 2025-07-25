#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from typing import Any, Dict

# 添加当前目录到路径，以便导入本地模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from models import OrderRequest, LocationUpdateRequest
from shenzhou_client import ShenZhouAPIClient


async def verify_mcp_functionality() -> None:
    """验证MCP核心功能"""
    print("🔧 神州专车MCP功能验证")
    print("=" * 40)
    
    # 显示配置
    print(f"📝 配置信息:")
    print(f"   认证模式: {config.auth.mode.value}")
    print(f"   API主机: {config.api_host}")
    print(f"   Token文件: {config.token_file}")
    print()
    
    # 创建客户端
    client = ShenZhouAPIClient(config)
    
    # 验证认证管理器
    print("🔐 测试认证管理器...")
    try:
        token_info = client.auth_manager.get_token_info()
        if token_info:
            print(f"   ✅ Token存在: {token_info.access_token[:20]}...")
            print(f"   ⏰ 过期时间戳: {token_info.expires_at}")
        else:
            print("   ⚠️  无本地Token")
    except Exception as e:
        print(f"   ❌ 认证失败: {e}")
    
    # 验证数据模型
    print("\n📋 测试数据模型...")
    try:
        # 测试订单请求模型
        order_req = OrderRequest(
            passenger_mobile="13800138000",
            start_lat=39.908692,
            start_lng=116.397477,
            start_name="天安门",
            start_address="北京市东城区天安门广场",
            end_lat=39.918692,
            end_lng=116.407477,
            end_name="王府井",
            end_address="北京市东城区王府井大街"
        )
        print(f"   ✅ 订单模型创建成功: {order_req.passenger_mobile}")
        
        # 测试位置更新模型
        location_req = LocationUpdateRequest(
            order_id="test_order_123",
            latitude=39.928692,
            longitude=116.417477,
            name="新位置",
            address="新地址"
        )
        print(f"   ✅ 位置更新模型创建成功: {location_req.order_id}")
        
    except Exception as e:
        print(f"   ❌ 数据模型测试失败: {e}")
    
    # 验证配置访问
    print("\n⚙️  测试配置访问...")
    try:
        print(f"   客户端ID: {config.client_id}")
        print(f"   重定向URI: {config.redirect_uri}")
        print(f"   认证优先级: {' -> '.join(config.auth.priority or [])}")
        print("   ✅ 配置访问正常")
    except Exception as e:
        print(f"   ❌ 配置访问失败: {e}")
    
    print("\n🎯 MCP功能验证完成")
    print("📄 查看完整文档: cat README.md")
    print("🚀 启动MCP服务器: ./start_http_server.sh")


async def main() -> None:
    """主函数"""
    await verify_mcp_functionality()


if __name__ == "__main__":
    asyncio.run(main())