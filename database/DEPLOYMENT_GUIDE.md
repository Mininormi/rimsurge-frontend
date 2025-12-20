# 数据库同步工具 - 部署与使用指南

## 📋 工具概述

这是一个基于 Schema 驱动的数据库结构同步工具，支持：
- ✅ 声明式数据库结构管理（通过 `schema.json`）
- ✅ 自动检测差异并生成 SQL
- ✅ Web UI 界面（开发环境专用）
- ✅ 版本日志记录（按版本号和日期）
- ✅ 待删除字段/表 TODO 管理

## 📁 工具文件结构

```
database/
├── sync.php                    # 核心同步脚本（命令行）
├── sync-ui.php                 # Web UI 界面
├── generate-schema.php         # 从数据库生成 schema.json
├── SchemaParser.php            # Schema 解析器
├── DatabaseInspector.php       # 数据库结构检查器
├── DiffGenerator.php           # 差异生成器
├── schema.json                 # Schema 定义文件（需要生成）
├── pending_deletions.json       # 待删除字段/表列表（自动生成）
├── processed_deletions.json     # 已处理删除项（自动生成）
├── logs/                       # 版本日志目录（自动创建）
│   └── {version}/              # 按版本号分类
│       └── MM-DD.log            # 按日期记录日志
├── start-ui.sh                 # Linux/Mac 启动脚本
├── start-ui.bat                # Windows 启动脚本
└── DEPLOYMENT_GUIDE.md         # 本文档
```

## 🚀 在新项目中部署

### ⚡ 快速部署（推荐）

**一键复制脚本：**

```bash
#!/bin/bash
# 从旧项目复制工具到新项目

OLD_PROJECT="path/to/old-project"
NEW_PROJECT="path/to/new-project"

# 创建目录
mkdir -p "$NEW_PROJECT/database"

# 复制核心文件
cp "$OLD_PROJECT/database/sync.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/sync-ui.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/generate-schema.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/SchemaParser.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/DatabaseInspector.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/DiffGenerator.php" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/start-ui.sh" "$NEW_PROJECT/database/"
cp "$OLD_PROJECT/database/start-ui.bat" "$NEW_PROJECT/database/"

echo "✅ 工具文件已复制到 $NEW_PROJECT/database/"
echo "📝 下一步：配置 docker-compose.yml 并生成初始 schema.json"
```

### 方法一：复制整个 database 目录（推荐）

1. **复制工具文件**
   ```bash
   # 从旧项目复制整个 database 目录到新项目
   cp -r old-project/database new-project/database
   ```

2. **清理项目特定文件**
   ```bash
   cd new-project/database
   
   # 删除项目特定的文件（这些需要重新生成）
   rm -f schema.json                    # 需要重新生成
   rm -f pending_deletions.json         # 会自动生成
   rm -f processed_deletions.json       # 会自动生成
   rm -rf logs/*                        # 日志目录会自动创建
   
   # 保留工具核心文件（这些是必需的）
   # ✅ sync.php
   # ✅ sync-ui.php
   # ✅ generate-schema.php
   # ✅ SchemaParser.php
   # ✅ DatabaseInspector.php
   # ✅ DiffGenerator.php
   # ✅ start-ui.sh / start-ui.bat
   ```

### 方法二：只复制核心文件

如果只想复制核心工具文件：

```bash
# 创建 database 目录
mkdir -p new-project/database

# 复制核心文件
cp old-project/database/sync.php new-project/database/
cp old-project/database/sync-ui.php new-project/database/
cp old-project/database/generate-schema.php new-project/database/
cp old-project/database/SchemaParser.php new-project/database/
cp old-project/database/DatabaseInspector.php new-project/database/
cp old-project/database/DiffGenerator.php new-project/database/
cp old-project/database/start-ui.sh new-project/database/
cp old-project/database/start-ui.bat new-project/database/
```

### 📋 核心文件清单

**必需文件（必须复制）：**
- ✅ `sync.php` - 核心同步脚本
- ✅ `sync-ui.php` - Web UI 界面
- ✅ `generate-schema.php` - Schema 生成工具
- ✅ `SchemaParser.php` - Schema 解析器
- ✅ `DatabaseInspector.php` - 数据库检查器
- ✅ `DiffGenerator.php` - 差异生成器
- ✅ `start-ui.sh` / `start-ui.bat` - 启动脚本

**不需要复制的文件（会自动生成）：**
- ❌ `schema.json` - 需要在新项目中重新生成
- ❌ `pending_deletions.json` - 自动生成
- ❌ `processed_deletions.json` - 自动生成
- ❌ `logs/` - 自动创建

## 🐳 Docker 环境配置

### 1. 确保 docker-compose.yml 配置正确

在 `docker-compose.yml` 中，PHP 服务需要：

```yaml
services:
  php:
    # ... 其他配置 ...
    volumes:
      - ./backend/admin:/var/www/html
      - ./database:/var/www/database    # 重要：挂载 database 目录
    ports:
      - "8082:8082"                     # Web UI 访问端口
```

### 2. 启动 Web UI（Docker 环境）

