# AetherMon

A **Pokemon-style creature battle RPG** with expanded **magic classes and spells** — fully text-based with optional ASCII / full-color block-art picture mode rendered in your terminal.

---

## Features

| Feature | Details |
|---------|---------|
| Creature Classes | Warrior · Mage · Rogue · Priest · Ranger |
| Move Categories | Physical Skills · Magical Spells (use MP) · Status Effects |
| Display Modes | `text` / `ascii` / `block` (pixel sprite art in terminal) |
| Status Effects | Burn · Freeze · Poison · Stun · Sleep · Charm |
| Progression | EXP / Leveling · Stats grow on level-up |
| World | Starter choice · Rival battle · Wild encounters · Town heal/shop |
| Save / Load | JSON save file |

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Download free CC0 sprite images
python scripts/download_assets.py

# 4. Run the game
python main.py

# Optional flags
python main.py --mode ascii      # ASCII art mode (default)
python main.py --mode block      # Full-color block-art mode (requires sprites)
python main.py --mode text       # Plain text only
```

---

## Project Structure

```
AetherMon/
├── main.py                     # Entry point
├── requirements.txt
├── assets/
│   └── sprites/
│       ├── creatures/          # PNG sprites (downloaded by scripts/)
│       └── backgrounds/
├── scripts/
│   └── download_assets.py      # Downloads free CC0 sprite images
├── src/
│   ├── data/
│   │   ├── type_chart.py       # Type effectiveness matrix
│   │   ├── moves_data.py       # All moves / spells database
│   │   ├── classes_data.py     # Creature class definitions
│   │   └── creatures_data.py   # All creature definitions
│   ├── entities/
│   │   ├── creature.py         # Creature class
│   │   ├── player.py           # Player / inventory
│   │   └── move.py             # Move / spell runtime object
│   ├── engine/
│   │   ├── battle.py           # Battle state machine
│   │   ├── display.py          # Rendering (text / ascii / block)
│   │   └── game.py             # World / main game loop
│   └── ui/
│       ├── art.py              # Hardcoded ASCII art sprites
│       └── renderer.py         # Rich terminal renderer helpers
└── tests/
    ├── test_battle.py
    └── test_creatures.py
```

---

## Sprite Credits

Free CC0 sprites downloaded from:
- **Kenney.nl** — `https://www.kenney.nl/assets/rpg-urban-kit` (CC0)
- **OpenGameArt** — various CC0 packs by Buch, Sharm, etc.

All source images are public domain / CC0. See `assets/CREDITS.md` after running `download_assets.py`.

---

## License

MIT — do whatever you like with it.
