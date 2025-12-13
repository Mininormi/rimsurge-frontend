#!/bin/bash
# ============================================
# 数据库同步脚本 - Docker 版本 (Linux/Mac)
# ============================================

echo "正在通过 Docker 执行数据库同步..."
echo ""

# 检查容器是否运行
if ! docker-compose ps php | grep -q "Up"; then
    echo "[错误] PHP 容器未运行，请先启动 Docker 容器："
    echo "  docker-compose up -d"
    exit 1
fi

# 在容器内执行同步脚本
docker-compose exec -T php php /var/www/database/sync.php

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 数据库同步失败"
    exit 1
else
    echo ""
    echo "[成功] 数据库同步完成！"
fi

