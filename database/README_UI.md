# 数据库同步工具 Web UI 使用指南

## 访问方式

### 方式 1：通过 PHP 内置服务器（推荐）

1. **确保端口映射已配置**
   
   在 `docker-compose.yml` 中，php 服务应该包含：
   ```yaml
   php:
     ports:
       - "8082:8082"
   ```

2. **启动 PHP 内置服务器**
   
   ```bash
   docker compose exec -d php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php
   ```

3. **访问地址**
   
   ```
   http://localhost:8082/sync-ui.php
   ```

### 方式 2：通过 Nginx（需要配置）

访问地址：
```
http://localhost:8080/database/sync-ui.php
```

## 启动/停止服务器

### 启动服务器
```bash
docker compose exec -d php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php
```

### 停止服务器
```bash
docker compose exec php pkill -f "php -S 0.0.0.0:8082"
```

### 查看服务器状态
```bash
# 检查端口是否监听
docker compose exec php netstat -tlnp | grep 8082

# 检查进程
docker compose exec php ps aux | grep "php -S"
```

## 故障排查

### 1. 无法访问 localhost:8082

**检查端口映射：**
```bash
docker compose ps php
```
应该显示 `0.0.0.0:8082->8082/tcp`

**如果端口映射不存在：**
1. 确保 `docker-compose.yml` 中有端口配置
2. 重新创建容器：`docker compose up -d --force-recreate php`

### 2. 服务器未启动

**检查服务器是否运行：**
```bash
docker compose exec php curl http://localhost:8082/sync-ui.php
```

**如果返回 200，说明服务器在运行**
**如果连接被拒绝，需要启动服务器**

### 3. 容器内可以访问，宿主机无法访问

这通常是端口映射问题：
1. 检查防火墙设置
2. 确认端口 8082 未被占用：`netstat -ano | findstr :8082`
3. 重新创建容器使端口映射生效

## 便捷脚本

### Windows
```bash
database\start-ui.bat
```

### Linux/Mac
```bash
bash database/start-ui.sh
```

## 注意事项

1. **PHP 内置服务器是单线程的**，适合开发环境使用
2. **每次容器重启后需要重新启动服务器**
3. **此工具仅用于开发环境**，生产环境请勿使用
4. **确保 exec() 函数可用**，否则无法执行同步操作

