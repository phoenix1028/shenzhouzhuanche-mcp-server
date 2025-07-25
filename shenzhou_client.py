#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, Any, Optional
import aiohttp

from config import ShenZhouConfig
from auth_manager import ShenZhouAuthManager
from models import OrderRequest, LocationUpdateRequest, ShenZhouResponse


class ShenZhouAPIClient:
    """神州专车API客户端"""
    
    def __init__(self, config: ShenZhouConfig) -> None:
        self.config = config
        self.auth_manager = ShenZhouAuthManager(config)
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        return await self.auth_manager.get_valid_token()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发起HTTP请求"""
        url = f"{self.config.api_host}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, params=params) as response:
                        # 检查响应状态和内容类型
                        if response.status != 200:
                            text = await response.text()
                            raise Exception(f"HTTP {response.status}: {text}")
                        
                        # 尝试解析JSON，不管content-type如何
                        try:
                            get_result: Dict[str, Any] = await response.json()
                            return get_result
                        except Exception:
                            # 如果json()失败，尝试手动解析
                            text = await response.text()
                            try:
                                import json
                                get_result = json.loads(text)
                                return get_result
                            except json.JSONDecodeError:
                                content_type = response.headers.get('content-type', '')
                                raise Exception(f"JSON解析失败 (content-type: {content_type}): {text[:200]}...")
                elif method.upper() == "POST":
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json'
                    }
                    async with session.post(url, data=data, headers=headers) as response:
                        # 检查响应状态和内容类型
                        if response.status != 200:
                            text = await response.text()
                            raise Exception(f"HTTP {response.status}: {text}")
                        
                        # 尝试解析JSON，不管content-type如何
                        try:
                            post_result: Dict[str, Any] = await response.json()
                            return post_result
                        except Exception:
                            # 如果json()失败，尝试手动解析
                            text = await response.text()
                            try:
                                import json
                                post_result = json.loads(text)
                                return post_result
                            except json.JSONDecodeError:
                                content_type = response.headers.get('content-type', '')
                                raise Exception(f"JSON解析失败 (content-type: {content_type}): {text[:200]}...")
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                    
        except Exception as e:
            raise Exception(f"API请求失败: {e}")
    
    async def get_city_services(self) -> ShenZhouResponse:
        """获取城市服务信息"""
        try:
            access_token = await self._get_access_token()
            params = {"access_token": access_token}
            
            result = await self._make_request(
                "GET", 
                "/v1/resource/common/getCityService", 
                params=params
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message="获取城市服务成功",
                    result=result.get("content")
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "获取城市服务失败"),
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"获取城市服务异常: {e}"
            )
    
    async def estimate_price(
        self, 
        service_id: int, 
        car_group_id: int,
        start_lat: float, 
        start_lng: float,
        end_lat: float, 
        end_lng: float
    ) -> ShenZhouResponse:
        """价格预估"""
        try:
            access_token = await self._get_access_token()
            params = {
                "access_token": access_token,
                "serviceId": service_id,
                "carGroupId": car_group_id,
                "slat": start_lat,
                "slng": start_lng,
                "elat": end_lat,
                "elng": end_lng
            }
            
            result = await self._make_request(
                "GET",
                "/v1/resource/common/estimate/price",
                params=params
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message="价格预估成功",
                    result=result.get("content")
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "价格预估失败"),
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"价格预估异常: {e}"
            )
    
    async def create_order(self, order_req: OrderRequest) -> ShenZhouResponse:
        """创建专车订单"""
        try:
            access_token = await self._get_access_token()
            
            # 先获取estimate_id
            estimate_response = await self.estimate_price(
                order_req.service_id,
                order_req.car_group_id,
                order_req.start_lat,
                order_req.start_lng,
                order_req.end_lat,
                order_req.end_lng
            )
            
            if estimate_response.status != "success":
                return ShenZhouResponse(
                    status="error",
                    message="价格预估失败，无法创建订单"
                )
            
            estimate_id = estimate_response.result.get("estimateId") if estimate_response.result else None
            if not estimate_id:
                return ShenZhouResponse(
                    status="error",
                    message="无法获取estimate_id"
                )
            
            # 创建订单
            data = {
                "access_token": access_token,
                "serviceId": order_req.service_id,
                "carGroupId": order_req.car_group_id,
                "passengerMobile": order_req.passenger_mobile,
                "passengerName": order_req.passenger_name,
                "estimateId": estimate_id,
                "slat": order_req.start_lat,
                "slng": order_req.start_lng,
                "startName": order_req.start_name,
                "startAddress": order_req.start_address,
                "elat": order_req.end_lat,
                "elng": order_req.end_lng,
                "endName": order_req.end_name,
                "endAddress": order_req.end_address
            }
            
            result = await self._make_request(
                "POST",
                "/v1/action/order/create",
                data=data
            )
            
            if result.get("code") == 1:
                content = result.get("content", {})
                order_id = content.get("orderId")
                
                return ShenZhouResponse(
                    status="success",
                    message="订单创建成功",
                    order_id=order_id,
                    result=content
                )
            else:
                # 提供更详细的错误信息
                error_msg = result.get("msg", "订单创建失败")
                busi_code = result.get("busiCode", "")
                
                # 针对常见错误给出友好提示
                if busi_code == "passengerMoreThanThreeOrder":
                    error_msg += " (建议使用其他手机号)"
                elif busi_code == "companyIdError":
                    error_msg += " (企业ID不匹配)"
                
                return ShenZhouResponse(
                    status="error",
                    message=error_msg,
                    error_code=f"{result.get('code')}:{busi_code}"
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"创建订单异常: {e}"
            )
    
    async def cancel_order(
        self, 
        order_id: str, 
        force: bool = False,
        reason: str = "用户取消",
        reason_id: int = 1
    ) -> ShenZhouResponse:
        """取消订单"""
        try:
            access_token = await self._get_access_token()
            
            data = {
                "access_token": access_token,
                "orderId": order_id,
                "force": "true" if force else "false",
                "reason": reason,
                "reasonId": reason_id
            }
            
            result = await self._make_request(
                "POST",
                "/v1/action/order/cancel",
                data=data
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message="订单取消成功",
                    order_id=order_id,
                    result=result.get("content")
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "订单取消失败"),
                    order_id=order_id,
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"取消订单异常: {e}",
                order_id=order_id
            )
    
    async def update_pickup_location(self, update_req: LocationUpdateRequest) -> ShenZhouResponse:
        """修改上车地点"""
        try:
            access_token = await self._get_access_token()
            
            data = {
                "access_token": access_token,
                "orderId": update_req.order_id,
                "slng": update_req.longitude,
                "slat": update_req.latitude,
                "startName": update_req.name,
                "startAddress": update_req.address
            }
            
            result = await self._make_request(
                "POST",
                "/v1/action/order/updateStart",
                data=data
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message="上车地点修改成功",
                    order_id=update_req.order_id,
                    result=result.get("content")
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "上车地点修改失败"),
                    order_id=update_req.order_id,
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"修改上车地点异常: {e}",
                order_id=update_req.order_id
            )
    
    async def update_dropoff_location(self, update_req: LocationUpdateRequest) -> ShenZhouResponse:
        """修改下车地点"""
        try:
            access_token = await self._get_access_token()
            
            data = {
                "access_token": access_token,
                "orderId": update_req.order_id,
                "elng": update_req.longitude,
                "elat": update_req.latitude,
                "endName": update_req.name,
                "endAddress": update_req.address
            }
            
            result = await self._make_request(
                "POST",
                "/v1/action/order/updateEnd",
                data=data
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message="下车地点修改成功",
                    order_id=update_req.order_id,
                    result=result.get("content")
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "下车地点修改失败"),
                    order_id=update_req.order_id,
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"修改下车地点异常: {e}",
                order_id=update_req.order_id
            )
    
    async def get_driver_phone(self, order_id: str, ptn_order_id: Optional[str] = None) -> ShenZhouResponse:
        """获取司机真实电话"""
        try:
            access_token = await self._get_access_token()
            
            params = {
                "access_token": access_token,
                "orderId": order_id
            }
            
            if ptn_order_id:
                params["ptnOrderId"] = ptn_order_id
            
            result = await self._make_request(
                "GET",
                "/v1/resource/queryDriverPhone",
                params=params
            )
            
            if result.get("code") == 1:
                content = result.get("content", {})
                driver_phone = content.get("driverPhone")
                
                return ShenZhouResponse(
                    status="success",
                    message="获取司机电话成功",
                    order_id=order_id,
                    driver_phone=driver_phone,
                    result=content
                )
            else:
                return ShenZhouResponse(
                    status="error",
                    message=result.get("msg", "获取司机电话失败"),
                    order_id=order_id,
                    error_code=str(result.get("code"))
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"获取司机电话异常: {e}",
                order_id=order_id
            )
    
    async def recharge_account(
        self, 
        mobile: str, 
        pay_amount: int = 1000000,  # 默认充值100万分（10000元）
        pay_type: int = 6  # 充值卡
    ) -> ShenZhouResponse:
        """账户充值"""
        try:
            access_token = await self._get_access_token()
            
            data = {
                "access_token": access_token,
                "mobile": mobile,
                "payAmount": pay_amount,
                "payType": pay_type
            }
            
            # 如果是充值卡，添加默认密码
            if pay_type == 6:
                data["rechargePwd"] = "123456"  # 测试充值卡密码
            
            result = await self._make_request(
                "POST",
                "/v1/action/tradingplatform/recharge",
                data=data
            )
            
            if result.get("code") == 1:
                return ShenZhouResponse(
                    status="success",
                    message=f"账户充值成功，金额: {pay_amount/100}元",
                    result=result.get("content")
                )
            else:
                error_msg = result.get("msg", "充值失败")
                busi_code = result.get("busiCode", "")
                
                return ShenZhouResponse(
                    status="error",
                    message=f"充值失败: {error_msg}",
                    error_code=f"{result.get('code')}:{busi_code}"
                )
                
        except Exception as e:
            return ShenZhouResponse(
                status="error",
                message=f"充值异常: {e}"
            )