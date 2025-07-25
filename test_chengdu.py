#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from shenzhou_client import ShenZhouAPIClient


async def test_chengdu_estimate():
    """测试成都地区价格预估"""
    client = ShenZhouAPIClient(config)
    
    print("🌆 测试成都地区价格预估...")
    print("=" * 40)
    
    response = await client.estimate_price(
        service_id=14,
        car_group_id=2,
        start_lat=30.546698,   # 成都天府三街地铁站A口
        start_lng=104.068066,
        end_lat=30.574053,     # 成都德商国际c座
        end_lng=104.061066
    )
    
    print(f"状态: {response.status}")
    print(f"消息: {response.message}")
    print(f"错误码: {response.error_code}")
    
    if response.result:
        print(f"结果: {response.result}")
    else:
        print("无结果数据")
    
    # 测试其他城市服务是否可用
    print(f"\n🏙️ 检查城市服务...")
    city_response = await client.get_city_services()
    print(f"城市服务状态: {city_response.status}")
    print(f"城市服务消息: {city_response.message}")
    
    if city_response.result:
        cities = city_response.result
        print(f"支持的城市数量: {len(cities) if isinstance(cities, list) else '未知'}")
        
        # 查找成都
        chengdu_found = False
        if isinstance(cities, list):
            for city in cities:
                if isinstance(city, dict):
                    city_name = city.get('cityName', '')
                    if '成都' in city_name:
                        print(f"✅ 找到成都: {city}")
                        chengdu_found = True
                        break
        
        if not chengdu_found:
            print("❌ 未找到成都服务")
            print("支持的城市列表:")
            if isinstance(cities, list):
                for i, city in enumerate(cities[:10]):  # 只显示前10个
                    if isinstance(city, dict):
                        print(f"  {i+1}. {city.get('cityName', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_chengdu_estimate())