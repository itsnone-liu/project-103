# _isd_chain12.ps1 — 等批1驱动退出 → 重跑批1(自动只补产失败段) → 启动批2
$ErrorActionPreference = 'Continue'
Set-Location 'D:\qjcNetDiskDownload\deepseek-harness\project\103'
$PY = 'D:\ComfyUI_windows_portable\python_embeded\python.exe'
function Test-DriverAlive {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match '_isd_batch1\.py' } | Measure-Object | ForEach-Object { $_.Count -gt 0 }
}
Write-Output ("chain: waiting for batch1 driver @ " + (Get-Date -Format 'HH:mm:ss'))
while (Test-DriverAlive) { Start-Sleep 120 }
Write-Output ("chain: batch1 driver exited @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain: repair round (failed segments only)..."
& $PY -X utf8 _isd_batch1.py 2>&1
Write-Output ("chain: repair done @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain: starting batch2..."
& $PY -X utf8 _isd_batch2.py 2>&1
Write-Output ("chain: batch2 done @ " + (Get-Date -Format 'HH:mm:ss'))
