"""
验证码管理（Redis DB 10）
"""
import random
import redis
from typing import Optional
from app.config import settings


class VerificationCodeRedisClient:
    """验证码 Redis 客户端（使用 DB 10）"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=10,  # 验证码专用数据库
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    
    def generate_code(self) -> str:
        """
        生成 6 位数字验证码
        
        Returns:
            6位数字字符串
        """
        return str(random.randint(100000, 999999))
    
    def set_code(self, email: str, code: str, expire_seconds: Optional[int] = None) -> bool:
        """
        存储验证码到 Redis
        
        Args:
            email: 邮箱地址
            code: 验证码
            expire_seconds: 过期时间（秒），默认使用配置值
        
        Returns:
            是否成功
        """
        if expire_seconds is None:
            expire_seconds = settings.VERIFICATION_CODE_EXPIRE_SECONDS
        
        try:
            key = f"verification_code:{email}"
            self.client.setex(key, expire_seconds, code)
            return True
        except Exception:
            return False
    
    def get_code(self, email: str) -> Optional[str]:
        """
        获取验证码
        
        Args:
            email: 邮箱地址
        
        Returns:
            验证码字符串，如果不存在或已过期则返回 None
        """
        try:
            key = f"verification_code:{email}"
            code = self.client.get(key)
            return code
        except Exception:
            return None
    
    def verify_code(self, email: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            email: 邮箱地址
            code: 用户输入的验证码
        
        Returns:
            是否验证成功
        """
        stored_code = self.get_code(email)
        if not stored_code:
            return False
        
        # 验证成功后删除验证码（一次性使用）
        if stored_code == code:
            self.delete_code(email)
            return True
        
        return False
    
    def delete_code(self, email: str) -> bool:
        """
        删除验证码
        
        Args:
            email: 邮箱地址
        
        Returns:
            是否成功
        """
        try:
            key = f"verification_code:{email}"
            self.client.delete(key)
            return True
        except Exception:
            return False
    
    def check_rate_limit(self, email: str) -> bool:
        """
        检查发送频率限制（邮箱维度）
        
        Args:
            email: 邮箱地址
        
        Returns:
            True 表示可以发送，False 表示需要等待
        """
        try:
            rate_limit_key = f"verification_code_rate:{email}"
            exists = self.client.exists(rate_limit_key)
            
            if exists:
                # 还在限制期内，不能发送
                return False
            
            # 设置频率限制标记（120秒）
            rate_limit_seconds = settings.VERIFICATION_CODE_RATE_LIMIT_SECONDS
            self.client.setex(rate_limit_key, rate_limit_seconds, "1")
            return True
        except Exception:
            # 如果 Redis 出错，允许发送（避免阻塞）
            return True
    
    def check_ip_rate_limit(self, ip: str) -> bool:
        """
        检查 IP 维度的发送频率限制
        
        Args:
            ip: IP 地址
        
        Returns:
            True 表示可以发送，False 表示需要等待
        """
        try:
            rate_limit_key = f"verification_code_rate_ip:{ip}"
            exists = self.client.exists(rate_limit_key)
            
            if exists:
                # 还在限制期内，不能发送
                return False
            
            # 设置频率限制标记（120秒）
            rate_limit_seconds = settings.VERIFICATION_CODE_RATE_LIMIT_SECONDS
            self.client.setex(rate_limit_key, rate_limit_seconds, "1")
            return True
        except Exception:
            # 如果 Redis 出错，允许发送（避免阻塞）
            return True


# 全局验证码 Redis 客户端实例
verification_code_client = VerificationCodeRedisClient()
