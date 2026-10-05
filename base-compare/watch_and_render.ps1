# watcher: wait for GLM scene -> install -> render -> contact sheet.
$ErrorActionPreference = 'Continue'
$base = 'D:\qjcNetDiskDownload\deepseek-harness\project\103\base-compare'
$case = "$base\case-a"
$scene = "$case\glm\butterfly.js"
$procId = 4380

# Phase 1: wait for GLM output (or caller process death with no output).
$deadline = (Get-Date).AddMinutes(95)
while ((Get-Date) -lt $deadline) {
    if ((Test-Path $scene) -and ((Get-Item $scene).Length -gt 200)) { break }
    $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $p) {
        Start-Sleep 5
        if (-not ((Test-Path $scene) -and ((Get-Item $scene).Length -gt 200))) {
            Write-Host "GLM caller died without output"
            Get-Content "$base\glm_call.err.log" -Tail 15 -ErrorAction SilentlyContinue
            exit 2
        }
        break
    }
    Start-Sleep 30
}
if (-not (Test-Path $scene)) { Write-Host 'timeout waiting for GLM'; exit 3 }
Write-Host "GLM scene landed: $((Get-Item $scene).Length) bytes"

# Phase 2: install + render + sheet.
$env:PYTHONIOENCODING = 'utf-8'
python "$base\glm_install_and_render.py" 2>&1 | Select-Object -Last 12
$code = $LASTEXITCODE
Write-Host "install_and_render exit=$code"
exit $code
