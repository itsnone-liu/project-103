# _isd_chain26.ps1 — 等批3补产轮(chain25)退出 → 启动批4
$ErrorActionPreference = 'Continue'
Set-Location 'D:\qjcNetDiskDownload\deepseek-harness\project\103'
$PY = 'D:\ComfyUI_windows_portable\python_embeded\python.exe'
function Test-Chain25Alive {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match '_isd_batch3\.py' -or $_.CommandLine -match '_isd_chain25\.ps1' } |
        Measure-Object | ForEach-Object { $_.Count -gt 0 }
}
Write-Output ("chain26: waiting for chain25 @ " + (Get-Date -Format 'HH:mm:ss'))
while (Test-Chain25Alive) { Start-Sleep 120 }
Write-Output ("chain26: chain25 exited @ " + (Get-Date -Format 'HH:mm:ss'))
Write-Output "chain26: starting batch4..."
& $PY -X utf8 _isd_batch4.py 2>&1
Write-Output ("chain26: batch4 done @ " + (Get-Date -Format 'HH:mm:ss'))
