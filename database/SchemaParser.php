<?php
/**
 * Schema 解析器
 * 
 * 解析 JSON schema 文件并转换为标准化的表结构对象
 */

class SchemaParser
{
    private $schemaFile;
    private $schema;
    
    public function __construct($schemaFile)
    {
        $this->schemaFile = $schemaFile;
        $this->loadSchema();
    }
    
    /**
     * 加载 Schema 文件
     */
    private function loadSchema()
    {
        if (!file_exists($this->schemaFile)) {
            throw new \Exception("Schema 文件不存在: {$this->schemaFile}");
        }
        
        $content = file_get_contents($this->schemaFile);
        $this->schema = json_decode($content, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new \Exception("Schema JSON 解析失败: " . json_last_error_msg());
        }
        
        if (!isset($this->schema['tables']) || !is_array($this->schema['tables'])) {
            throw new \Exception("Schema 格式错误: 缺少 tables 字段");
        }
    }
    
    /**
     * 获取所有表名
     */
    public function getTableNames()
    {
        return array_keys($this->schema['tables']);
    }
    
    /**
     * 获取表结构定义
     */
    public function getTableDefinition($tableName)
    {
        if (!isset($this->schema['tables'][$tableName])) {
            return null;
        }
        
        return $this->schema['tables'][$tableName];
    }
    
    /**
     * 获取所有表定义
     */
    public function getAllTables()
    {
        return $this->schema['tables'];
    }
    
    /**
     * 获取 Schema 版本
     */
    public function getVersion()
    {
        return $this->schema['version'] ?? '1.0.0';
    }
    
    /**
     * 标准化字段定义
     */
    public function normalizeColumn($columnName, $columnDef)
    {
        $normalized = [
            'name' => $columnName,
            'type' => $columnDef['type'] ?? '',
            'null' => $columnDef['null'] ?? true,
            'default' => $columnDef['default'] ?? null,
            'auto_increment' => $columnDef['auto_increment'] ?? false,
            'comment' => $columnDef['comment'] ?? '',
        ];
        
        return $normalized;
    }
    
    /**
     * 标准化索引定义
     */
    public function normalizeIndex($indexName, $indexDef)
    {
        // 检查是否是关联数组格式：{"columns": [...], "unique": true}
        if (is_array($indexDef) && isset($indexDef['columns'])) {
            return [
                'name' => $indexName,
                'columns' => $indexDef['columns'],
                'unique' => $indexDef['unique'] ?? false,
            ];
        }
        // 检查是否是简单数组格式：["col1", "col2"]
        else if (is_array($indexDef) && !isset($indexDef['columns'])) {
            // 检查是否是索引数组（数字键）
            $isIndexedArray = array_keys($indexDef) === range(0, count($indexDef) - 1);
            if ($isIndexedArray) {
                return [
                    'name' => $indexName,
                    'columns' => $indexDef,
                    'unique' => false,
                ];
            } else {
                // 关联数组但没有 'columns' 键，可能是格式错误
                return [
                    'name' => $indexName,
                    'columns' => [],
                    'unique' => false,
                ];
            }
        } 
        // 字符串格式："col1"
        else if (is_string($indexDef)) {
            return [
                'name' => $indexName,
                'columns' => [$indexDef],
                'unique' => false,
            ];
        }
        
        // 默认返回空
        return [
            'name' => $indexName,
            'columns' => [],
            'unique' => false,
        ];
    }
    
    /**
     * 生成字段的 SQL 定义
     */
    public function generateColumnSql($column)
    {
        $sql = "`{$column['name']}` {$column['type']}";
        
        if (!$column['null']) {
            $sql .= " NOT NULL";
        }
        
        if ($column['auto_increment']) {
            $sql .= " AUTO_INCREMENT";
        } elseif ($column['default'] !== null) {
            // 只有在不是 AUTO_INCREMENT 时才设置默认值
            if (is_string($column['default'])) {
                // 转义单引号
                $default = str_replace("'", "''", $column['default']);
                $sql .= " DEFAULT '{$default}'";
            } elseif (is_numeric($column['default'])) {
                $sql .= " DEFAULT {$column['default']}";
            } elseif ($column['default'] === 'CURRENT_TIMESTAMP') {
                $sql .= " DEFAULT CURRENT_TIMESTAMP";
            } else {
                $sql .= " DEFAULT NULL";
            }
        } elseif ($column['null']) {
            // 允许 NULL 且没有默认值
            $sql .= " DEFAULT NULL";
        }
        
        if (!empty($column['comment'])) {
            // 转义单引号
            $comment = str_replace("'", "''", $column['comment']);
            $sql .= " COMMENT '{$comment}'";
        }
        
        return $sql;
    }
}



