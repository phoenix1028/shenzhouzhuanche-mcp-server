#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class AuthMode(Enum):
    """认证模式枚举"""
    AUTO = "auto"
    PASSWORD = "password" 
    OAUTH = "oauth"


@dataclass
class AuthConfig:
    """认证配置"""
    mode: AuthMode = AuthMode.AUTO
    username: Optional[str] = None
    password: Optional[str] = None
    enable_interactive: bool = False
    
    # 认证优先级：已保存token -> 密码模式 -> 授权码模式
    priority: Optional[List[str]] = None
    
    def __post_init__(self) -> None:
        if self.priority is None:
            if self.mode == AuthMode.AUTO:
                # 自动模式：优先使用密码模式（如果配置了）
                if self.username and self.password:
                    self.priority = ["saved_token", "password_mode", "authorization_code"]
                else:
                    self.priority = ["saved_token", "authorization_code"]
            elif self.mode == AuthMode.PASSWORD:
                self.priority = ["saved_token", "password_mode"]
            elif self.mode == AuthMode.OAUTH:
                self.priority = ["saved_token", "authorization_code"]


@dataclass 
class ShenZhouConfig:
    """神州专车API配置"""
    # 测试环境配置
    client_id: str = "你的客户端ID"
    client_secret: str = "你的客户端密钥"
    redirect_uri: str = "https://www.baidu.com"
    
    # 服务端点
    auth_host: str = "https://sandboxoauth.10101111.com"
    api_host: str = "https://sandboxapi.10101111.com"
    
    # Token管理
    token_file: str = "shenzhou_tokens.json"
    
    # 认证配置
    auth: Optional[AuthConfig] = None
    
    def __post_init__(self) -> None:
        if self.auth is None:
            # 从环境变量读取认证配置，如果没有则使用测试账号
            username = os.getenv("SHENZHOU_USERNAME", "你的测试账号")  # 测试账号
            password = os.getenv("SHENZHOU_PASSWORD", "你爹测试密码")  # 测试密码
            enable_interactive = os.getenv("SHENZHOU_INTERACTIVE", "false").lower() == "true"
            
            self.auth = AuthConfig(
                username=username,
                password=password,
                enable_interactive=enable_interactive
            )


# 全局配置实例
config = ShenZhouConfig()
# 确保auth配置不为空
if config.auth is None:
    config.auth = AuthConfig()
