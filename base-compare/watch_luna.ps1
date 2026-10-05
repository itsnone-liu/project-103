# watcher for case-b: wait for Luna scene -> install -> render -> sheet.
$ErrorActionPreference = 'Continue'
$base = 'D:\qjcNetDiskDownload\deepseek-harness\project\103\base-compare'
$case = "$base\case-b"
$scene = "$case\luna\butterfly.js"

# find the luna caller python pid (newest python started after case-b existed)
$deadline = (Get-Date).AddMinutes(40)
$caller = $null
while ((Get-Date) -lt $deadline -and -not $caller) {
    $caller = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like '*luna_call.py*' } |
        Sort-Object CreationDate -Descending | Select-Object -First 1
    if (-not $caller) { Start-Sleep 10 }
}
if ($caller) { Write-Host "caller pid=$($caller.ProcessId)" } else { Write-Host 'no caller found' }

# wait for output or caller exit
$deadline = (Get-Date).AddMinutes(60)
while ((Get-Date) -lt $deadline) {
    if ((Test-Path $scene) -and ((Get-Item $scene).Length -gt 200)) { break }
    if ($caller) {
        $p = Get-Process -Id $caller.ProcessId -ErrorAction SilentlyContinue
        if (-not $p) {
            Start-Sleep 5
            if (-not ((Test-Path $scene) -and ((Get-Item $scene).Length -gt 200))) {
                Write-Host 'LUNA caller died without output'
                Get-Content "$base\luna_call.err.log" -Tail 15 -ErrorAction SilentlyContinue
                exit 2
            }
            break
        }
    }
    Start-Sleep 30
}
if (-not (Test-Path $scene)) { Write-Host 'timeout waiting for Luna'; exit 3 }
Write-Host "Luna scene landed: $((Get-Item $scene).Length) bytes"

# install: copy scene, patch studio.html + config
$env:PYTHONIOENCODING = 'utf-8'
python - "$scene" "$case" @'
import re, sys
from pathlib import Path
scene = Path(sys.argv[1]); case = Path(sys.argv[2])
text = scene.read_text(encoding='utf-8')
(case / 'src' / 'scenes' / 'butterfly.js').write_text(text, encoding='utf-8')
m = re.search(r'duration\s*[:=]\s*([\d.]+).*?bpm\s*[:=]\s*(\d+)', text, re.S)
dur, bpm = (float(m.group(1)), int(m.group(2))) if m else (15.0, 120)
(case / 'src' / 'config.js').write_text(
    '// config.js: set by luna watcher.\n'
    f'const PROJECT = {{ duration: {dur:g}, bpm: {bpm}, offset: 0 }};\n',
    encoding='utf-8')
html = (case / 'studio.html').read_text(encoding='utf-8')
(case / 'studio.html').write_text(
    html.replace('src/scenes/demo.js', 'src/scenes/butterfly.js'),
    encoding='utf-8')
print(f'installed dur={dur:g} bpm={bpm}')
'@
if ($LASTEXITCODE -ne 0) { Write-Host 'install failed'; exit 4 }

$comp = 'D:\qjcNetDiskDownload\deepseek-harness\project\103\runs\architecture-smoke\node_modules\@remotion\compositor-win32-x64-msvc'
$env:PATH = "$comp;" + $env:PATH
Set-Location $case
node render.mjs --clip --out=out/luna_video.mp4 2>&1 | Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { Write-Host 'render failed'; exit 5 }

python "$base\make_sheet.py" luna 2>&1 | Select-Object -Last 2
Write-Host 'LUNA PIPELINE DONE'
