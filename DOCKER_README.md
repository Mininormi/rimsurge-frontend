# FastAdmin Docker 环境使用说明

## 环境要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose

## 快速开始

### 1. 配置环境变量

复制环境变量示例文件：

```bash
cp env.docker.example .env
```

编辑 `.env` 文件，根据需要修改数据库密码等配置。

### 2. 启动 Docker 容器

```bash
docker-compose up -d
```

### 3. 安装 Composer 依赖（首次运行）

```bash
docker-compose exec php composer install
```

### 4. 设置目录权限

确保 `runtime` 目录有写权限：

```bash
docker-compose exec php chown -R www-data:www-data /var/www/html/runtime
docker-compose exec php chmod -R 755 /var/www/html/runtime
```

### 5. 访问应用

- **FastAdmin 前台**：http://localhost:8080
- **FastAdmin 后台**：http://localhost:8080/zvElCkbXuZ.php
- **Next.js 前端**：http://localhost:3000
- **Adminer 数据库管理**：http://localhost:8081
- **数据库同步工具（Web UI）**：http://localhost:8080/database/sync-ui.php

## 数据库配置

### FastAdmin 数据库连接信息

在 FastAdmin 安装过程中，使用以下数据库连接信息：

- **数据库主机**: `mysql`（容器内）或 `127.0.0.1`（宿主机）
- **数据库端口**: `3306`

### Adminer 登录信息

访问 http://localhost:8081 后，使用以下信息登录：

- **系统**: MySQL
- **服务器**: `mysql`（Docker 服务名）
- **用户名**: `mininormi`
- **密码**: `a123123`
- **数据库**: `rimsurge`


## 常用命令

### 查看容器状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看 PHP 服务日志
docker-compose logs php

# 查看 Nginx 服务日志
docker-compose logs nginx

# 查看 MySQL 服务日志
docker-compose logs mysql

# 查看前端服务日志
docker-compose logs frontend

# 查看 Adminer 服务日志
docker-compose logs adminer
```

### 进入容器
```bash
# 进入 PHP 容器
docker-compose exec php bash

# 进入 MySQL 容器
docker-compose exec mysql bash

# 进入前端容器
docker-compose exec frontend sh
```

### 数据库同步工具命令
```bash
# 生成 Schema 文件（从数据库导出表结构）
docker compose exec -T php php /var/www/database/generate-schema.php

# 预览同步 SQL（不执行）
docker compose exec -T php php /var/www/database/sync.php --dry-run

# 执行同步（实际修改数据库）
docker compose exec -T php php /var/www/database/sync.php

