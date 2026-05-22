# Outbound Guide 自动更新 - Windows 定时任务设置脚本
# 以管理员身份运行 PowerShell 执行此脚本

$TaskName = "OutboundGuideAutoUpdate"
$ScriptPath = Join-Path $PSScriptRoot "main.py"
$PythonPath = "python"  # 或指定完整路径如 "C:\Python311\python.exe"

# 检查是否以管理员身份运行
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "请以管理员身份运行 PowerShell!" -ForegroundColor Red
    exit 1
}

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $PSScriptRoot

# 创建任务触发器 - 每天 09:00 运行
$Trigger = New-ScheduledTaskTrigger -Daily -At "09:00"

# 创建任务设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force
    Write-Host "✓ 定时任务已创建: $TaskName" -ForegroundColor Green
    Write-Host "  运行时间: 每天 09:00" -ForegroundColor Cyan
    Write-Host "  脚本路径: $ScriptPath" -ForegroundColor Cyan
} catch {
    Write-Host "✗ 创建任务失败: $_" -ForegroundColor Red
}

# 显示任务信息
Write-Host "`n任务列表:" -ForegroundColor Yellow
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, NextRunTime | Format-Table

Write-Host "`n手动运行测试命令:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host "`n删除任务命令:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Cyan
