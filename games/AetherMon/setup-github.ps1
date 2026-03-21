#!/usr/bin/env pwsh
# AetherMon Setup Script
# Run this ONCE after `gh auth login` to create the private repo and push.
#
# Steps:
#   1. Open a new terminal in C:\evil-mod\Game\AetherMon
#   2. Run: gh auth login   (choose GitHub.com → HTTPS → Login with web browser)
#   3. Run: .\setup-github.ps1

$repo = "aethermon"
$desc = "AetherMon - Pokemon-style creature battle RPG with classes, spells, and block-art sprites"
$venvPython = ".\.venv\Scripts\python.exe"

Write-Host "`n=== AetherMon GitHub Setup ===" -ForegroundColor Cyan

# 1. Create private repo + push
Write-Host "`n[1] Creating private GitHub repo and pushing..." -ForegroundColor Yellow
gh repo create "tristanbrice/$repo" `
    --private `
    --description $desc `
    --source . `
    --remote origin `
    --push

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] GitHub push failed. Make sure you ran: gh auth login" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Repo created: https://github.com/tristanbrice/$repo" -ForegroundColor Green

# 2. Remind about venv activation
Write-Host @"

=== To play the game ===
  Activate venv:   .\.venv\Scripts\activate
  ASCII art mode:  python main.py
  Block-art mode:  python main.py --mode block
  Plain text mode: python main.py --mode text
  Run tests:       .\.venv\Scripts\python.exe -m pytest tests/ -v

"@ -ForegroundColor Cyan
