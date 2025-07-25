#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from config import config
from shenzhou_client import ShenZhouAPIClient
from models import (
    ShenZhouResponse, 
    OrderRequest, 
    LocationUpdateRequest, 
    ConfigInfo
)


# 创建MCP服务器实例
mcp = FastMCP("ShenZhou Car Service")

# 全局API客户端
api_client = ShenZhouAPIClient(config)


@mcp.tool()
async def create_order(
    passenger_mobile: str,
    start_lat: float,
    start_lng: float,
    start_name: str,
    start_address: str,
    end_lat: float,
    end_lng: float,
    end_name: str,
    end_address: str,
    passenger_name: str = "乘客",
    service_id: int = 14,
    car_group_id: int = 2
) -> ShenZhouResponse:
    """创建神州专车订单
    
    Args:
        passenger_mobile: 乘客手机号
        start_lat: 上车地点纬度
        start_lng: 上车地点经度
        start_name: 上车地点名称
        start_address: 上车地点详细地址
        end_lat: 下车地点纬度
        end_lng: 下车地点经度
        end_name: 下车地点名称
        end_address: 下车地点详细地址
        passenger_name: 乘客姓名（默认"乘客"）
        service_id: 服务类型ID（默认14-立即叫车）
        car_group_id: 车型ID（默认2-公务车型）
    
    Returns:
        订单创建结果
    """
    order_req = OrderRequest(
        service_id=service_id,
        car_group_id=car_group_id,
        passenger_mobile=passenger_mobile,
        passenger_name=passenger_name,
        start_lat=start_lat,
        start_lng=start_lng,
        start_name=start_name,
        start_address=start_address,
        end_lat=end_lat,
        end_lng=end_lng,
        end_name=end_name,
        end_address=end_address
    )
    
    return await api_client.create_order(order_req)


@mcp.tool()
async def cancel_order(
    order_id: str,
    force: bool = False,
    reason: str = "用户取消",
    reason_id: int = 1
) -> ShenZhouResponse:
    """取消神州专车订单
    
    Args:
        order_id: 订单ID
        force: 是否强制取消（默认False）
        reason: 取消原因（默认"用户取消"）
        reason_id: 取消原因ID（默认1）
    
    Returns:
        订单取消结果
    """
    return await api_client.cancel_order(order_id, force, reason, reason_id)


@mcp.tool()
async def update_pickup_location(
    order_id: str,
    latitude: float,
    longitude: float,
    name: str,
    address: str
) -> ShenZhouResponse:
    """修改上车地点
    
    Args:
        order_id: 订单ID
        latitude: 新上车地点纬度
        longitude: 新上车地点经度
        name: 新上车地点名称
        address: 新上车地点详细地址
    
    Returns:
        地点修改结果
    """
    update_req = LocationUpdateRequest(
        order_id=order_id,
        latitude=latitude,
        longitude=longitude,
        name=name,
        address=address
    )
    
    return await api_client.update_pickup_location(update_req)


@mcp.tool()
async def update_dropoff_location(
    order_id: str,
    latitude: float,
    longitude: float,
    name: str,
    address: str
) -> ShenZhouResponse:
    """修改下车地点
    
    Args:
        order_id: 订单ID
        latitude: 新下车地点纬度
        longitude: 新下车地点经度
        name: 新下车地点名称
        address: 新下车地点详细地址
    
    Returns:
        地点修改结果
    """
    update_req = LocationUpdateRequest(
        order_id=order_id,
        latitude=latitude,
        longitude=longitude,
        name=name,
        address=address
    )
    
    return await api_client.update_dropoff_location(update_req)


@mcp.tool()
async def get_driver_phone(
    order_id: str,
    ptn_order_id: Optional[str] = None
) -> ShenZhouResponse:
    """获取司机真实电话
    
    Args:
        order_id: 订单ID
        ptn_order_id: 第三方订单ID（可选）
    
    Returns:
        司机电话查询结果
    """
    return await api_client.get_driver_phone(order_id, ptn_order_id)


@mcp.tool()
async def get_city_services() -> ShenZhouResponse:
    """获取城市服务信息
    
    Returns:
        城市服务信息
    """
    return await api_client.get_city_services()


@mcp.tool()
async def estimate_price(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    service_id: int = 14,
    car_group_id: int = 2
) -> ShenZhouResponse:
    """价格预估
    
    Args:
        start_lat: 出发地纬度
        start_lng: 出发地经度
        end_lat: 目的地纬度
        end_lng: 目的地经度
        service_id: 服务类型ID（默认14-立即叫车）
        car_group_id: 车型ID（默认2-公务车型）
    
    Returns:
        价格预估结果
    """
    return await api_client.estimate_price(
        service_id, car_group_id, start_lat, start_lng, end_lat, end_lng
    )


# 添加资源支持
@mcp.resource("shenzhou://config")
async def get_config() -> ConfigInfo:
    """获取神州专车配置信息"""
    return ConfigInfo(
        auth_host=config.auth_host,
        api_host=config.api_host,
        client_id=config.client_id,
        token_file=config.token_file
    )


@mcp.resource("shenzhou://token-status")
async def get_token_status() -> Dict[str, Any]:
    """获取Token状态信息"""
    token_info = api_client.auth_manager.get_token_info()
    
    if token_info:
        status = api_client.auth_manager.token_manager.get_token_status()
        return {
            "status": status,
            "expires_at": token_info.expires_at,
            "created_at": token_info.created_at,
            "has_refresh_token": bool(token_info.refresh_token)
        }
    else:
        return {
            "status": "无Token",
            "message": "请先进行认证"
        }


# Run server with streamable-http transport
if __name__ == "__main__":
    print("🚗 启动神州专车MCP服务器 (HTTP Stream模式)")
    print("\n📋 可用的工具:")
    print("1. create_order - 创建专车订单")
    print("2. cancel_order - 取消专车订单")
    print("3. update_pickup_location - 修改上车地点")
    print("4. update_dropoff_location - 修改下车地点")
    print("5. get_driver_phone - 获取司机真实电话")
    print("6. get_city_services - 获取城市服务信息")
    print("7. estimate_price - 价格预估")
    
    print("\n📦 可用的资源:")
    print("1. shenzhou://config - 获取配置信息")
    print("2. shenzhou://token-status - 获取Token状态")
    
    print(f"\n🔐 认证配置:")
    print(f"   模式: {config.auth.mode.value}")
    print(f"   优先级: {' -> '.join(config.auth.priority)}")
    if config.auth.username:
        print(f"   用户名: {config.auth.username}")
    print(f"   交互模式: {'启用' if config.auth.enable_interactive else '禁用'}")
    
    print("\n🚀 正在启动服务器...")
    
    # 使用streamable-http传输 (推荐的HTTP Stream方式)
    mcp.run(transport="streamable-http")