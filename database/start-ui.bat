@echo off
REM 启动数据库同步工具 Web 界面（Windows）
REM 使用方法: 直接双击此文件，或在命令行运行

echo 启动数据库同步工具...
echo 访问地址: http://localhost:8082/sync-ui.php
docker compose exec -d php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"



