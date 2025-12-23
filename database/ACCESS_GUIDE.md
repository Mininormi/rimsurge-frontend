# 数据库同步工具访问指南

## ✅ 已验证：服务器正在运行

端口 8082 已成功映射并可以访问。

## 访问地址

```
http://localhost:8082/sync-ui.php
```

或者

```
http://127.0.0.1:8082/sync-ui.php
```

## 如果无法访问，请检查：

### 1. 确认服务器正在运行

```bash
# 检查端口是否监听
netstat -ano | findstr :8082

# 应该看到类似输出：
# TCP    0.0.0.0:8082           0.0.0.0:0              LISTENING
```

### 2. 测试连接

在 PowerShell 中运行：
```powershell
Test-NetConnection -ComputerName localhost -Port 8082
```

应该显示：`TcpTestSucceeded : True`

### 3. 测试访问

在 PowerShell 中运行：
```powershell
Invoke-WebRequest -Uri "http://localhost:8082/test-access.html" -UseBasicParsing
```

如果返回 200，说明服务器正常。

### 4. 启动服务器（如果未运行）

```bash
docker compose exec php bash -c "cd /var/www/database && nohup php -S 0.0.0.0:8082 > /var/log/php-server.log 2>&1 &"
```

### 5. 查看服务器日志

```bash
docker compose exec php tail -f /var/log/php-server.log
```

### 6. 浏览器问题排查

- **清除浏览器缓存**：按 Ctrl+Shift+Delete
- **尝试无痕模式**：Ctrl+Shift+N (Chrome) 或 Ctrl+Shift+P (Firefox)
- **检查浏览器控制台**：F12，查看 Console 和 Network 标签
- **尝试其他浏览器**

### 7. 防火墙检查

Windows 防火墙可能阻止了端口 8082。检查：
1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 检查入站规则中是否有阻止 8082 端口的规则

## 快速诊断命令

```bash
# 1. 检查容器状态
docker compose ps php

# 2. 检查端口映射
docker compose ps php | findstr 8082

# 3. 检查服务器是否在运行
docker compose exec php curl http://localhost:8082/test-access.html

# 4. 重启服务器
docker compose exec php bash -c "cd /var/www/database && nohup php -S 0.0.0.0:8082 > /var/log/php-server.log 2>&1 &"
```

## 常见问题

### 问题：连接被拒绝
**解决**：服务器未启动，运行启动命令

### 问题：页面空白或 500 错误
**解决**：检查 PHP 错误日志
```bash
docker compose exec php tail -f /var/log/php-server.log
```

### 问题：浏览器显示"无法访问此网站"
**解决**：
1. 确认服务器正在运行
2. 检查防火墙设置
3. 尝试使用 127.0.0.1 而不是 localhost



