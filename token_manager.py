#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 测试环境配置
CLIENT_ID = "C2BB2BF800001A0A"
CLIENT_SECRET = "ktvj3lw2u45sswicg9jp"
AUTH_HOST = "https://sandboxoauth.10101111.com"


class TokenManager:
    """令牌管理器"""
    
    def __init__(self, token_file: str = "shenzhou_tokens.json") -> None:
        self.token_file = token_file
        self.tokens = self.load_tokens()
    
    def load_tokens(self) -> Dict[str, Any]:
        """从文件加载令牌"""
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                tokens: Dict[str, Any] = json.load(f)
                return tokens
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"加载令牌文件失败: {e}")
            return {}
    
    def save_tokens(self) -> None:
        """保存令牌到文件"""
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
            print(f"令牌已保存到 {self.token_file}")
        except Exception as e:
            print(f"保存令牌文件失败: {e}")
    
    def set_tokens(self, access_token: str, refresh_token: Optional[str], expires_in: int) -> None:
        """设置令牌信息"""
        now = time.time()
        self.tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "expires_at": now + expires_in,  # 过期时间戳
            "created_at": now,
            "updated_at": now
        }
        self.save_tokens()
        
        # 打印令牌信息
        expire_time = datetime.fromtimestamp(self.tokens["expires_at"])
        print(f"✅ 令牌信息已更新:")
        print(f"   访问令牌: {access_token[:20]}...")
        refresh_display = refresh_token[:20] + "..." if refresh_token else "None"
        print(f"   刷新令牌: {refresh_display}")
        print(f"   有效期: {expires_in}秒 ({expires_in/3600:.1f}小时)")
        print(f"   过期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_valid_access_token(self) -> Optional[str]:
        """获取有效的访问令牌（自动刷新）"""
        if not self.tokens:
            print("❌ 没有令牌信息，请先进行授权")
            return None
        
        now = time.time()
        expires_at = self.tokens.get("expires_at", 0)
        
        # 检查是否即将过期（提前5分钟刷新）
        if now >= (expires_at - 300):
            print("🔄 访问令牌即将过期，尝试刷新...")
            if self.refresh_access_token():
                return self.tokens["access_token"]
            else:
                print("❌ 刷新令牌失败，请重新授权")
                return None
        else:
            remaining = expires_at - now
            print(f"✅ 访问令牌有效，剩余时间: {remaining/3600:.1f}小时")
            access_token: str = self.tokens["access_token"]
            return access_token
    
    def refresh_access_token(self) -> bool:
        """刷新访问令牌"""
        if not self.tokens.get("refresh_token"):
            print("❌ 没有刷新令牌")
            return False
        
        url = f"{AUTH_HOST}/oauth/token"
        params = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.tokens["refresh_token"]
        }
        
        try:
            response = requests.post(url, params=params)
            result = response.json()
            print(f"刷新令牌结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if "access_token" in result:
                # 更新令牌信息
                access_token = result["access_token"]
                refresh_token = result.get("refresh_token", self.tokens["refresh_token"])  # 有些实现不返回新的refresh_token
                expires_in = result.get("expires_in", 43200)  # 默认12小时
                
                self.set_tokens(access_token, refresh_token, expires_in)
                print("✅ 令牌刷新成功")
                return True
            else:
                print(f"❌ 刷新令牌失败: {result.get('error_description', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 刷新令牌异常: {e}")
            return False
    
    def get_token_status(self) -> str:
        """获取令牌状态"""
        if not self.tokens:
            return "无令牌"
        
        now = time.time()
        expires_at = self.tokens.get("expires_at", 0)
        created_at = self.tokens.get("created_at", 0)
        
        if now >= expires_at:
            return "已过期"
        elif now >= (expires_at - 300):  # 5分钟内过期
            return "即将过期"
        else:
            remaining_hours = (expires_at - now) / 3600
            created_time = datetime.fromtimestamp(created_at).strftime('%m-%d %H:%M')
            return f"有效 (剩余{remaining_hours:.1f}h, 创建于{created_time})"


def demo_token_usage() -> None:
    """演示令牌使用"""
    print("=== 神州专车令牌管理演示 ===\n")
    
    manager = TokenManager()
    
    # 显示当前令牌状态
    status = manager.get_token_status()
    print(f"当前令牌状态: {status}\n")
    
    # 尝试获取有效的访问令牌
    access_token = manager.get_valid_access_token()
    
    if access_token:
        print(f"\n✅ 获得有效访问令牌: {access_token[:30]}...")
        
        # 可以用这个token调用API了
        print("\n💡 现在可以用这个token调用神州专车API")
        print("例如: python3 simple_oauth_test.py --token", access_token[:20] + "...")
        
    else:
        print("\n❌ 无法获取有效令牌，需要重新授权")
        print("请运行: python3 simple_oauth_test.py")


def save_tokens_from_oauth(access_token: str, refresh_token: str, expires_in: int) -> None:
    """从OAuth授权结果保存令牌"""
    manager = TokenManager()
    manager.set_tokens(access_token, refresh_token, expires_in)
    print("令牌已保存，下次可以直接使用而无需重新授权")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--save":
        # 手动保存令牌（用于测试）
        if len(sys.argv) >= 5:
            access_token = sys.argv[2]
            refresh_token = sys.argv[3]
            expires_in = int(sys.argv[4])
            save_tokens_from_oauth(access_token, refresh_token, expires_in)
        else:
            print("用法: python3 token_manager.py --save <access_token> <refresh_token> <expires_in>")
    else:
        demo_token_usage()