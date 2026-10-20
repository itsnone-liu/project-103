# _isd_chain23.ps1 — 等链1(批1修复+批2)退出 → 启动批3
$ErrorActionPreference = 'Continue'
Set-Location 'D:\qjcNetDiskDownload\deepseek-harness\project\103'
$PY = 'D:\ComfyUI_windows_portable\python_embeded\python.exe'
function Test-Chain1Alive {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match '_isd_chain12\.ps1' -or $_.CommandLine -match '_isd_batch2\.py' } |
        Measure-Object | ForEach-Object { $_.Count -gt 0 }
}
Write-Output ("chain23: waiting for chain12 @ " + (Get-Date -Format 'HH:mm:ss'))
while (Test-Chain1Alive) { Start-Sleep 180 }
Write-Output ("chain23: chain12 exited @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain23: starting batch3..."
& $PY -X utf8 _isd_batch3.py 2>&1
Write-Output ("chain23: batch3 done @ " + (Get-Date -Format 'HH:mm:ss'))
