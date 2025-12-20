<?php
/**
 * 诊断 sync-ui.php 访问问题
 * 使用方法: docker compose exec php php /var/www/database/diagnose-sync-ui.php
 */

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:10',
    'message' => 'Diagnostic script started',
    'data' => ['timestamp' => time(), 'php_version' => PHP_VERSION],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'A'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

echo "=== 数据库同步工具诊断 ===\n\n";

// 检查 1: PHP 版本和基本环境
echo "1. PHP 环境检查:\n";
echo "   PHP 版本: " . PHP_VERSION . "\n";
echo "   PHP 可执行文件: " . PHP_BINARY . "\n";
echo "   当前工作目录: " . getcwd() . "\n";
echo "   脚本路径: " . __FILE__ . "\n\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:25',
    'message' => 'PHP environment checked',
    'data' => [
        'php_version' => PHP_VERSION,
        'php_binary' => PHP_BINARY,
        'cwd' => getcwd(),
        'script_path' => __FILE__
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'A'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 检查 2: 文件是否存在
echo "2. 文件检查:\n";
$syncUiFile = __DIR__ . '/sync-ui.php';
$schemaFile = __DIR__ . '/schema.json';
echo "   sync-ui.php: " . ($syncUiFileExists = file_exists($syncUiFile) ? "✓ 存在" : "✗ 不存在") . "\n";
echo "   schema.json: " . ($schemaFileExists = file_exists($schemaFile) ? "✓ 存在" : "✗ 不存在") . "\n";
if ($syncUiFileExists) {
    echo "   sync-ui.php 权限: " . substr(sprintf('%o', fileperms($syncUiFile)), -4) . "\n";
}
echo "\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:42',
    'message' => 'File existence checked',
    'data' => [
        'sync_ui_exists' => $syncUiFileExists,
        'schema_exists' => $schemaFileExists,
        'sync_ui_perms' => $syncUiFileExists ? substr(sprintf('%o', fileperms($syncUiFile)), -4) : null
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'B'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 检查 3: 端口监听状态
echo "3. 端口监听检查:\n";
$port = 8082;
$checkPortCmd = "netstat -tlnp 2>/dev/null | grep :$port || ss -tlnp 2>/dev/null | grep :$port || echo '无法检查端口'";
$portOutput = shell_exec($checkPortCmd);
echo "   端口 $port 监听状态:\n";
if ($portOutput && trim($portOutput) !== '无法检查端口') {
    echo "   " . trim($portOutput) . "\n";
    $portListening = true;
} else {
    echo "   ✗ 端口未监听\n";
    $portListening = false;
}
echo "\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:60',
    'message' => 'Port listening status checked',
    'data' => [
        'port' => $port,
        'is_listening' => $portListening,
        'port_output' => trim($portOutput ?? '')
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'B'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 检查 4: PHP 内置服务器进程
echo "4. PHP 内置服务器进程检查:\n";
$psOutput = shell_exec("ps aux | grep 'php -S' | grep -v grep || echo '无进程'");
if ($psOutput && trim($psOutput) !== '无进程') {
    echo "   找到进程:\n";
    echo "   " . trim($psOutput) . "\n";
    $serverRunning = true;
} else {
    echo "   ✗ 未找到 PHP 内置服务器进程\n";
    $serverRunning = false;
}
echo "\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:78',
    'message' => 'PHP server process checked',
    'data' => [
        'server_running' => $serverRunning,
        'ps_output' => trim($psOutput ?? '')
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'A'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 检查 5: 测试本地访问
echo "5. 本地访问测试:\n";
$testUrl = "http://localhost:$port/sync-ui.php";
$ch = curl_init($testUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

if ($httpCode == 200) {
    echo "   ✓ 本地访问成功 (HTTP $httpCode)\n";
    $localAccessOk = true;
} else {
    echo "   ✗ 本地访问失败\n";
    echo "   HTTP 状态码: " . ($httpCode ?: 'N/A') . "\n";
    if ($curlError) {
        echo "   错误信息: $curlError\n";
    }
    $localAccessOk = false;
}
echo "\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:105',
    'message' => 'Local access test completed',
    'data' => [
        'url' => $testUrl,
        'http_code' => $httpCode,
        'curl_error' => $curlError,
        'access_ok' => $localAccessOk,
        'response_length' => strlen($response ?? '')
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'C'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 检查 6: Docker 端口映射（需要从宿主机检查，这里只提示）
echo "6. Docker 端口映射检查:\n";
echo "   请在宿主机运行: docker compose ps php | grep 8082\n";
echo "   应该看到: 0.0.0.0:8082->8082/tcp\n\n";

// #region agent log
$logData = [
    'location' => 'diagnose-sync-ui.php:120',
    'message' => 'Diagnostic completed',
    'data' => [
        'summary' => [
            'files_ok' => $syncUiFileExists && $schemaFileExists,
            'port_listening' => $portListening,
            'server_running' => $serverRunning,
            'local_access_ok' => $localAccessOk
        ]
    ],
    'timestamp' => time() * 1000,
    'sessionId' => 'debug-session',
    'runId' => 'run1',
    'hypothesisId' => 'A'
];
@file_put_contents('/tmp/debug-sync-ui.log', json_encode($logData) . "\n", FILE_APPEND);
// #endregion

// 总结和建议
echo "=== 诊断总结 ===\n";
if (!$serverRunning) {
    echo "⚠ 问题: PHP 内置服务器未运行\n";
    echo "解决方案: 运行以下命令启动服务器:\n";
    echo "  docker compose exec -d php php -S 0.0.0.0:8082 -t /var/www/database sync-ui.php\n\n";
} elseif (!$portListening) {
    echo "⚠ 问题: 端口未监听\n";
    echo "可能原因: 服务器启动失败或端口被占用\n\n";
} elseif (!$localAccessOk) {
    echo "⚠ 问题: 本地访问失败\n";
    echo "可能原因: 服务器配置问题或文件权限问题\n\n";
} else {
    echo "✓ 所有检查通过，服务器应该正常运行\n";
    echo "如果宿主机仍无法访问，请检查:\n";
    echo "  1. Docker 端口映射: docker compose ps php\n";
    echo "  2. 防火墙设置\n";
    echo "  3. 浏览器缓存\n\n";
}

echo "诊断完成！\n";

