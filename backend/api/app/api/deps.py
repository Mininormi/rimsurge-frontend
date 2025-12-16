"""
依赖注入：用户认证等
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db, get_table
from app.core.security import verify_access_token
from app.schemas.user import UserResponse
from app.config import settings


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户（依赖注入）
    
    Web API 认证方式：仅支持 HttpOnly Cookie 中的 access_token
    
    ⚠️ 重要：本函数仅支持 Cookie 认证，不支持 Authorization: Bearer
    如果请求中包含 Authorization: Bearer Header，将被忽略
    
    使用方式：
        @app.get("/me")
        def get_me(current_user: dict = Depends(get_current_user)):
            ...
    """
    # 从 Cookie 获取 token（Web API 只支持 Cookie 认证）
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    # 验证 Access Token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
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
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户（可选，未登录返回 None）
    """
    from typing import Optional
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


async def verify_origin_only(request: Request):
    """
    Origin/Referer 校验依赖（用于登录/注册接口）
    
    校验规则：
    - 只检查 Origin 头是否在白名单中（Origin 为空时校验 Referer 作为兜底）
    - 不校验 CSRF Token（因为首次请求还没有 csrf_token）
    
    使用场景：
    - 登录/注册接口（用户首次交互，还没有 CSRF Token）
    
    使用方式：
        @router.post("/login")
        async def login(
            ...,
            _: None = Depends(verify_origin_only)  # Origin 校验
        ):
            ...
    
    重要：
    - 登录/注册接口必须添加此依赖，防止跨站请求伪造
    - 成功后必须下发 csrf_token Cookie，供后续请求使用
    """
    # 校验 Origin 头（写请求必须校验）
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


async def verify_csrf_token(request: Request):
    """
    CSRF Token 校验依赖
    
    校验规则：
    1. 检查 Origin 头是否在白名单中（Origin 为空时校验 Referer 作为兜底）
    2. 检查 Header 中的 X-CSRF-Token 是否等于 Cookie 中的 csrf_token
    
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
    
    重要：
    - 所有写接口（POST/PUT/PATCH/DELETE）必须显式添加此依赖，漏一个就等于安全漏洞！
    - 此函数不判断 HTTP method，由开发者是否在路由上添加 Depends 来决定是否校验
    - 如果开发者忘记添加 Depends，接口将直接暴露，不会被"伪安全"掩盖
    """
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

