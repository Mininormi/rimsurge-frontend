"""
验证码管理（Redis DB 10）
"""
import random
import redis
import hashlib
from typing import Optional
from app.config import settings


class VerificationCodeRedisClient:
    """验证码 Redis 客户端（使用 DB 10）"""
    
    def __init__(self):
        # 如果密码为空字符串或 None，则不传递 password 参数
        redis_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": 10,  # 验证码专用数据库
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
        # 只有当密码存在且非空时才添加 password 参数
        if settings.REDIS_PASSWORD:
            redis_kwargs["password"] = settings.REDIS_PASSWORD
        
        self.client = redis.Redis(**redis_kwargs)
    
    def generate_code(self) -> str:
        """
        生成 6 位数字验证码
        
        Returns:
            6位数字字符串
        """
        return str(random.randint(100000, 999999))
    
    def _hash_code(self, code: str) -> str:
        """
        对验证码进行哈希（SHA256(code + server_pepper)）
        
        Args:
            code: 明文验证码
        
        Returns:
            哈希后的验证码
        """
        pepper = getattr(settings, 'VERIFICATION_CODE_PEPPER', 'RimSurge_Verification_Code_Pepper_2024')
        return hashlib.sha256((code + pepper).encode()).hexdigest()
    
    def set_code(self, email: str, code: str, scene: str = "register", expire_seconds: Optional[int] = None) -> bool:
        """
        存储验证码到 Redis（按场景分离，哈希存储）
        
        Args:
            email: 邮箱地址
            code: 验证码（明文，存储时会哈希）
            scene: 场景（register/reset）
            expire_seconds: 过期时间（秒），默认使用配置值
        
        Returns:
            是否成功
        """
        if expire_seconds is None:
            expire_seconds = settings.VERIFICATION_CODE_EXPIRE_SECONDS
        
        try:
            key = f"verification_code:{email}:{scene}"
            # 存储哈希后的验证码
            hashed_code = self._hash_code(code)
            self.client.setex(key, expire_seconds, hashed_code)
            return True
        except Exception:
            return False
    
    def get_code_hash(self, email: str, scene: str = "register") -> Optional[str]:
        """
        获取验证码哈希值（按场景分离）
        
        Args:
            email: 邮箱地址
            scene: 场景（register/reset）
        
        Returns:
            验证码哈希值，如果不存在或已过期则返回 None
        """
        try:
            key = f"verification_code:{email}:{scene}"
            hashed_code = self.client.get(key)
            return hashed_code
        except Exception:
            return None
    
    def verify_code(self, email: str, code: str, scene: str = "register") -> tuple[bool, Optional[str]]:
        """
        验证验证码（按场景分离，哈希比对）
        
        Args:
            email: 邮箱地址
            code: 用户输入的验证码（明文）
            scene: 场景（register/reset）
        
        Returns:
            (是否验证成功, 错误消息)
        """
        # 获取存储的哈希值
        stored_hash = self.get_code_hash(email, scene)
        if not stored_hash:
            return False, "验证码不存在或已过期"
        
        # 对用户输入的验证码进行哈希
        input_hash = self._hash_code(code)
        
        # 验证成功后删除验证码（一次性使用）
        if stored_hash == input_hash:
            self.delete_code(email, scene)
            # 清除验证失败计数
            self._clear_verify_failures(email, scene)
            return True, None
        
        # 验证码错误，记录失败次数
        return False, "验证码错误"
    
    def delete_code(self, email: str, scene: str = "register") -> bool:
        """
        删除验证码（按场景分离）
        
        Args:
            email: 邮箱地址
            scene: 场景（register/reset）
        
        Returns:
            是否成功
        """
        try:
            key = f"verification_code:{email}:{scene}"
            self.client.delete(key)
            return True
        except Exception:
            return False
    
    def check_email_exists_cache(self, email: str) -> Optional[bool]:
        """
        检查邮箱是否存在（带缓存）
        
        Args:
            email: 邮箱地址
        
        Returns:
            None: 缓存不存在，需要查询数据库
            True: 邮箱已存在（缓存）
            False: 邮箱不存在（缓存）
        """
        try:
            cache_key = f"email_exists:{email}"
            cached = self.client.get(cache_key)
            if cached is not None:
                return cached == "1"
            return None
        except Exception:
            return None
    
    def set_email_exists_cache(self, email: str, exists: bool, ttl: int = 10800) -> bool:
        """
        设置邮箱存在状态缓存（TTL 3小时）
        
        Args:
            email: 邮箱地址
            exists: 是否存在
            ttl: 缓存时间（秒），默认3小时
        
        Returns:
            是否成功
        """
        try:
            cache_key = f"email_exists:{email}"
            value = "1" if exists else "0"
            self.client.setex(cache_key, ttl, value)
            return True
        except Exception:
            return False
    
    def check_cooldown(self, email: str, ip: str, scene: str = "register") -> tuple[bool, Optional[int]]:
        """
        检查1分钟冷却时间（使用 Redis 原子锁防止并发，按场景分离）
        
        使用 SET cooldown:email:<email>:<scene> 1 NX EX 60 原子操作
        成功才允许发码，失败直接拒绝
        
        Args:
            email: 邮箱地址
            ip: IP 地址
            scene: 场景（register/reset）
        
        Returns:
            (是否可以发送, 剩余秒数)
        """
        cooldown_seconds = 60
        email_cooldown_key = f"cooldown:email:{email}:{scene}"
        ip_cooldown_key = f"cooldown:ip:{ip}:{scene}"
        try:
            # 原子化：两个 key 要么都成功 set，要么都不 set（避免“邮箱锁成功但 IP 锁失败”的误伤）
            lua = """
            if (redis.call('exists', KEYS[1]) == 1) or (redis.call('exists', KEYS[2]) == 1) then
              return 0
            end
            redis.call('set', KEYS[1], '1', 'EX', ARGV[1])
            redis.call('set', KEYS[2], '1', 'EX', ARGV[1])
            return 1
            """
            ok = self.client.eval(lua, 2, email_cooldown_key, ip_cooldown_key, str(cooldown_seconds))
            if ok == 1:
                return True, None
            # 冷却中：返回剩余秒数（内部用；上层 send-verification-code 已不向外透出真实值）
            ttl1 = self.client.ttl(email_cooldown_key)
            ttl2 = self.client.ttl(ip_cooldown_key)
            remaining = max(ttl1 if ttl1 > 0 else 0, ttl2 if ttl2 > 0 else 0) or cooldown_seconds
            return False, remaining
        except Exception:
            # Redis 出错：安全优先，拒绝发送
            return False, cooldown_seconds
    
    def record_send_attempt(self, email: str, ip: str, scene: str = "register") -> tuple[bool, Optional[int]]:
        """
        记录发送尝试，检查是否需要 ban（按场景分离）
        
        规则：
        - 10 分钟窗口内连续发送 6 次 → ban 3 小时
        - 同 IP 不同邮箱：检查 Set 基数（SCARD）是否 > 1 才触发 ban
        - 同邮箱不同 IP：检查 Set 基数（SCARD）是否 > 1 才触发 ban
        
        Args:
            email: 邮箱地址
            ip: IP 地址
            scene: 场景（register/reset）
        
        Returns:
            (是否允许发送, ban剩余秒数)
        """
        try:
            # 检查是否已被 ban（按场景分离）
            email_ban_key = f"verification_ban_email:{email}:{scene}"
            ip_ban_key = f"verification_ban_ip:{ip}:{scene}"
            
            email_ban_ttl = self.client.ttl(email_ban_key)
            ip_ban_ttl = self.client.ttl(ip_ban_key)
            
            # 如果已被 ban，返回剩余时间
            if email_ban_ttl > 0:
                return False, email_ban_ttl
            if ip_ban_ttl > 0:
                return False, ip_ban_ttl
            
            ban_seconds = 10800  # 3小时
            window_seconds = 600  # 10分钟窗口
            
            # 1. 检查同 IP 不同邮箱的发送次数（10分钟窗口，按场景分离）
            # 使用 Set 记录该 IP 发送过的邮箱列表
            ip_emails_set_key = f"set:ip:{ip}:emails:{scene}"
            # 添加邮箱到 Set（如果不存在则添加）
            self.client.sadd(ip_emails_set_key, email)
            self.client.expire(ip_emails_set_key, window_seconds)  # 10分钟窗口
            
            # 使用计数器记录该 IP 的发送次数（10分钟窗口，按场景分离）
            ip_count_key = f"count:ip:{ip}:{scene}"
            ip_count = self.client.incr(ip_count_key)
            if ip_count == 1:
                # 第一次设置，需要设置过期时间
                self.client.expire(ip_count_key, window_seconds)
            
            # 获取该 IP 发送的不同邮箱数量（Set 基数）
            ip_email_set_size = self.client.scard(ip_emails_set_key)
            
            # 只有当计数 >= 6 且 Set 基数 > 1（确实有不同邮箱）时才 ban
            if ip_count >= 6 and ip_email_set_size > 1:
                self.client.setex(ip_ban_key, ban_seconds, "1")
                # 清除计数和 Set
                self.client.delete(ip_count_key)
                self.client.delete(ip_emails_set_key)
                return False, ban_seconds
            
            # 2. 检查同邮箱不同 IP 的发送次数（10分钟窗口，按场景分离）
            # 使用 Set 记录该邮箱被哪些 IP 发送过
            email_ips_set_key = f"set:email:{email}:ips:{scene}"
            # 添加 IP 到 Set（如果不存在则添加）
            self.client.sadd(email_ips_set_key, ip)
            self.client.expire(email_ips_set_key, window_seconds)  # 10分钟窗口
            
            # 使用计数器记录该邮箱的发送次数（10分钟窗口，按场景分离）
            email_count_key = f"count:email:{email}:{scene}"
            email_count = self.client.incr(email_count_key)
            if email_count == 1:
                # 第一次设置，需要设置过期时间
                self.client.expire(email_count_key, window_seconds)
            
            # 获取该邮箱被不同 IP 发送的次数（Set 基数）
            email_ip_set_size = self.client.scard(email_ips_set_key)
            
            # 只有当计数 >= 6 且 Set 基数 > 1（确实有不同 IP）时才 ban
            if email_count >= 6 and email_ip_set_size > 1:
                self.client.setex(email_ban_key, ban_seconds, "1")
                # 清除计数和 Set
                self.client.delete(email_count_key)
                self.client.delete(email_ips_set_key)
                return False, ban_seconds
            
            return True, None
        except Exception:
            # Redis 出错时拒绝发送（安全优先）
            return False, ban_seconds if 'ban_seconds' in locals() else 10800
    
    def _clear_verify_failures(self, email: str, scene: str = "register") -> None:
        """清除验证失败计数（按场景分离）"""
        try:
            failure_key = f"verification_failures:{email}:{scene}"
            self.client.delete(failure_key)
        except Exception:
            pass
    
    def record_verify_failure(self, email: str, scene: str = "register") -> tuple[bool, int]:
        """
        记录验证失败次数（10分钟窗口，按场景分离）
        
        Args:
            email: 邮箱地址
            scene: 场景（register/reset）
        
        Returns:
            (是否允许继续验证, 当前失败次数)
        """
        try:
            window_seconds = 600  # 10分钟窗口
            failure_key = f"verification_failures:{email}:{scene}"
            failure_count = self.client.incr(failure_key)
            # 如果是第一次设置，需要设置过期时间
            if failure_count == 1:
                self.client.expire(failure_key, window_seconds)
            
            # 如果失败6次，删除验证码
            if failure_count >= 6:
                self.delete_code(email, scene)
                return False, failure_count
            
            return True, failure_count
        except Exception:
            # Redis 出错时允许继续验证
            return True, 0
    
    def check_rate_limit(self, email: str) -> bool:
        """
        检查发送频率限制（邮箱维度）- 保留兼容性
        
        Args:
            email: 邮箱地址
        
        Returns:
            True 表示可以发送，False 表示需要等待
        """
        # 如果限流被禁用，直接返回 True（用于测试）
        rate_limit_enabled = getattr(settings, 'VERIFICATION_CODE_RATE_LIMIT_ENABLED', True)
        if isinstance(rate_limit_enabled, str):
            rate_limit_enabled = rate_limit_enabled.lower() in ('true', '1', 'yes', 'on')
        if not rate_limit_enabled:
            return True
        
        try:
            rate_limit_key = f"verification_code_rate:{email}"
            exists = self.client.exists(rate_limit_key)
            
            if exists:
                return False
            
            rate_limit_seconds = settings.VERIFICATION_CODE_RATE_LIMIT_SECONDS
            self.client.setex(rate_limit_key, rate_limit_seconds, "1")
            return True
        except Exception:
            return True
    
    def check_ip_rate_limit(self, ip: str) -> bool:
        """
        检查 IP 维度的发送频率限制 - 保留兼容性
        
        Args:
            ip: IP 地址
        
        Returns:
            True 表示可以发送，False 表示需要等待
        """
        rate_limit_enabled = getattr(settings, 'VERIFICATION_CODE_RATE_LIMIT_ENABLED', True)
        if isinstance(rate_limit_enabled, str):
            rate_limit_enabled = rate_limit_enabled.lower() in ('true', '1', 'yes', 'on')
        if not rate_limit_enabled:
            return True
        
        try:
            rate_limit_key = f"verification_code_rate_ip:{ip}"
            exists = self.client.exists(rate_limit_key)
            
            if exists:
                return False
            
            rate_limit_seconds = settings.VERIFICATION_CODE_RATE_LIMIT_SECONDS
            self.client.setex(rate_limit_key, rate_limit_seconds, "1")
            return True
        except Exception:
            return True


# 全局验证码 Redis 客户端实例
verification_code_client = VerificationCodeRedisClient()
