# 部署检查清单

使用此清单确保工具在新项目中正确部署。

## ✅ 文件检查

- [ ] `sync.php` 已复制
- [ ] `sync-ui.php` 已复制
- [ ] `generate-schema.php` 已复制
- [ ] `SchemaParser.php` 已复制
- [ ] `DatabaseInspector.php` 已复制
- [ ] `DiffGenerator.php` 已复制
- [ ] `start-ui.sh` 已复制（Linux/Mac）
- [ ] `start-ui.bat` 已复制（Windows）

## ✅ Docker 配置检查

- [ ] `docker-compose.yml` 中 PHP 服务已挂载 `./database:/var/www/database`
- [ ] `docker-compose.yml` 中 PHP 服务已映射端口 `8082:8082`
- [ ] Docker 容器已启动：`docker-compose up -d`

## ✅ 数据库配置检查

- [ ] `backend/admin/application/database.php` 配置正确
- [ ] 数据库连接正常
- [ ] 表前缀设置正确（默认 `mini_`）

## ✅ 初始设置

- [ ] 已生成初始 `schema.json`：运行 `generate-schema.php`
- [ ] Web UI 可以访问：`http://localhost:8082/sync-ui.php`
- [ ] 测试执行同步（预览模式）

## ✅ 版本控制

- [ ] `schema.json` 已添加到 Git
- [ ] `.gitignore` 中已排除 `logs/` 目录
- [ ] `.gitignore` 中已排除 `pending_deletions.json`
- [ ] `.gitignore` 中已排除 `processed_deletions.json`

## 📝 示例 .gitignore 配置

```gitignore
# 数据库同步工具
database/logs/
database/pending_deletions.json
database/processed_deletions.json

# 保留 schema.json（需要版本控制）
!database/schema.json
```

## 🎯 完成检查后

1. ✅ 所有项目都打勾
2. ✅ 测试生成 Schema
3. ✅ 测试执行同步（预览模式）
4. ✅ 确认 Web UI 正常工作

## 🆘 遇到问题？

参考 `DEPLOYMENT_GUIDE.md` 中的"常见问题"章节。
