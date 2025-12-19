"""
地址缓存模块（Cache-Aside 模式）
"""
import json
from typing import Optional, List, Dict, Any
from app.core.usercache_client import usercache_client


class AddressCache:
    """地址缓存管理"""
    
    CACHE_PREFIX = "usercache:addr"
    DEFAULT_TTL = 1800  # 30分钟
    
    @staticmethod
    def _get_version_key(user_id: int) -> str:
        """获取版本号键"""
        return f"{AddressCache.CACHE_PREFIX}:ver:u{user_id}"
    
    @staticmethod
    def _get_list_key(user_id: int, address_type: Optional[str] = None, version: Optional[int] = None) -> str:
        """
        获取地址列表缓存键
        
        Args:
            user_id: 用户ID
            address_type: 地址类型（shipping/billing），None 表示所有类型
            version: 版本号，None 表示使用当前版本
        """
        if version is None:
            version = usercache_client.get_version(user_id, "addr")
        
        if address_type:
            return f"{AddressCache.CACHE_PREFIX}:v{version}:u{user_id}:list:{address_type}"
        else:
            return f"{AddressCache.CACHE_PREFIX}:v{version}:u{user_id}:list:all"
    
    @staticmethod
    def _get_detail_key(user_id: int, address_id: int, version: Optional[int] = None) -> str:
        """
        获取单个地址缓存键
        
        Args:
            user_id: 用户ID
            address_id: 地址ID
            version: 版本号，None 表示使用当前版本
        """
        if version is None:
            version = usercache_client.get_version(user_id, "addr")
        return f"{AddressCache.CACHE_PREFIX}:v{version}:u{user_id}:id:{address_id}"
    
    @staticmethod
    def _get_default_key(user_id: int, address_type: str, version: Optional[int] = None) -> str:
        """
        获取默认地址缓存键
        
        Args:
            user_id: 用户ID
            address_type: 地址类型
            version: 版本号，None 表示使用当前版本
        """
        if version is None:
            version = usercache_client.get_version(user_id, "addr")
        return f"{AddressCache.CACHE_PREFIX}:v{version}:u{user_id}:default:{address_type}"
    
    @staticmethod
    def get_address_list(
        user_id: int,
        address_type: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        从缓存获取地址列表
        
        Args:
            user_id: 用户ID
            address_type: 地址类型（可选）
            
        Returns:
            地址列表（字典列表），缓存未命中返回 None
        """
        cache_key = AddressCache._get_list_key(user_id, address_type)
        cached_data = usercache_client.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except Exception:
                return None
        
        return None
    
    @staticmethod
    def set_address_list(
        user_id: int,
        addresses: List[Dict[str, Any]],
        address_type: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存地址列表
        
        Args:
            user_id: 用户ID
            addresses: 地址列表（字典列表）
            address_type: 地址类型（可选）
            ttl: 过期时间（秒），None 使用默认值
            
        Returns:
            是否成功
        """
        cache_key = AddressCache._get_list_key(user_id, address_type)
        try:
            data_json = json.dumps(addresses, ensure_ascii=False)
            return usercache_client.set(cache_key, data_json, ttl)
        except Exception:
            return False
    
    @staticmethod
    def get_address_detail(user_id: int, address_id: int) -> Optional[Dict[str, Any]]:
        """
        从缓存获取单个地址详情
        
        Args:
            user_id: 用户ID
            address_id: 地址ID
            
        Returns:
            地址字典，缓存未命中返回 None
        """
        cache_key = AddressCache._get_detail_key(user_id, address_id)
        cached_data = usercache_client.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except Exception:
                return None
        
        return None
    
    @staticmethod
    def set_address_detail(
        user_id: int,
        address_id: int,
        address: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存单个地址详情
        
        Args:
            user_id: 用户ID
            address_id: 地址ID
            address: 地址字典
            ttl: 过期时间（秒），None 使用默认值
            
        Returns:
            是否成功
        """
        cache_key = AddressCache._get_detail_key(user_id, address_id)
        try:
            data_json = json.dumps(address, ensure_ascii=False)
            return usercache_client.set(cache_key, data_json, ttl)
        except Exception:
            return False
    
    @staticmethod
    def get_default_address(user_id: int, address_type: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取默认地址
        
        Args:
            user_id: 用户ID
            address_type: 地址类型
            
        Returns:
            默认地址字典，缓存未命中返回 None
        """
        cache_key = AddressCache._get_default_key(user_id, address_type)
        cached_data = usercache_client.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except Exception:
                return None
        
        return None
    
    @staticmethod
    def set_default_address(
        user_id: int,
        address_type: str,
        address: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存默认地址
        
        Args:
            user_id: 用户ID
            address_type: 地址类型
            address: 地址字典
            ttl: 过期时间（秒），None 使用默认值
            
        Returns:
            是否成功
        """
        cache_key = AddressCache._get_default_key(user_id, address_type)
        try:
            data_json = json.dumps(address, ensure_ascii=False)
            return usercache_client.set(cache_key, data_json, ttl)
        except Exception:
            return False
    
    @staticmethod
    def invalidate_user_addresses(user_id: int) -> None:
        """
        失效用户所有地址缓存（通过版本号递增）
        
        这是最安全的方式：递增版本号后，所有旧版本的缓存键自动失效
        新请求会使用新版本号，自然无法命中旧缓存
        
        Args:
            user_id: 用户ID
        """
        try:
            # 递增版本号，使所有旧缓存失效
            usercache_client.bump_version(user_id, "addr")
        except Exception:
            # 如果失败，尝试删除所有相关键（降级方案）
            pattern = f"{AddressCache.CACHE_PREFIX}:*:u{user_id}:*"
            usercache_client.delete_pattern(pattern)
    
    @staticmethod
    def invalidate_address_detail(user_id: int, address_id: int) -> None:
        """
        失效单个地址详情缓存
        
        Args:
            user_id: 用户ID
            address_id: 地址ID
        """
        # 获取当前版本号
        version = usercache_client.get_version(user_id, "addr")
        cache_key = AddressCache._get_detail_key(user_id, address_id, version)
        usercache_client.delete(cache_key)
    
    @staticmethod
    def invalidate_address_lists(user_id: int) -> None:
        """
        失效所有地址列表缓存（all, shipping, billing）
        
        Args:
            user_id: 用户ID
        """
        version = usercache_client.get_version(user_id, "addr")
        keys = [
            AddressCache._get_list_key(user_id, None, version),  # all
            AddressCache._get_list_key(user_id, "shipping", version),
            AddressCache._get_list_key(user_id, "billing", version),
        ]
        usercache_client.delete(*keys)
    
    @staticmethod
    def invalidate_default_addresses(user_id: int) -> None:
        """
        失效所有默认地址缓存（shipping, billing）
        
        Args:
            user_id: 用户ID
        """
        version = usercache_client.get_version(user_id, "addr")
        keys = [
            AddressCache._get_default_key(user_id, "shipping", version),
            AddressCache._get_default_key(user_id, "billing", version),
        ]
        usercache_client.delete(*keys)
