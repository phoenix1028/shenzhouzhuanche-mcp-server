#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from shenzhou_client import ShenZhouAPIClient
from models import OrderRequest


async def test_chengdu_order():
    """测试成都地区订单创建"""
    client = ShenZhouAPIClient(config)
    
    print("🚗 测试成都地区订单创建...")
    print("=" * 40)
    
    # 使用用户提供的数据
    order_req = OrderRequest(
        passenger_mobile="17376580883",
        passenger_name="陈树",
        start_lat=30.546698,   # 成都天府三街地铁站A口
        start_lng=104.068066,
        start_name="成都天府三街地铁站A口",
        start_address="成都天府三街地铁站A口",
        end_lat=30.574053,     # 成都德商国际c座
        end_lng=104.061066,
        end_name="成都德商国际c座",
        end_address="成都德商国际c座",
        service_id=14,         # 立即叫车
        car_group_id=2         # 公务车型
    )
    
    print(f"乘客: {order_req.passenger_name} ({order_req.passenger_mobile})")
    print(f"起点: {order_req.start_name}")
    print(f"终点: {order_req.end_name}")
    print(f"服务: {order_req.service_id}, 车型: {order_req.car_group_id}")
    print()
    
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


if __name__ == "__main__":
    asyncio.run(test_chengdu_order())