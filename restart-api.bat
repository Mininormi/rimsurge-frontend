@echo off
chcp 65001 >nul
echo ==========================================
echo FastAPI 容器重启和日志查看脚本
echo ==========================================
echo.

REM 检查 Docker 是否运行
echo 正在检查 Docker 服务状态...
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 服务未运行，请先启动 Docker Desktop
    echo.
    pause
    exit /b 1
)
echo [成功] Docker 服务运行正常
echo.

REM 检查容器是否存在
echo 正在检查 FastAPI 容器状态...
docker compose ps api >nul 2>&1
if errorlevel 1 (
    echo [警告] 无法检查容器状态，尝试继续执行...
    echo.
) else (
    echo [信息] 容器状态检查完成
    echo.
)

REM 重启容器
echo ==========================================
echo 正在重启 FastAPI 容器...
echo ==========================================
docker compose restart api

if errorlevel 1 (
    echo [错误] 重启容器失败
    echo.
    pause
    exit /b 1
)

echo [成功] 容器重启完成
echo.

REM 等待服务启动
echo 等待服务完全启动（3秒）...
timeout /t 3 /nobreak >nul

REM 显示容器状态
echo.
echo ==========================================
echo 容器状态：
echo ==========================================
docker compose ps api
echo.

REM 显示日志
echo ==========================================
echo 开始显示实时日志（按 Ctrl+C 退出）
echo ==========================================
echo.
docker compose logs -f api
