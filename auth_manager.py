#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import time
from typing import Optional, Dict, Any
import aiohttp
import requests

from config import ShenZhouConfig, AuthMode
from token_manager import TokenManager
from models import TokenInfo


class AuthenticationError(Exception):
    """认证异常"""
    pass


class ShenZhouAuthManager:
    """神州专车认证管理器"""
    
    def __init__(self, config: ShenZhouConfig) -> None:
        self.config = config
        self.token_manager = TokenManager(config.token_file)
    
    async def get_valid_token(self) -> str:
        """获取有效token - 按优先级尝试各种认证方式"""
        
        for auth_method in self.config.auth.priority:
            try:
                if auth_method == "saved_token":
                    token = self._get_saved_token()
                    if token:
                        return token
                        
                elif auth_method == "password_mode":
                    if self._has_password_config():
                        token = await self._auth_by_password()
                        if token:
                            return token
                            
                elif auth_method == "authorization_code":
                    if self.config.auth.enable_interactive:
                        token = await self._auth_by_code()
                        if token:
                            return token
                            
            except Exception as e:
                print(f"认证方式 {auth_method} 失败: {e}")
                continue
        
        raise AuthenticationError("所有认证方式都失败")
    
    def _get_saved_token(self) -> Optional[str]:
        """获取已保存的有效token"""
        try:
            return self.token_manager.get_valid_access_token()
        except Exception:
            return None
    
    def _has_password_config(self) -> bool:
        """检查是否配置了密码认证"""
        return bool(self.config.auth.username and self.config.auth.password)
    
    async def _auth_by_password(self) -> Optional[str]:
        """密码模式认证"""
        if not self._has_password_config():
            return None
            
        url = f"{self.config.auth_host}/oauth/token"
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "password",
            "username": self.config.auth.username,
            "password": self.config.auth.password
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    result = await response.json()
                    
            if "access_token" in result:
                # 保存token
                access_token = result["access_token"]
                refresh_token = result.get("refresh_token")
                expires_in = result.get("expires_in", 43200)
                
                self.token_manager.set_tokens(access_token, refresh_token, expires_in)
                return access_token
            else:
                print(f"密码模式认证失败: {result.get('error_description', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"密码模式认证异常: {e}")
            return None
    
    async def _auth_by_code(self) -> Optional[str]:
        """授权码模式认证 - 交互式"""
        if not self.config.auth.enable_interactive:
            return None
            
        # 生成授权URL
        auth_url = self._generate_auth_url()
        print(f"请打开以下URL完成授权: {auth_url}")
        
        # 等待用户输入授权码
        try:
            code = input("请输入授权码: ").strip()
            if not code:
                return None
                
            return await self._get_token_by_code(code)
            
        except (KeyboardInterrupt, EOFError):
            print("用户取消授权")
            return None
    
    def _generate_auth_url(self) -> str:
        """生成授权URL"""
        from urllib.parse import urlencode
        
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": "read"
        }
        
        return f"{self.config.auth_host}/oauth/authorize?{urlencode(params)}"
    
    async def _get_token_by_code(self, code: str) -> Optional[str]:
        """通过授权码获取token"""
        url = f"{self.config.auth_host}/oauth/token"
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    result = await response.json()
                    
            if "access_token" in result:
                # 保存token
                access_token = result["access_token"]
                refresh_token = result.get("refresh_token")
                expires_in = result.get("expires_in", 43200)
                
                self.token_manager.set_tokens(access_token, refresh_token, expires_in)
                return access_token
            else:
                print(f"授权码认证失败: {result.get('error_description', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"授权码认证异常: {e}")
            return None
    
    def get_token_info(self) -> Optional[TokenInfo]:
        """获取token信息"""
        try:
            tokens = self.token_manager.load_tokens()
            if not tokens:
                return None
                
            return TokenInfo(
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                expires_in=tokens["expires_in"],
                expires_at=tokens["expires_at"],
                created_at=tokens["created_at"],
                updated_at=tokens["updated_at"]
            )
        except Exception:
            return None