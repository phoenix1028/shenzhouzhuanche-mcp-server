#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from shenzhou_client import ShenZhouAPIClient
from models import OrderRequest


async def test_fix():
    """测试修复后的功能"""
    print("🔧 测试价格预估和订单创建修复")
    print("=" * 40)
    
    client = ShenZhouAPIClient(config)
    
    # 测试价格预估
    print("💰 测试价格预估...")
    try:
        response = await client.estimate_price(
            service_id=14,
            car_group_id=2,
            start_lat=39.908692,  # 天安门
            start_lng=116.397477,
            end_lat=39.918692,    # 王府井
            end_lng=116.407477
        )
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success" and response.result:
            estimate_id = response.result.get("estimateId")
            prices = response.result.get("prices", [])
            print(f"✅ 获取到estimate_id: {estimate_id}")
            print(f"✅ 价格选项数量: {len(prices)}")
            
            if prices:
                price_info = prices[0]  # 第一个价格选项
                print(f"   车型: {price_info.get('name')}")
                print(f"   价格: {price_info.get('price')}元")
        else:
            print(f"❌ 价格预估失败: {response.error_code}")
            return
            
    except Exception as e:
        print(f"❌ 价格预估异常: {e}")
        return
    
    # 测试订单创建
    print(f"\n🚗 测试订单创建...")
    try:
        order_req = OrderRequest(
            passenger_mobile="13800138000",
            passenger_name="测试用户",
            start_lat=39.908692,
            start_lng=116.397477,
            start_name="天安门",
            start_address="北京市东城区天安门广场",
            end_lat=39.918692,
            end_lng=116.407477,
            end_name="王府井",
            end_address="北京市东城区王府井大街"
        )
        
        response = await client.create_order(order_req)
        print(f"状态: {response.status}")
        print(f"消息: {response.message}")
        
        if response.status == "success":
            print(f"✅ 订单创建成功!")
            print(f"   订单ID: {response.order_id}")
            if response.result:
                print(f"   订单号: {response.result.get('orderNumber')}")
                print(f"   创建状态: {response.result.get('createStatus')}")
        else:
            print(f"❌ 订单创建失败")
            print(f"   错误码: {response.error_code}")
            
    except Exception as e:
        print(f"❌ 订单创建异常: {e}")
    
    print(f"\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_fix())