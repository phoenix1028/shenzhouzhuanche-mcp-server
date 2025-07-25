#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional

# 添加当前目录到路径，以便导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, AuthMode
from shenzhou_client import ShenZhouAPIClient
from models import OrderRequest, LocationUpdateRequest


async def test_auth_manager() -> None:
    """测试认证管理器"""
    print("=== 测试认证管理器 ===")
    
    client = ShenZhouAPIClient(config)
    
    try:
        # 尝试获取token
        token = await client.auth_manager.get_valid_token()
        print(f"✅ 成功获取token: {token[:20]}...")
        
        # 获取token信息
        token_info = client.auth_manager.get_token_info()
        if token_info:
            print(f"   过期时间: {token_info.expires_at}")
            print(f"   创建时间: {token_info.created_at}")
            print(f"   有效期: {token_info.expires_in}秒")
        
    except Exception as e:
        print(f"❌ 认证失败: {e}")


async def test_city_services() -> None:
    """测试获取城市服务"""
    print("\n=== 测试获取城市服务 ===")
    
    client = ShenZhouAPIClient(config)
    
    try:
        response = await client.get_city_services()
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success" and response.result:
            # 打印部分城市信息
            cities = response.result.get("cityServiceMap", {})
            print(f"支持城市数量: {len(cities)}")
            
            # 显示前3个城市
            for i, (city_name, city_info) in enumerate(cities.items()):
                if i >= 3:
                    break
                print(f"  城市: {city_name}")
                services = city_info.get("services", [])
                print(f"    服务数量: {len(services)}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_price_estimate() -> None:
    """测试价格预估"""
    print("\n=== 测试价格预估 ===")
    
    client = ShenZhouAPIClient(config)
    
    # 北京测试坐标：天安门 -> 王府井
    start_lat, start_lng = 39.908692, 116.397477
    end_lat, end_lng = 39.918692, 116.407477
    
    try:
        response = await client.estimate_price(
            service_id=14,  # 立即叫车
            car_group_id=2,  # 公务车型
            start_lat=start_lat,
            start_lng=start_lng,
            end_lat=end_lat,
            end_lng=end_lng
        )
        
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success" and response.result:
            estimate_id = response.result.get("estimateId")
            price = response.result.get("price")
            distance = response.result.get("distance")
            
            print(f"  预估ID: {estimate_id}")
            print(f"  预估价格: {price}元")
            print(f"  预估距离: {distance}公里")
        else:
            print(f"  错误代码: {response.error_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_create_order() -> Optional[str]:
    """测试创建订单（需要有效的认证）"""
    print("\n=== 测试创建订单 ===")
    
    client = ShenZhouAPIClient(config)
    
    # 测试订单数据
    order_req = OrderRequest(
        service_id=14,  # 立即叫车
        car_group_id=2,  # 公务车型
        passenger_mobile="13800138000",  # 测试手机号
        passenger_name="测试用户",
        start_lat=39.908692,  # 天安门
        start_lng=116.397477,
        start_name="天安门",
        start_address="北京市东城区天安门广场",
        end_lat=39.918692,  # 王府井
        end_lng=116.407477,
        end_name="王府井",
        end_address="北京市东城区王府井大街"
    )
    
    try:
        response = await client.create_order(order_req)
        
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success":
            print(f"  订单ID: {response.order_id}")
            if response.result:
                order_number = response.result.get("orderNumber")
                create_status = response.result.get("createStatus")
                print(f"  订单号: {order_number}")
                print(f"  创建状态: {create_status}")
                
        # 返回订单ID供后续测试使用
        return response.order_id if response.status == "success" else None
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None


async def test_driver_phone(order_id: str) -> None:
    """测试获取司机电话"""
    if not order_id:
        print("\n⚠️  跳过司机电话测试（没有有效订单ID）")
        return
        
    print(f"\n=== 测试获取司机电话 (订单: {order_id}) ===")
    
    client = ShenZhouAPIClient(config)
    
    try:
        response = await client.get_driver_phone(order_id)
        
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success":
            print(f"  司机电话: {response.driver_phone}")
            if response.result:
                driver_name = response.result.get("driverSalutation")
                print(f"  司机称呼: {driver_name}")
        else:
            print(f"  错误代码: {response.error_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_cancel_order(order_id: str) -> None:
    """测试取消订单"""
    if not order_id:
        print("\n⚠️  跳过取消订单测试（没有有效订单ID）")
        return
        
    print(f"\n=== 测试取消订单 (订单: {order_id}) ===")
    
    client = ShenZhouAPIClient(config)
    
    try:
        response = await client.cancel_order(
            order_id=order_id,
            force=True,  # 强制取消
            reason="测试取消",
            reason_id=1
        )
        
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success":
            print("  ✅ 订单取消成功")
        else:
            print(f"  错误代码: {response.error_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def main() -> None:
    """主测试函数"""
    print("🚗 神州专车MCP服务器测试套件")
    print("=" * 50)
    
    # 显示配置信息
    print(f"认证模式: {config.auth.mode.value}")
    print(f"认证优先级: {' -> '.join(config.auth.priority)}")
    print(f"API服务器: {config.api_host}")
    print(f"认证服务器: {config.auth_host}")
    
    # 测试序列
    await test_auth_manager()
    await test_city_services()
    await test_price_estimate()
    
    # 如果有密码配置，尝试创建订单相关测试
    if config.auth.username and config.auth.password:
        print(f"\n🔐 检测到密码认证配置，将测试完整订单流程...")
        order_id = await test_create_order()
        
        if order_id:
            # 等待一下再测试司机电话
            await asyncio.sleep(2)
            await test_driver_phone(order_id)
            
            # 等待一下再取消订单
            await asyncio.sleep(2)
            await test_cancel_order(order_id)
    else:
        print(f"\n⚠️  未配置密码认证，跳过订单创建测试")
        print("    如需测试完整功能，请设置环境变量:")
        print("    export SHENZHOU_USERNAME='your_username'")
        print("    export SHENZHOU_PASSWORD='your_password'")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())