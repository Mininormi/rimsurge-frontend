# CSRF 安全防护 Prompt

你是一个有真实生产经验的后端安全工程师。

当前项目技术栈：
- 后端：FastAPI
- 认证方式：HttpOnly Cookie 中的 access_token / refresh_token
- 前端：Next.js
- 所有写接口（POST/PUT/PATCH/DELETE）都使用 Cookie 认证

安全要求（必须严格遵守）：

1️⃣ 本项目使用 Cookie 承载登录态，因此必须防御 CSRF。
2️⃣ CORS 不是 CSRF 防护手段，不要把它当解决方案。
3️⃣ 所有写请求必须同时满足：
   - 校验 Origin 头（白名单方式）
   - 校验 CSRF Token（Double Submit Cookie 模式）

CSRF Token 设计要求：
- 后端生成随机 CSRF Token
- 通过 Set-Cookie 返回给前端
- csrf_token Cookie 必须：
  - 非 HttpOnly
  - Secure（生产环境）
  - SameSite 与 access_token 保持一致
- 前端在所有写请求中通过 Header 发送：
  X-CSRF-Token: <token>
- 后端校验：
  Header 中的 X-CSRF-Token 必须等于 Cookie 中的 csrf_token

实现要求：
- 使用 FastAPI 中间件或依赖注入实现 CSRF 校验
- **所有写接口（POST/PUT/PATCH/DELETE）必须显式添加 `Depends(verify_csrf_token)`，漏一个就等于安全漏洞！**
- refresh / logout 接口也必须受 CSRF 保护
- 登录/注册接口不校验 CSRF（因为此时还没有 CSRF Token），但会设置 CSRF Token Cookie
- 验证码接口不要求 CSRF Token（未登录用户可能没有），改用强限流/风控
- 给出完整可运行的示例代码
- 明确标注应该放在哪个文件（例如 middleware.py / deps.py）
- 不要省略关键逻辑，不要只给伪代码

如果你的实现不能防御 CSRF，请不要输出。

## 实现示例

### 1. CSRF Token 生成

**文件**: `backend/api/app/core/security.py`

```python
import secrets

def generate_csrf_token() -> str:
    """
    生成 CSRF Token（32 字节随机字符串）
    
    Returns:
        CSRF Token 字符串
    """
    return secrets.token_urlsafe(32)
```

### 2. CSRF Token 设置（登录/注册时）

**文件**: `backend/api/app/api/v1/auth.py`

在登录和注册接口中，设置 CSRF Token Cookie：

```python
from app.core.security import generate_csrf_token

# 在 login 和 register 函数中，设置 Cookie 后添加：
csrf_token = generate_csrf_token()
response.set_cookie(
    key="csrf_token",
    value=csrf_token,
    httponly=False,  # 非 HttpOnly，前端需要读取
    secure=is_production,  # 生产环境使用 HTTPS
    samesite="lax",  # 与 access_token 保持一致
    max_age=settings.CSRF_TOKEN_EXPIRE_SECONDS,  # CSRF Token 过期时间（默认1天）
)
```

### 3. CSRF 校验依赖注入

**文件**: `backend/api/app/api/deps.py`

```python
from fastapi import Request, HTTPException, status
from app.config import settings

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
    
    # 如果 Origin 为空，尝试从 Referer 提取 origin（兜底）
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
    
    # 2. 校验 CSRF Token
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
```

### 4. 在所有写请求中应用 CSRF 保护

**文件**: `backend/api/app/api/v1/auth.py`

**重要：所有写接口（POST/PUT/PATCH/DELETE）必须显式添加 `Depends(verify_csrf_token)`，漏一个就等于安全漏洞！**

在所有 POST/PUT/PATCH/DELETE 接口中添加 CSRF 校验（登录/注册和验证码接口除外）：

```python
from app.api.deps import verify_csrf_token

@router.post("/refresh", ...)
async def refresh_token(
    request: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_csrf_token)  # CSRF 校验
):
    ...

@router.post("/logout", ...)
async def logout(
    request: LogoutRequest,
    req: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_csrf_token)  # CSRF 校验
):
    ...

# 注意：验证码接口不要求 CSRF Token（未登录用户可能没有）
# 改用强限流/风控（IP+邮箱维度）来防止滥用
@router.post("/send-verification-code", ...)
async def send_verification_code(
    request: SendVerificationCodeRequest,
    req: Request
    # 注意：这里不添加 Depends(verify_csrf_token)
):
    ...

@router.post("/verify-code", ...)
async def verify_code(
    request: VerifyCodeRequest,
    req: Request
    # 注意：这里不添加 Depends(verify_csrf_token)
):
    ...
```

**重要提示**: 
- **所有写接口（POST/PUT/PATCH/DELETE）必须显式添加 `Depends(verify_csrf_token)`，漏一个就等于安全漏洞！**
- 登录/注册接口不校验 CSRF（因为此时还没有 CSRF Token），但会设置 CSRF Token Cookie
- 验证码接口（`/send-verification-code` 和 `/verify-code`）不要求 CSRF Token，改用强限流/风控（IP+邮箱维度）
- GET/HEAD/OPTIONS 请求不需要 CSRF 保护（依赖函数会自动跳过）

