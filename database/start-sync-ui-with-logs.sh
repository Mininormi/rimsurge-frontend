#!/bin/bash
# 启动数据库同步工具 Web 界面（带调试日志）
# 使用方法: docker compose exec php bash /var/www/database/start-sync-ui-with-logs.sh

cd /var/www/database

# #region agent log
echo "{\"location\":\"start-sync-ui-with-logs.sh:7\",\"message\":\"Starting PHP built-in server\",\"data\":{\"port\":8082,\"directory\":\"/var/www/database\",\"router\":\"sync-ui.php\"},\"timestamp\":$(date +%s)000,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"A\"}" >> /tmp/debug-sync-ui.log
# #endregion

echo "启动数据库同步工具..."
echo "访问地址: http://localhost:8082/sync-ui.php"
echo "调试日志: /tmp/debug-sync-ui.log"

# #region agent log
echo "{\"location\":\"start-sync-ui-with-logs.sh:13\",\"message\":\"Before starting server\",\"data\":{\"php_binary\":\"$(which php)\",\"current_dir\":\"$(pwd)\"},\"timestamp\":$(date +%s)000,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"C\"}" >> /tmp/debug-sync-ui.log
# #endregion

# 启动 PHP 内置服务器（后台运行）
php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php > /tmp/php-server.log 2>&1 &
SERVER_PID=$!

# #region agent log
echo "{\"location\":\"start-sync-ui-with-logs.sh:20\",\"message\":\"Server started\",\"data\":{\"pid\":$SERVER_PID,\"port\":8082},\"timestamp\":$(date +%s)000,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"A\"}" >> /tmp/debug-sync-ui.log
# #endregion

sleep 2

# 检查服务器是否启动成功
if ps -p $SERVER_PID > /dev/null; then
    echo "✓ 服务器启动成功 (PID: $SERVER_PID)"
    # #region agent log
    echo "{\"location\":\"start-sync-ui-with-logs.sh:28\",\"message\":\"Server confirmed running\",\"data\":{\"pid\":$SERVER_PID},\"timestamp\":$(date +%s)000,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"A\"}" >> /tmp/debug-sync-ui.log
    # #endregion
else
    echo "✗ 服务器启动失败，查看日志: /tmp/php-server.log"
    # #region agent log
    echo "{\"location\":\"start-sync-ui-with-logs.sh:32\",\"message\":\"Server failed to start\",\"data\":{\"pid\":$SERVER_PID,\"log\":\"$(cat /tmp/php-server.log 2>/dev/null | head -5)\"},\"timestamp\":$(date +%s)000,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"C\"}" >> /tmp/debug-sync-ui.log
    # #endregion
fi

echo "查看服务器日志: docker compose exec php tail -f /tmp/php-server.log"
echo "查看调试日志: docker compose exec php cat /tmp/debug-sync-ui.log"


