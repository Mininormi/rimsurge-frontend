# ============================================
# 数据库同步脚本 - Docker 版本 (PowerShell)
# ============================================

Write-Host "正在通过 Docker 执行数据库同步..." -ForegroundColor Cyan
Write-Host ""

# 检查容器是否运行
$containerStatus = docker compose ps php 2>&1 | Select-String "Up"
if (-not $containerStatus) {
    Write-Host "[错误] PHP 容器未运行，请先启动 Docker 容器：" -ForegroundColor Red
    Write-Host "  docker compose up -d" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

# 在容器内执行同步脚本
Write-Host "正在执行数据库同步..." -ForegroundColor Cyan
Write-Host ""

docker compose exec -T php php /var/www/database/sync.php

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[错误] 数据库同步失败" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
} else {
    Write-Host ""
    Write-Host "[成功] 数据库同步完成！" -ForegroundColor Green
    Write-Host ""
    Read-Host "按 Enter 键退出"
}



