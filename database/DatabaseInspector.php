<?php
/**
 * 数据库结构提取器
 * 
 * 从数据库中提取现有表的结构信息
 */

use think\Db;

class DatabaseInspector
{
    private $prefix;
    
    public function __construct($prefix = 'mini_')
    {
        $this->prefix = $prefix;
    }
    
    /**
     * 获取所有 MINI_ 前缀的表名
     */
    public function getTableNames()
    {
        $tables = Db::query("SHOW TABLES");
        $tableNames = [];
        
        foreach ($tables as $table) {
            $tableName = array_values($table)[0];
            if (strpos($tableName, $this->prefix) === 0) {
                // 排除 migrations 和 table_versions 表
                if ($tableName !== $this->prefix . 'migrations' && 
                    $tableName !== $this->prefix . 'table_versions') {
                    $tableNames[] = $tableName;
                }
            }
        }
        
        return $tableNames;
    }
    
    /**
     * 获取表结构定义
     */
    public function getTableDefinition($tableName)
    {
        if (!$this->tableExists($tableName)) {
            return null;
        }
        
        $columns = $this->getColumns($tableName);
        $indexes = $this->getIndexes($tableName);
        $primaryKey = $this->getPrimaryKey($tableName);
        $tableInfo = $this->getTableInfo($tableName);
        
        return [
            'columns' => $columns,
            'primary_key' => $primaryKey,
            'indexes' => $indexes,
            'engine' => $tableInfo['engine'] ?? 'InnoDB',
            'charset' => $tableInfo['charset'] ?? 'utf8mb4',
            'comment' => $tableInfo['comment'] ?? '',
        ];
    }
    
    /**
     * 检查字段是否存在
     */
    public function columnExists($tableName, $columnName)
    {
        try {
            $result = Db::query("SHOW COLUMNS FROM `{$tableName}` LIKE '{$columnName}'");
            return !empty($result);
        } catch (\Exception $e) {
            return false;
        }
    }
    
    /**
     * 检查表是否存在
     */
    public function tableExists($tableName)
    {
        try {
            $result = Db::query("SHOW TABLES LIKE '{$tableName}'");
            return !empty($result);
        } catch (\Exception $e) {
            return false;
        }
    }
    
    /**
     * 获取表的字段信息
     */
    private function getColumns($tableName)
    {
        $columns = [];
        $result = Db::query("SHOW FULL COLUMNS FROM `{$tableName}`");
        
        foreach ($result as $col) {
            $default = $col['Default'];
            
            // 处理默认值：NULL 字符串转为真正的 null
            if ($default === 'NULL' && $col['Null'] === 'YES') {
                $default = null;
            }
            
            $columns[$col['Field']] = [
                'name' => $col['Field'],
                'type' => $this->normalizeType($col['Type']),
                'null' => $col['Null'] === 'YES',
                'default' => $default,
                'auto_increment' => strpos($col['Extra'], 'auto_increment') !== false,
                'comment' => $col['Comment'] ?? '',
            ];
        }
        
        return $columns;
    }
    
    /**
     * 获取表的索引信息
     */
    private function getIndexes($tableName)
    {
        $indexes = [];
        $result = Db::query("SHOW INDEX FROM `{$tableName}`");
        
        foreach ($result as $idx) {
            $indexName = $idx['Key_name'];
            
            // 跳过主键
            if ($indexName === 'PRIMARY') {
                continue;
            }
            
            if (!isset($indexes[$indexName])) {
                $indexes[$indexName] = [
                    'name' => $indexName,
                    'columns' => [],
                    'unique' => $idx['Non_unique'] == 0,
                ];
            }
            
            $indexes[$indexName]['columns'][] = $idx['Column_name'];
        }
        
        return $indexes;
    }
    
    /**
     * 获取主键
     */
    private function getPrimaryKey($tableName)
    {
        $result = Db::query("SHOW INDEX FROM `{$tableName}` WHERE Key_name = 'PRIMARY'");
        
        $primaryKey = [];
        foreach ($result as $idx) {
            $primaryKey[] = $idx['Column_name'];
        }
        
        return $primaryKey;
    }
    
    /**
     * 获取表的基本信息（引擎、字符集、注释）
     */
    private function getTableInfo($tableName)
    {
        $result = Db::query("SHOW CREATE TABLE `{$tableName}`");
        
        if (empty($result)) {
            return [];
        }
        
        $createTable = $result[0]['Create Table'];
        
        // 提取引擎
        preg_match('/ENGINE=(\w+)/i', $createTable, $engineMatch);
        $engine = $engineMatch[1] ?? 'InnoDB';
        
        // 提取字符集
        preg_match('/CHARSET=(\w+)/i', $createTable, $charsetMatch);
        $charset = $charsetMatch[1] ?? 'utf8mb4';
        
        // 提取注释
        preg_match("/COMMENT='([^']*)'/i", $createTable, $commentMatch);
        $comment = $commentMatch[1] ?? '';
        
        return [
            'engine' => $engine,
            'charset' => $charset,
            'comment' => $comment,
        ];
    }
    
    /**
     * 标准化字段类型（去除长度等信息，用于对比）
     */
    private function normalizeType($type)
    {
        // 移除长度信息，只保留基本类型用于对比
        // 例如: varchar(100) -> varchar(100) (保留完整信息)
        return $type;
    }
    
    /**
     * 计算表结构的哈希值
     */
    public function getTableHash($tableName)
    {
        $definition = $this->getTableDefinition($tableName);
        if (!$definition) {
            return null;
        }
        
        // 移除可能变化的时间戳字段
        $normalized = json_encode($definition, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        return md5($normalized);
    }
}


