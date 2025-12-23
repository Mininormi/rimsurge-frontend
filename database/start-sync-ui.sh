#!/bin/bash
# 启动数据库同步工具 Web 界面
# 使用方法: docker compose exec php bash /var/www/database/start-sync-ui.sh

cd /var/www/database
php -S 0.0.0.0:8082 sync-ui.php