### 5. 前端获取和使用 CSRF Token

**文件**: `frontend/lib/api/client.ts`

```typescript
class ApiClient {
  /**
   * 获取 Cookie 值
   */
  private getCookie(name: string): string | null {
    if (typeof document === 'undefined') return null
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift() || null
    return null
  }

  /**
   * 发送请求
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    // 获取 CSRF Token（从 Cookie）
    const csrfToken = this.getCookie('csrf_token')
    
    // 判断 body 是否为 JSON（需要设置 Content-Type）
    // 只有当 body 是字符串时才设置 Content-Type（因为 post/put 方法使用 JSON.stringify）
    // 如果 body 是 FormData 或 Blob 等类型，浏览器会自动设置正确的 Content-Type
    const isJsonBody = options.body && typeof options.body === 'string'
    
    const config: RequestInit = {
      ...options,
      headers: {
        // 只有在 body 是 JSON 字符串时才设置 Content-Type
        // 如果 body 是 FormData 或其他类型，浏览器会自动设置正确的 Content-Type
        ...(isJsonBody && { 'Content-Type': 'application/json' }),
        ...(csrfToken && { 'X-CSRF-Token': csrfToken }),  // 添加 CSRF Token
        ...options.headers,
      },
      credentials: 'include', // 自动携带 Cookie
    }
    
    // ... 其余代码
  }
}
```

### 6. 配置更新

**文件**: `backend/api/app/config.py`

新增 CSRF_TRUSTED_ORIGINS 配置（独立于 CORS_ORIGINS）：

```python
# CORS 配置
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8001",
]

# CSRF 防护配置（独立于 CORS）
CSRF_TRUSTED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8001",
]
```

**重要**: 不要使用 CORS_ORIGINS 作为 CSRF 的 trusted origin 白名单，必须使用独立的 CSRF_TRUSTED_ORIGINS。

## 特殊处理

### 登录/注册接口的 CSRF 处理

由于登录/注册是用户首次交互，此时还没有 CSRF Token，因此：
- **登录/注册接口不校验 CSRF Token**（但设置 CSRF Token Cookie）
- **其他所有写请求都必须校验 CSRF Token**

### 验证码接口的 CSRF 处理

`/send-verification-code` 和 `/verify-code` 接口不要求 CSRF Token，因为：
- 未登录用户可能没有 CSRF Token
- 改用强限流/风控（IP+邮箱维度）来防止滥用

### GET 请求

GET 请求通常不需要 CSRF 保护（因为不会修改数据），但如果需要，也可以添加。

### Origin 校验说明

- **攻击者读不到 cookie 主要靠同源策略**（evil.com 的 JS 读不到 rimsurge.com 的 cookie）
- **SameSite 影响的是"跨站请求是否带 cookie"**，不是"能不能读 cookie"
- 写请求必须校验 Origin 头，如果 Origin 为空，校验 Referer 作为兜底
- 两者都没有则返回 403

## 测试要点

1. ✅ 登录后，CSRF Token Cookie 已设置（非 HttpOnly）
2. ✅ 写请求包含 X-CSRF-Token Header
3. ✅ 后端校验 Origin 头（白名单）
4. ✅ 后端校验 CSRF Token 匹配
5. ✅ 缺少 CSRF Token 时返回 403
6. ✅ CSRF Token 不匹配时返回 403
7. ✅ Origin 不在白名单时返回 403

## 文件位置总结

- **CSRF Token 生成**: `backend/api/app/core/security.py` - `generate_csrf_token()`
- **CSRF Token 设置**: `backend/api/app/api/v1/auth.py` - 登录/注册接口中
- **CSRF 校验依赖**: `backend/api/app/api/deps.py` - `verify_csrf_token()`
- **前端 CSRF Token 使用**: `frontend/lib/api/client.ts` - `getCookie()` 和 `request()` 方法
- **配置**: `backend/api/app/config.py` - `CSRF_TRUSTED_ORIGINS`（独立于 CORS_ORIGINS）

## 安全原理

### Double Submit Cookie 模式

1. 服务器生成随机 CSRF Token，通过 Cookie 发送给客户端
2. 客户端在每次写请求中，将 Cookie 中的 CSRF Token 通过 Header 发送回服务器
3. 服务器比较 Header 和 Cookie 中的 CSRF Token 是否一致

### 为什么能防御 CSRF？

- 攻击者无法读取 Cookie，主要依赖浏览器同源策略；SameSite 仅影响跨站请求是否携带 Cookie，而不是 Cookie 是否可读。
- 攻击者无法设置自定义 Header（浏览器同源策略）
- 因此攻击者无法构造包含正确 CSRF Token 的请求

### Origin 头校验的作用

- 作为额外的安全层，确保请求来自允许的源
- 即使 CSRF Token 泄露，Origin 校验也能提供额外保护
