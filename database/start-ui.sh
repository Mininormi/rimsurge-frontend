#!/bin/bash
# 启动数据库同步工具 Web 界面（PHP 内置服务器）
# 使用方法: docker compose exec php bash /var/www/database/start-ui.sh

cd /var/www/database
echo "启动数据库同步工具..."
echo "访问地址: http://localhost:8082/sync-ui.php"
php -S 0.0.0.0:8082



