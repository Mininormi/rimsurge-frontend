# 数据库同步工具服务器启动指南

## 问题说明

PHP 容器默认只运行 `php-fpm`，不会自动启动 PHP 内置服务器。因此，访问 `http://localhost:8082/sync-ui.php` 前需要手动启动服务器。

## 解决方案

### 方案 1：自动启动（推荐，已配置）

`docker-compose.yml` 已配置为容器启动时自动运行 PHP 内置服务器。

**重启容器使配置生效：**
```bash
docker compose restart php
```

**验证服务器是否运行：**
```bash
docker compose exec php curl http://localhost:8082/sync-ui.php
```
应该返回 HTTP 200。

### 方案 2：手动启动（如果自动启动失败）

如果容器重启后服务器未自动启动，可以手动启动：

**Windows:**
```bash
database\start-sync-ui.bat
```

**Linux/Mac:**
```bash
bash database/start-sync-ui.sh
```

**或直接使用 Docker 命令：**
```bash
docker compose exec -d php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php
```

### 方案 3：检查服务器状态

**检查服务器是否运行：**
```bash
docker compose exec php curl -s -o /dev/null -w '%{http_code}' http://localhost:8082/sync-ui.php
```
返回 `200` 表示服务器正在运行。

**查看服务器日志：**
```bash
docker compose exec php tail -f /tmp/php-server.log
```

**停止服务器：**
```bash
docker compose exec php pkill -f "php -S 0.0.0.0:8082"
```

## 故障排查

### 1. 无法访问 localhost:8082

**检查端口映射：**
```bash
docker compose ps php | findstr 8082
```
应该显示 `0.0.0.0:8082->8082/tcp`

**检查服务器进程：**
```bash
docker compose exec php ps aux | grep "php -S"
```

### 2. 服务器启动失败

**查看错误日志：**
```bash
docker compose exec php cat /tmp/php-server.log
```

**运行诊断脚本：**
```bash
docker compose exec php php /var/www/database/diagnose-sync-ui.php
```

### 3. 端口被占用

**检查宿主机端口占用（Windows）：**
```powershell
netstat -ano | findstr :8082
```

**如果端口被占用，可以修改 docker-compose.yml 中的端口映射：**
```yaml
ports:
  - "8083:8082"  # 改为其他端口
```

## 访问地址

服务器启动后，访问：
- http://localhost:8082/sync-ui.php
- http://127.0.0.1:8082/sync-ui.php


