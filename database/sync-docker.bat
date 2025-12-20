@echo off
chcp 65001 >nul 2>&1
REM ============================================
REM 数据库同步脚本 - Docker 版本 (Windows)
REM ============================================

echo 正在通过 Docker 执行数据库同步...
echo.

REM 直接使用 docker compose（新版本）
REM 如果失败，可以尝试改为 docker-compose

REM 检查容器是否运行
docker compose ps php 2>nul | findstr "Up" >nul
if errorlevel 1 (
    echo [错误] PHP 容器未运行，请先启动 Docker 容器：
    echo   docker compose up -d
    echo.
    pause
    exit /b 1
)

REM 在容器内执行同步脚本
echo 正在执行数据库同步...
echo.
docker compose exec -T php php /var/www/database/sync.php

if errorlevel 1 (
    echo.
    echo [错误] 数据库同步失败
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [成功] 数据库同步完成！
    echo.
    pause
)

