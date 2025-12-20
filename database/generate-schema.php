<?php
/**
 * Schema 生成工具
 * 
 * 从数据库反向生成 schema.json 文件
 * 
 * 使用方法:
 *   php database/generate-schema.php
 */

// 引入 ThinkPHP 框架
$isDocker = (strpos(__DIR__, '/var/www/database') === 0);

if ($isDocker) {
    $adminPath = '/var/www/html';
} else {
    $adminPath = __DIR__ . '/../backend/admin';
}

define('APP_PATH', $adminPath . '/application/');
define('RUNTIME_PATH', $adminPath . '/runtime/');
define('ROOT_PATH', $adminPath . '/');

require $adminPath . '/thinkphp/base.php';
\think\App::initCommon();

require_once __DIR__ . '/DatabaseInspector.php';

use think\Db;

class SchemaGenerator
{
    private $inspector;
    private $schemaFile;
    
    public function __construct()
    {
        $this->inspector = new DatabaseInspector('mini_');
        $this->schemaFile = __DIR__ . '/schema.json';
    }
    
    /**
     * 生成 Schema 文件
     */
    public function generate()
    {
        echo "========================================\n";
        echo "生成 Schema 文件\n";
        echo "========================================\n\n";
        
        try {
            $tables = $this->inspector->getTableNames();
            
            if (empty($tables)) {
                echo "⚠ 没有找到 MINI_ 前缀的表\n";
                return;
            }
            
            echo "发现 " . count($tables) . " 个表\n\n";
            
            $schema = [
                'version' => '1.0.0',
                'generated_at' => date('Y-m-d H:i:s'),
                'tables' => [],
            ];
            
            foreach ($tables as $tableName) {
                echo "处理表: {$tableName}\n";
                $definition = $this->inspector->getTableDefinition($tableName);
                
                if ($definition) {
                    $schema['tables'][$tableName] = $this->convertToSchemaFormat($tableName, $definition);
                }
            }
            
            // 写入文件
            $json = json_encode($schema, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            file_put_contents($this->schemaFile, $json);
            
            echo "\n========================================\n";
            echo "✓ Schema 文件已生成: {$this->schemaFile}\n";
            echo "========================================\n";
            
        } catch (\Exception $e) {
            echo "\n✗ 生成失败: " . $e->getMessage() . "\n";
            exit(1);
        }
    }
    
    /**
     * 转换为 Schema 格式
     */
    private function convertToSchemaFormat($tableName, $definition)
    {
        $schema = [
            'columns' => [],
            'primary_key' => $definition['primary_key'] ?? [],
            'indexes' => [],
            'engine' => $definition['engine'] ?? 'InnoDB',
            'charset' => $definition['charset'] ?? 'utf8mb4',
            'comment' => $definition['comment'] ?? '',
        ];
        
        // 转换字段
        foreach ($definition['columns'] as $colName => $colDef) {
            $schema['columns'][$colName] = [
                'type' => $colDef['type'],
                'null' => $colDef['null'],
                'default' => $colDef['default'],
                'auto_increment' => $colDef['auto_increment'],
                'comment' => $colDef['comment'],
            ];
            
            // 移除 null 的默认值
            if ($schema['columns'][$colName]['default'] === null && $colDef['null']) {
                unset($schema['columns'][$colName]['default']);
            }
            
            // 移除 false 的 auto_increment
            if (!$colDef['auto_increment']) {
                unset($schema['columns'][$colName]['auto_increment']);
            }
        }
        
        // 转换索引
        foreach ($definition['indexes'] as $idxName => $idxDef) {
            if ($idxDef['unique']) {
                $schema['indexes'][$idxName] = [
                    'columns' => $idxDef['columns'],
                    'unique' => true,
                ];
            } else {
                $schema['indexes'][$idxName] = $idxDef['columns'];
            }
        }
        
        return $schema;
    }
}

// 运行生成器
try {
    $generator = new SchemaGenerator();
    $generator->generate();
} catch (\Exception $e) {
    echo "\n✗ 错误: " . $e->getMessage() . "\n";
    exit(1);
}


