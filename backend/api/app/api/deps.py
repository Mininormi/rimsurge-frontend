"""
依赖注入：用户认证等
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from app.database import get_db, get_table
from app.core.security import verify_access_token
from app.schemas.user import UserResponse
from app.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户（依赖注入）
    
    支持从 Authorization Header 或 Cookie 中获取 token
    
    使用方式：
        @app.get("/me")
        def get_me(current_user: dict = Depends(get_current_user)):
            ...
    """
    # 优先从 Header 获取 token
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # 从 Cookie 获取 token
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证 Access Token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # 从数据库查询用户信息
    users_table = get_table("fa_user")
    result = db.execute(
        select(users_table).where(users_table.c.id == user_id)
    )
    user_row = result.fetchone()
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    user_dict = dict(user_row._mapping)
    
    # 检查用户状态
    if user_dict.get("status") != "normal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is locked",
        )
    
    return user_dict


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    获取当前登录用户（可选，未登录返回 None）
    """
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None


async def verify_csrf_token(request: Request):
    """
    CSRF Token 校验依赖
    
    校验规则：
    1. 只对写请求（POST/PUT/PATCH/DELETE）进行校验，GET/HEAD/OPTIONS 跳过
    2. 检查 Origin 头是否在白名单中（Origin 为空时校验 Referer 作为兜底）
    3. 检查 Header 中的 X-CSRF-Token 是否等于 Cookie 中的 csrf_token
    
    安全说明：
    - 攻击者读不到 cookie 主要靠同源策略（evil.com 的 JS 读不到 rimsurge.com 的 cookie）
    - SameSite 影响的是"跨站请求是否带 cookie"，不是"能不能读 cookie"
    
    使用方式：
        @router.post("/some-endpoint")
        async def some_endpoint(
            ...,
            _: None = Depends(verify_csrf_token)  # CSRF 校验
        ):
            ...
    
    重要：所有写接口（POST/PUT/PATCH/DELETE）必须显式添加此依赖，漏一个就等于安全漏洞！
    """
    # 0. 只对写请求进行校验（GET/HEAD/OPTIONS 跳过）
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return None
    
    # 1. 校验 Origin 头（写请求必须校验）
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    
    # 如果 Origin 为空，尝试从 Referer 提取 origin
    if not origin and referer:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(referer)
            origin = f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            pass
    
    # Origin 或 Referer 必须存在且在白名单中
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Origin header"
        )
    
    if origin not in settings.CSRF_TRUSTED_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Origin"
        )
    
    # 2. 校验 CSRF Token（Double Submit Cookie 模式）
    header_token = request.headers.get("X-CSRF-Token")
    cookie_token = request.cookies.get("csrf_token")
    
    if not header_token or not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    if header_token != cookie_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )

