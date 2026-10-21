# _isd_chain25.ps1 — 等批2补产轮(chain24)退出 → 重跑批3(只补产 5-02/5-03/6-02)
$ErrorActionPreference = 'Continue'
Set-Location 'D:\qjcNetDiskDownload\deepseek-harness\project\103'
$PY = 'D:\ComfyUI_windows_portable\python_embeded\python.exe'
function Test-RepairAlive {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match '_isd_batch2\.py' -or $_.CommandLine -match '_isd_chain24\.ps1' } |
        Measure-Object | ForEach-Object { $_.Count -gt 0 }
}
Write-Output ("chain25: waiting for chain24/batch2-repair @ " + (Get-Date -Format 'HH:mm:ss'))
while (Test-RepairAlive) { Start-Sleep 120 }
Write-Output ("chain25: batch2 repair exited @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain25: batch3 repair round..."
& $PY -X utf8 _isd_batch3.py 2>&1
Write-Output ("chain25: batch3 repair done @ " + (Get-Date -Format 'HH:mm:ss'))