# 查看同步日志
docker compose exec php cat /var/www/database/logs/1.0.0/$(date +%m-%d).log
```

### 停止服务
```bash
docker-compose stop
```

### 停止并删除容器
```bash
docker-compose down
```

### 停止并删除容器和数据卷（注意：会删除数据库数据）
```bash
docker-compose down -v
```

### 重新构建镜像
```bash
docker-compose build --no-cache
```

## 服务说明

### PHP 8.0-FPM
- 容器名: `fastadmin_php`
- 工作目录: `/var/www/html`
- 端口映射: `8082:8082`（数据库同步工具内置服务器，开发环境使用）
- 目录挂载:
  - `./backend/admin` → `/var/www/html`（FastAdmin 后端）
  - `./database` → `/var/www/database`（数据库同步工具）
- 已安装扩展: pdo_mysql, mysqli, mbstring, exif, pcntl, bcmath, gd, zip, opcache

### Nginx
- 容器名: `fastadmin_nginx`
- 端口映射: `8080:80`
- 配置文件: `docker/nginx/default.conf`
- 特殊路由:
  - `/database/*.php` → 数据库同步工具（通过 PHP-FPM）
  - 禁止访问 `/database/*.{sql,json,log}` 敏感文件

### MySQL 8.0
- 容器名: `fastadmin_mysql`
- 端口映射: `3306:3306`
- 数据持久化: Docker volume `mysql_data`
- 字符集: utf8mb4
- 排序规则: utf8mb4_unicode_ci

### Next.js 前端
- 容器名: `rimsurge_frontend`
- 端口映射: `3000:3000`
- 工作目录: `/app`
- 开发模式: 支持热重载（Hot Reload）
- 环境: Node.js 20 (Alpine)

### Adminer 数据库管理
- 容器名: `fastadmin_adminer`
- 端口映射: `8081:8080`
- 访问地址: http://localhost:8081
- 功能: 完整的数据库管理工具（增删改查、表结构管理等）

### 数据库同步工具
- 访问地址: http://localhost:8080/database/sync-ui.php
- 目录挂载: `./database` → `/var/www/database`（PHP 容器内）
- 功能:
  - 声明式数据库结构管理（通过 `schema.json`）
  - 自动检测差异并生成 SQL
  - Web UI 界面（开发环境专用）
  - 版本日志记录（按版本号和日期）
  - 待删除字段/表 TODO 管理
  - 字段类型验证和兼容性检查
- 注意: 此工具仅用于开发环境，生产环境请勿使用

## 故障排查

### 1. 无法访问网站

检查容器是否正常运行：
```bash
docker-compose ps
```

检查 Nginx 日志：
```bash
docker-compose logs nginx
```

### 2. 数据库连接失败

确保 MySQL 容器已启动：
```bash
docker-compose ps mysql
```

检查 MySQL 日志：
```bash
docker-compose logs mysql
```

测试数据库连接：
```bash
docker-compose exec mysql mysql -u fastadmin -pfastadmin123 fastadmin
```

### 3. 文件权限问题

修复 runtime 目录权限：
```bash
docker-compose exec php chown -R www-data:www-data /var/www/html/runtime
docker-compose exec php chmod -R 755 /var/www/html/runtime
```

### 4. Composer 依赖问题

重新安装依赖：
```bash
docker-compose exec php composer install --no-cache
```

### 5. 数据库同步工具无法访问

检查 Nginx 配置是否正确：
```bash
docker-compose exec nginx nginx -t
```

检查 PHP 容器内文件是否存在：
```bash
docker-compose exec php ls -la /var/www/database/sync-ui.php
```

检查 Nginx 日志：
```bash
docker-compose logs nginx | grep database
```

### 6. 数据库同步工具执行失败

查看同步日志：
```bash
# 查看最新日志
docker compose exec php ls -la /var/www/database/logs/*/

# 查看今天的日志
docker compose exec php cat /var/www/database/logs/1.0.0/$(date +%m-%d).log
```

检查数据库连接：
```bash
docker-compose exec php php /var/www/database/sync.php --dry-run
```

## 注意事项

1. **首次安装**: 访问 http://localhost:8080 会自动跳转到安装页面
2. **数据库主机**: 在容器内连接数据库时，使用服务名 `mysql`；在宿主机连接时，使用 `127.0.0.1`
3. **数据持久化**: MySQL 数据存储在 Docker volume 中，删除容器不会丢失数据（除非使用 `docker-compose down -v`）
4. **文件修改**: 修改代码后无需重启容器，PHP-FPM 会自动加载新代码
5. **端口冲突**: 如果 8080、3000、3306 或 8082 端口被占用，可以在 `docker-compose.yml` 中修改端口映射
6. **前端热重载**: Next.js 前端支持热重载，修改代码后会自动刷新（可能需要几秒钟）
7. **前端依赖**: 首次启动前端服务会自动安装 npm 依赖，可能需要几分钟时间
8. **数据库同步工具**: 
   - 仅用于开发环境，生产环境请勿使用
   - 通过 Nginx 路由访问：http://localhost:8080/database/sync-ui.php
   - 敏感文件（`.sql`, `.json`, `.log`）已被 Nginx 禁止直接访问
   - 首次使用需要先生成 `schema.json` 文件
9. **目录挂载**: `database/` 目录挂载到 PHP 容器的 `/var/www/database`，修改 `schema.json` 后立即生效

