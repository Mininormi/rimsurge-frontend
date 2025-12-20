# Schema.json 修改与同步使用指南

## Schema.json 文件结构

`schema.json` 文件的基本结构：

```json
{
    "version": "1.0.0",
    "generated_at": "2025-12-13 10:20:17",
    "tables": {
        "mini_table_name": {
            "columns": {
                "field_name": {
                    "type": "字段类型",
                    "null": true/false,
                    "default": "默认值",
                    "auto_increment": true/false,
                    "comment": "字段注释"
                }
            },
            "primary_key": ["id"],
            "indexes": {
                "index_name": ["column1", "column2"]
            },
            "engine": "InnoDB",
            "charset": "utf8mb4",
            "comment": "表注释"
        }
    }
}
```

## 常见操作示例

### 示例 1：添加新字段

**场景**：为 `mini_product` 表添加"浏览次数"字段

**步骤**：
1. 打开 `database/schema.json`
2. 找到 `mini_product` 表的 `columns` 部分
3. 在 `columns` 对象中添加新字段：

```json
"mini_product": {
    "columns": {
        // ... 现有字段 ...
        "view_count": {
            "type": "int",
            "null": false,
            "default": 0,
            "comment": "浏览次数"
        }
    }
}
```

**注意**：
- 字段顺序：新字段会添加在表的最后，如果需要指定位置，需要重新生成 schema
- 默认值：如果字段不允许 NULL，必须提供 `default` 值

### 示例 2：修改字段类型

**场景**：将 `mini_product.name` 字段从 `varchar(200)` 改为 `varchar(300)`

**步骤**：
1. 找到 `mini_product.columns.name`
2. 修改 `type`：

```json
"name": {
    "type": "varchar(300)",  // 从 varchar(200) 改为 varchar(300)
    "null": false,
    "default": null,
    "comment": "产品名称"
}
```

**注意**：
- 类型变更可能导致数据丢失，请谨慎操作
- 建议先备份数据

### 示例 3：修改字段默认值

**场景**：修改 `mini_product.stock` 的默认值从 0 改为 10

**步骤**：
```json
"stock": {
    "type": "int",
    "null": true,
    "default": "10",  // 从 "0" 改为 "10"
    "comment": "库存"
}
```

### 示例 4：修改字段是否允许 NULL

**场景**：将 `mini_product.slug` 从允许 NULL 改为不允许 NULL

**步骤**：
```json
"slug": {
    "type": "varchar(200)",
    "null": false,  // 从 true 改为 false
    "default": "",  // 需要提供默认值
    "comment": "URL别名"
}
```

**注意**：
- 如果字段不允许 NULL，必须提供 `default` 值
- 如果表中已有 NULL 值，需要先处理数据

### 示例 5：添加索引

**场景**：为 `mini_product` 表添加 `createtime` 字段的索引

**步骤**：
1. 找到 `mini_product.indexes`
2. 添加新索引：

```json
"mini_product": {
    "indexes": {
        // ... 现有索引 ...
        "idx_createtime": ["createtime"]  // 添加新索引
    }
}
```

### 示例 6：添加唯一索引

**场景**：为 `mini_product.slug` 添加唯一索引

**步骤**：
```json
"indexes": {
    "slug": {
        "columns": ["slug"],
        "unique": true
    }
}
```

### 示例 7：创建新表

**场景**：创建 `mini_review` 评论表

**步骤**：
1. 在 `tables` 对象中添加新表定义：

```json
"mini_review": {
    "columns": {
        "id": {
            "type": "int",
            "null": false,
            "auto_increment": true,
            "comment": "ID"
        },
        "product_id": {
            "type": "int",
            "null": false,
            "comment": "产品ID"
        },
        "user_id": {
            "type": "int",
            "null": false,
            "comment": "用户ID"
        },
        "content": {
            "type": "text",
            "null": false,
            "comment": "评论内容"
        },
        "rating": {
            "type": "tinyint",
            "null": false,
            "default": 5,
            "comment": "评分(1-5)"
        },
        "createtime": {
            "type": "int",
            "null": true,
            "comment": "创建时间"
        }
    },
    "primary_key": ["id"],
    "indexes": {
        "product_id": ["product_id"],
        "user_id": ["user_id"]
    },
    "engine": "InnoDB",
    "charset": "utf8mb4",
    "comment": "评论表"
}
```

## 同步流程

### 方式 1：使用 Web UI（推荐）

1. **修改 schema.json**
   - 使用编辑器打开 `database/schema.json`
   - 按照上述示例修改表结构

2. **预览变更**
   - 访问：`http://localhost:8082/sync-ui.php`
   - 勾选"预览模式"复选框
   - 点击"执行同步"按钮
   - 查看执行日志中的 SQL 语句

3. **执行同步**
   - 确认 SQL 无误后，取消勾选"预览模式"
   - 再次点击"执行同步"按钮
   - 查看执行结果

