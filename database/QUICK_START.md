# 快速开始 - 数据库同步工具

## 🚀 5 分钟快速上手

### 第一步：复制工具到新项目

```bash
# 复制整个 database 目录
cp -r old-project/database new-project/database

# 删除项目特定文件（保留工具核心文件）
cd new-project/database
rm -f schema.json pending_deletions.json processed_deletions.json
rm -rf logs/*
```

### 第二步：配置 Docker（如果使用 Docker）

确保 `docker-compose.yml` 中有：

```yaml
services:
  php:
    volumes:
      - ./database:/var/www/database    # 挂载 database 目录
    ports:
      - "8082:8082"                     # Web UI 端口
```

### 第三步：启动 Web UI

```bash
# Docker 环境
docker-compose exec php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"

# 访问
http://localhost:8082/sync-ui.php
```

### 第四步：生成初始 Schema

在 Web UI 中点击"生成 Schema 文件"，或命令行：

```bash
docker-compose exec php php /var/www/database/generate-schema.php
```

### 第五步：开始使用

1. 编辑 `database/schema.json` 修改表结构
2. 在 Web UI 中预览 SQL
3. 执行同步

## 📋 核心文件清单

**必需文件（复制到新项目）：**
- ✅ `sync.php`
- ✅ `sync-ui.php`
- ✅ `generate-schema.php`
- ✅ `SchemaParser.php`
- ✅ `DatabaseInspector.php`
- ✅ `DiffGenerator.php`
- ✅ `start-ui.sh` / `start-ui.bat`

**自动生成文件（不需要复制）：**
- ❌ `schema.json` - 需要重新生成
- ❌ `pending_deletions.json` - 自动生成
- ❌ `processed_deletions.json` - 自动生成
- ❌ `logs/` - 自动创建

## 🔧 常用命令

```bash
# 生成 Schema
docker-compose exec php php /var/www/database/generate-schema.php

# 预览同步（不执行）
docker-compose exec php php /var/www/database/sync.php --dry-run

# 执行同步
docker-compose exec php php /var/www/database/sync.php

# 启动 Web UI
docker-compose exec php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"
```

## 📖 详细文档

- **部署指南**：`DEPLOYMENT_GUIDE.md` - 完整部署说明
- **使用指南**：`USAGE_GUIDE.md` - Schema 修改详细说明
- **访问指南**：`ACCESS_GUIDE.md` - Web UI 配置

## ⚡ 一键启动脚本

**Linux/Mac:**
```bash
chmod +x database/start-ui.sh
./database/start-ui.sh
```

**Windows:**
```bash
database\start-ui.bat
```

## ⚠️ 重要提示

1. **表前缀**：工具默认管理 `mini_` 前缀的表
2. **生产环境**：Web UI 仅用于开发环境
3. **数据备份**：执行同步前建议备份数据库
4. **版本控制**：将 `schema.json` 纳入 Git，不要提交 `logs/` 目录
