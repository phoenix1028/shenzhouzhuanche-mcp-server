#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ShenZhouResponse(BaseModel):
    """神州专车API统一响应模型"""
    status: str
    message: str
    order_id: Optional[str] = None
    driver_phone: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class OrderRequest(BaseModel):
    """创建订单请求模型"""
    service_id: int = 14  # 立即叫车
    car_group_id: int = 2  # 公务车型
    passenger_mobile: str
    passenger_name: str = "乘客"
    start_lat: float
    start_lng: float
    start_name: str
    start_address: str
    end_lat: float
    end_lng: float
    end_name: str
    end_address: str


class LocationUpdateRequest(BaseModel):
    """位置更新请求模型"""
    order_id: str
    latitude: float
    longitude: float
    name: str
    address: str


class ConfigInfo(BaseModel):
    """配置信息模型"""
    auth_host: str
    api_host: str
    client_id: str
    token_file: str


class TokenInfo(BaseModel):
    """Token信息模型"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    expires_at: float
    created_at: float
    updated_at: float