### 方式 2：使用命令行

1. **修改 schema.json**（同上）

2. **预览变更**：
   ```bash
   docker compose exec -T php php /var/www/database/sync.php --dry-run
   ```

3. **执行同步**：
   ```bash
   docker compose exec -T php php /var/www/database/sync.php
   ```

## 字段类型参考

### 数值类型
- `int` 或 `int(11)` - 整数
- `tinyint` - 小整数（常用于布尔值）
- `decimal(10,2)` - 小数（10位总数，2位小数）
- `float` - 浮点数

### 字符串类型
- `varchar(100)` - 可变长度字符串（最大100字符）
- `char(10)` - 固定长度字符串（10字符）
- `text` - 长文本
- `longtext` - 超长文本

### 日期时间类型
- `datetime` - 日期时间
- `date` - 日期
- `time` - 时间
- `timestamp` - 时间戳

### 其他类型
- `enum('value1','value2')` - 枚举类型
- `json` - JSON 数据（MySQL 5.7+）

## 注意事项

### 1. JSON 格式
- 确保 JSON 语法正确（逗号、引号、括号）
- 建议使用支持 JSON 格式化的编辑器（VS Code、Sublime Text 等）
- 修改后可以用在线 JSON 验证工具检查

### 2. 字段顺序
- Schema 中的字段顺序会影响 `ALTER TABLE` 中字段的位置
- 新字段默认添加在最后
- 如果需要指定位置，需要调整 `columns` 对象中的顺序

### 3. 默认值格式
- 字符串默认值：`"default": "值"`
- 数字默认值：`"default": 0` 或 `"default": "0"`
- NULL 默认值：`"default": null` 或省略 `default` 字段
- 布尔值：使用 `tinyint(1)`，默认值 `"default": "0"` 或 `"default": "1"`

### 4. 删除字段/表
- **系统不会自动删除字段或表**
- 如果需要删除：
  1. 先备份数据
  2. 手动执行 SQL：`ALTER TABLE mini_product DROP COLUMN old_field;`
  3. 从 schema.json 中移除该字段定义

### 5. 类型变更风险
- 缩小类型范围（如 `varchar(200)` → `varchar(50)`）可能导致数据截断
- 类型不兼容（如 `varchar` → `int`）可能导致数据丢失
- **建议先备份数据，使用预览模式查看 SQL**

## 完整示例：添加产品浏览次数字段

### 步骤 1：修改 schema.json

找到 `mini_product` 表，在 `columns` 中添加：

```json
"view_count": {
    "type": "int",
    "null": false,
    "default": 0,
    "comment": "浏览次数"
}
```

完整示例（在 `columns` 对象中）：

```json
"mini_product": {
    "columns": {
        "id": { ... },
        "name": { ... },
        // ... 其他字段 ...
        "updatetime": {
            "type": "int",
            "null": true,
            "comment": "更新时间"
        },
        "view_count": {
            "type": "int",
            "null": false,
            "default": 0,
            "comment": "浏览次数"
        }
    }
}
```

### 步骤 2：预览 SQL

在 Web UI 中：
1. 勾选"预览模式"
2. 点击"执行同步"
3. 查看日志，应该看到类似：

```sql
ALTER TABLE `mini_product`
  ADD COLUMN `view_count` int NOT NULL DEFAULT 0 COMMENT '浏览次数';
```

### 步骤 3：执行同步

1. 取消勾选"预览模式"
2. 点击"执行同步"
3. 查看执行结果

### 步骤 4：验证

```sql
-- 检查字段是否添加成功
DESC mini_product;

-- 或查看表结构
SHOW CREATE TABLE mini_product;
```

## 常见问题

### Q: 修改后同步失败怎么办？

**A**: 
1. 检查 JSON 语法是否正确
2. 查看错误日志中的具体错误信息
3. 使用预览模式先查看 SQL
4. 确认字段类型是否兼容

### Q: 如何修改字段位置？

**A**: 
- Schema 中的字段顺序会影响 `ALTER TABLE` 中字段的位置
- 调整 `columns` 对象中字段的顺序即可
- 新字段会按照 schema 中的顺序添加

### Q: 可以同时修改多个表吗？

**A**: 
- 可以，在 schema.json 中修改多个表的定义
- 同步时会自动检测所有差异并生成 SQL
- 会按表顺序执行

### Q: 修改后需要重新生成 schema.json 吗？

**A**: 
- 不需要，直接修改 schema.json 即可
- 只有在数据库结构发生变化（手动修改）时，才需要重新生成 schema.json

## 最佳实践

1. **先预览后执行**：始终先使用预览模式查看 SQL
2. **备份数据**：重要变更前备份数据库
3. **版本控制**：将 schema.json 提交到 Git
4. **团队协作**：团队成员拉取代码后运行同步即可
5. **小步迭代**：一次修改一个表或少量字段，避免大规模变更


