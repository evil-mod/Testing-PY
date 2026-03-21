---
name: ai-tools
description: "Use when: Setting up AI tools, MCP servers, GitHub CLI, or VS Code extensions for the AetherMon project. Extends the global evil-mod AI Tools instructions with game-specific context."
applyTo:
  - ".vscode/settings.json"
  - ".github/**"
  - "requirements.txt"
---

# AI Tools — AetherMon (Game Repo)

> Inherits all rules from `C:\evil-mod\.github\instructions\ai-tools.instructions.md`.
> This file adds AetherMon-specific context and shortcuts.

---

## Quick-Start Checklist (AetherMon)

```powershell
# 1. Activate venv
.\.venv\Scripts\Activate.ps1

# 2. Bootstrap pip if missing (Python 3.14 venv quirk)
.\.venv\Scripts\python.exe -m ensurepip --upgrade

# 3. Install dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Generate sprite assets
.\.venv\Scripts\python.exe scripts/download_assets.py

# 5. Run test suite (37 tests — all should pass)
.\.venv\Scripts\python.exe -m pytest tests/ -v

# 6. Smoke test (no interactive input)
.\.venv\Scripts\python.exe -c "from src.engine.game import Game; from src.ui.renderer import DisplayMode; Game(mode=DisplayMode.TEXT); print('OK')"

# 7. GitHub CLI — push to repo
$env:PATH += ";C:\Program Files\GitHub CLI"
gh auth status
```

---

## GitHub Repo Target

Repo path: `Testing/Games/AetherMon` (under `tristanbrice` org/account)

```powershell
$env:PATH += ";C:\Program Files\GitHub CLI"

# Create and push (first time)
gh repo create "tristanbrice/Testing-Games-AetherMon" `
  --public `
  --description "AetherMon - Pokemon-style creature battle RPG with classes, spells, and block-art sprites" `
  --source . `
  --remote origin `
  --push

# Subsequent pushes
git add -A
git commit -m "feat: <what changed>"
git push
```

---

## MCP & Extensions — Project Settings

Add GitHub MCP to `.vscode/settings.json` for Copilot integration:

```json
{
  "mcp": {
    "servers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-pat>"
        }
      }
    }
  }
}
```

**Note**: Requires Node.js on PATH. Run `node --version` to verify. If missing:  
```powershell
winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
# Restart terminal after install
```

---

## Validation — AetherMon Specific

After any change to the game code:

- ✅ `pytest tests/ -v` — all 37 tests pass
- ✅ Smoke test imports cleanly (no `ImportError`)
- ✅ `assets/sprites/creatures/*.png` — 14 sprites exist
- ✅ `assets/CREDITS.md` — present after running `download_assets.py`
- ✅ `git status` — no untracked or modified files before push
- ✅ `gh repo view` — confirms remote repo exists and is accessible

### Reporting Format
```
✅ ACTION: Ran pytest tests/ -v
🔍 VALIDATION: 37 collected, 0 errors
📊 RESULT: 37 passed in 0.13s
Status: PASS — ready to push
```
