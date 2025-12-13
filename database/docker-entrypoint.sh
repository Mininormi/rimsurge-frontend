#!/bin/bash
# Docker 容器启动时自动启动 PHP 内置服务器

# 启动 PHP 内置服务器（后台运行）
cd /var/www/database
nohup php -S 0.0.0.0:8082 > /var/log/php-server.log 2>&1 &

# 保持容器运行
exec "$@"

