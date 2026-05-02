# 梵木里小程序启动脚本
# 需要先安装微信开发者工具

Write-Host "=== 梵木里小程序启动助手 ===" -ForegroundColor Green
Write-Host ""

# 检查微信开发者工具
$wechatDevToolPath = "${env:ProgramFiles(x86)}\Tencent\微信web开发者工具\cli.bat"
if (-not (Test-Path $wechatDevToolPath)) {
    $wechatDevToolPath = "${env:ProgramFiles}\Tencent\微信web开发者工具\cli.bat"
}

if (-not (Test-Path $wechatDevToolPath)) {
    Write-Host "❌ 未找到微信开发者工具" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先下载安装：" -ForegroundColor Yellow
    Write-Host "https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "安装完成后，请开启服务端口："
    Write-Host "1. 打开微信开发者工具"
    Write-Host "2. 点击 设置 → 安全设置"
    Write-Host "3. 开启「服务端口」"
    exit 1
}

Write-Host "✓ 找到微信开发者工具" -ForegroundColor Green
Write-Host ""

# 项目路径
$projectPath = "D:\desktop\VANMOLY-SYS-V3.0\miniapp"

# 启动微信开发者工具
Write-Host "正在启动小程序项目..." -ForegroundColor Yellow
& $wechatDevToolPath open --project $projectPath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ 小程序已启动！" -ForegroundColor Green
    Write-Host ""
    Write-Host "提示：首次使用需要在微信开发者工具中：" -ForegroundColor Yellow
    Write-Host "  设置 → 项目设置 → 勾选「不校验合法域名」" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ 启动失败，请手动启动微信开发者工具" -ForegroundColor Red
}
