@echo off
REM 启动数据库同步工具 Web 界面（Windows）
REM 使用方法: docker compose exec php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php

docker compose exec php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php



