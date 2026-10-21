# _isd_chain24.ps1 — 等批3驱动退出 → 重跑批2(只补产 4-05/5-01)
$ErrorActionPreference = 'Continue'
Set-Location 'D:\qjcNetDiskDownload\deepseek-harness\project\103'
$PY = 'D:\ComfyUI_windows_portable\python_embeded\python.exe'
function Test-Batch3Alive {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match '_isd_batch3\.py' -or $_.CommandLine -match '_isd_chain23\.ps1' } |
        Measure-Object | ForEach-Object { $_.Count -gt 0 }
}
Write-Output ("chain24: waiting for batch3 @ " + (Get-Date -Format 'HH:mm:ss'))
while (Test-Batch3Alive) { Start-Sleep 180 }
Write-Output ("chain24: batch3 exited @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain24: batch2 repair round..."
& $PY -X utf8 _isd_batch2.py 2>&1
Write-Output ("chain24: batch2 repair done @ " + (Get-Date -Format 'HH:mm:ss'))
