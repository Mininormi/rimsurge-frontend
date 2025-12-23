@echo off
REM 启动数据库同步工具 Web 界面（Windows，带调试）
REM 使用方法: database\start-sync-ui-debug.bat

echo 启动数据库同步工具（带调试日志）...
echo 访问地址: http://localhost:8082/sync-ui.php
echo.

REM 先运行诊断脚本
echo === 运行诊断 ===
docker compose exec php php /var/www/database/diagnose-sync-ui.php
echo.

REM 启动服务器（后台运行）
echo === 启动服务器 ===
docker compose exec -d php bash /var/www/database/start-sync-ui-with-logs.sh
echo.

echo 等待服务器启动...
timeout /t 3 /nobreak >nul

REM 检查服务器状态
echo === 检查服务器状态 ===
docker compose exec php ps aux | findstr "php -S" | findstr 8082
if %errorlevel% equ 0 (
    echo ✓ 服务器正在运行
) else (
    echo ✗ 服务器未运行，查看日志:
    docker compose exec php cat /tmp/php-server.log
)
echo.

echo === 查看调试日志 ===
docker compose exec php cat /tmp/debug-sync-ui.log
echo.

echo 完成！如果无法访问，请检查:
echo   1. Docker 端口映射: docker compose ps php ^| findstr 8082
echo   2. 防火墙设置
echo   3. 浏览器缓存
echo.

pause


