# Lancia il sito eCPPT in locale: rigenera docs/ + serve su http://127.0.0.1:8000
# Doppio click su questo file (o esecuzione manuale via PowerShell) -> sito attivo in browser.

$ErrorActionPreference = "Stop"

$venv   = Join-Path $PSScriptRoot "whisper-env"
$python = Join-Path $venv "Scripts\python.exe"
$build  = Join-Path $PSScriptRoot "build_site.py"
$root   = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path $python)) {
    Write-Host "ERROR: venv non trovato in $venv" -ForegroundColor Red
    Write-Host "Crealo prima con: py -3.11 -m venv $venv" -ForegroundColor Yellow
    exit 1
}

Set-Location $root

Write-Host "[1/2] Rigenero docs/ con build_site.py..." -ForegroundColor Cyan
& $python $build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "[2/2] Avvio mkdocs serve su http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Apri il link nel browser. Ctrl+C per fermare il server." -ForegroundColor Green
Write-Host ""

# Apre il browser dopo 2 secondi (in parallelo)
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

& $python -m mkdocs serve -a 127.0.0.1:8000