**方式一：使用启动脚本（推荐）**

```bash
# Linux/Mac
docker-compose exec php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"

# Windows PowerShell
docker-compose exec php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"
```

**方式二：手动启动**

```bash
# 进入 PHP 容器
docker-compose exec php bash

# 在容器内执行
cd /var/www/database
php -S 0.0.0.0:8082
```

**方式三：后台运行（使用启动脚本）**

```bash
# Linux/Mac
chmod +x database/start-ui.sh
docker-compose exec -d php bash -c "cd /var/www/database && php -S 0.0.0.0:8082"

# Windows
# 使用 start-ui.bat（需要修改为 Docker 命令）
```

### 3. 访问 Web UI

启动后，在浏览器访问：
```
http://localhost:8082/sync-ui.php
```

## 📝 快速开始步骤

### 第一步：生成初始 Schema

```bash
# Docker 环境
docker-compose exec php php /var/www/database/generate-schema.php

# 本地环境
php database/generate-schema.php
```

这会生成 `database/schema.json` 文件，包含当前数据库的所有表结构。

### 第二步：修改 Schema（如需要）

编辑 `database/schema.json`：
- 添加新字段
- 修改字段类型
- 添加索引
- 删除字段（会加入 TODO 列表）

### 第三步：执行同步

**方式一：使用 Web UI（推荐）**
1. 访问 `http://localhost:8082/sync-ui.php`
2. 点击"执行同步"按钮
3. 查看执行结果

**方式二：命令行**
```bash
# Docker 环境
docker-compose exec php php /var/www/database/sync.php

# 预览模式（只显示 SQL，不执行）
docker-compose exec php php /var/www/database/sync.php --dry-run

# 本地环境
php database/sync.php
php database/sync.php --dry-run
```

## ⚙️ 依赖要求

### 1. PHP 环境
- PHP >= 7.0
- 需要 ThinkPHP 框架（用于数据库连接）

### 2. 数据库配置
工具使用 ThinkPHP 的数据库配置，确保 `backend/admin/application/database.php` 配置正确。

### 3. 表前缀约定
- 工具默认管理 `mini_` 前缀的表
- `fa_` 前缀的表由 FastAdmin 管理，不会被同步

## 📖 使用流程

```
1. 生成 Schema
   └─> php generate-schema.php
       └─> 生成 schema.json

2. 修改 Schema
   └─> 编辑 schema.json
       ├─> 添加字段
       ├─> 修改字段
       └─> 删除字段（会加入 TODO）

3. 执行同步
   └─> php sync.php 或 Web UI
       ├─> 检测差异
       ├─> 生成 SQL
       ├─> 执行 SQL（或预览）
       └─> 记录日志

4. 处理待删除项
   └─> Web UI 中查看 TODO
       └─> 手动删除后标记"已处理"
```

## 🔧 常见问题

### Q1: 如何修改表前缀？

编辑 `database/sync.php`，找到：
```php
$this->prefix = 'mini_';  // 改为你需要的前缀
```

### Q2: Web UI 无法访问？

1. 检查端口映射：`docker-compose.yml` 中是否有 `8082:8082`
2. 检查 PHP 服务器是否启动
3. 检查防火墙设置

### Q3: Schema 文件不存在？

运行 `php generate-schema.php` 生成初始 Schema。

### Q4: 日志文件在哪里？

日志文件保存在 `database/logs/{version}/MM-DD.log`，例如：
- `database/logs/1.0.2/12-13.log`

### Q5: 如何查看历史日志？

直接打开对应的日志文件：
```bash
# 查看版本 1.0.2 在 12月13日的日志
cat database/logs/1.0.2/12-13.log
```

## 📚 相关文档

- `USAGE_GUIDE.md` - Schema 修改详细指南
- `ACCESS_GUIDE.md` - Web UI 访问配置指南
- `README.md` - 工具功能说明

## ⚠️ 注意事项

1. **生产环境警告**：此工具仅用于开发环境，生产环境请勿使用 Web UI
2. **数据备份**：执行同步前建议备份数据库
3. **版本管理**：修改 Schema 后记得更新 `version` 字段
4. **待删除项**：删除字段/表需要手动处理，工具只提供 TODO 提醒

## 🎯 最佳实践

1. **版本号管理**
   - 每次重大变更后更新 `schema.json` 中的 `version`
   - 版本号格式：`主版本.次版本.修订版本`（如 `1.0.2`）

2. **Schema 修改流程**
   - 先修改 `schema.json`
   - 使用 `--dry-run` 预览 SQL
   - 确认无误后执行同步

3. **日志管理**
   - 定期查看日志文件
   - 重要变更后检查日志确认执行结果

4. **团队协作**
   - 将 `schema.json` 纳入版本控制
   - 不要提交 `logs/`、`pending_deletions.json`、`processed_deletions.json`

## 📞 技术支持

如遇问题，请检查：
1. 日志文件：`database/logs/{version}/MM-DD.log`
2. 调试日志：`/var/www/.cursor/debug.log`（Docker）或 `../.cursor/debug.log`（本地）

