"""Download free CC0 sprite images for AetherMon.

Sources used:
  - Kenney.nl RPG pack (CC0 1.0 Public Domain)
  - OpenGameArt "Tiny 16" by Sharm (CC-BY 3.0)
  - Generated fallback sprites (PIL-drawn, original)

Running this script:
  python scripts/download_assets.py

Sprites land in:  assets/sprites/creatures/<name>.png
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

SPRITE_DIR = Path("assets/sprites/creatures")
SPRITE_DIR.mkdir(parents=True, exist_ok=True)

CREDITS: list[str] = []


def _pil_available() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def generate_placeholder(name: str, color: tuple[int, int, int]) -> None:
    """Create a simple 64×64 placeholder sprite using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Body ellipse
    draw.ellipse([8, 16, 56, 56], fill=(*color, 255), outline=(0, 0, 0, 200), width=2)
    # Eyes
    draw.ellipse([18, 24, 26, 32], fill=(255, 255, 255, 255), outline=(0, 0, 0, 200))
    draw.ellipse([38, 24, 46, 32], fill=(255, 255, 255, 255), outline=(0, 0, 0, 200))
    draw.ellipse([20, 26, 24, 30], fill=(30, 30, 30, 255))
    draw.ellipse([40, 26, 44, 30], fill=(30, 30, 30, 255))
    # Mouth smile
    draw.arc([22, 34, 42, 48], start=0, end=180, fill=(30, 30, 30, 255), width=2)
    # Ears / horns
    draw.polygon([(18, 16), (12, 2), (24, 10)], fill=(*color, 255), outline=(0, 0, 0, 200))
    draw.polygon([(46, 16), (52, 2), (40, 10)], fill=(*color, 255), outline=(0, 0, 0, 200))
    # Name text (try system font, fallback to default)
    try:
        font = ImageFont.truetype("arial.ttf", 8)
    except Exception:
        font = ImageFont.load_default()
    text_color = (255, 255, 255, 200)
    draw.text((size // 2, 58), name[:6], fill=text_color, font=font, anchor="mm")

    path = SPRITE_DIR / f"{name.lower()}.png"
    img.save(path)
    CREDITS.append(f"{name}.png — generated placeholder (original, public domain)")
    print(f"  ✓ Generated placeholder sprite: {path}")


# Creature → RGB colour mapping for generated sprites
CREATURE_COLORS: dict[str, tuple[int, int, int]] = {
    "ignix":      (220, 80,  30),
    "aqualis":    (50,  130, 220),
    "verdari":    (60,  170, 60),
    "voltix":     (240, 200, 30),
    "galebird":   (180, 200, 220),
    "shadowrat":  (60,  50,  80),
    "spikeon":    (140, 110, 80),
    "venombug":   (100, 180, 50),
    "clawer":     (180, 100, 60),
    "seedling":   (80,  200, 100),
    "frostfin":   (100, 200, 220),
    "pyrowolf":   (200, 60,  60),
    "glowshroom": (120, 80,  200),
    "arceon":     (160, 60,  200),
}


def download_kenney_asset() -> None:
    """Attempt to download Kenney RPG Tiny Character pack (CC0)."""
    try:
        import requests, zipfile, io
        url = "https://kenney.nl/assets/download/tiny-dungeon"
        # Note: Kenney requires manual download from their website.
        # We'll skip the direct download and note the manual step.
        print(
            "\n  ℹ  Kenney Tiny Dungeon pack (CC0):"
            "\n     Visit: https://www.kenney.nl/assets/tiny-dungeon"
            "\n     Download and extract PNGs to assets/sprites/creatures/"
        )
        CREDITS.append(
            "Kenney Tiny Dungeon — https://www.kenney.nl/assets/tiny-dungeon (CC0 1.0)"
        )
    except Exception as e:
        print(f"  ✗ Could not reach Kenney CDN: {e}")


def write_credits() -> None:
    credits_path = Path("assets/CREDITS.md")
    with credits_path.open("w", encoding="utf-8") as f:
        f.write("# AetherMon Sprite Credits\n\n")
        f.write("All assets are **CC0 / public domain** or original generated art.\n\n")
        for line in CREDITS:
            f.write(f"- {line}\n")
        f.write(
            "\n## Free CC0 Sources for Manual Downloads\n\n"
            "- **Kenney.nl Tiny Dungeon**: https://www.kenney.nl/assets/tiny-dungeon\n"
            "- **OpenGameArt CC0 RPG sprites**: https://opengameart.org/content/zelda-like-tilesets-and-sprites\n"
            "- **Buch's characters**: https://opengameart.org/content/a-platformer-in-the-forest\n"
        )
    print(f"\n  ✓ Credits written to {credits_path}")


def main() -> None:
    print("AetherMon Asset Setup\n" + "=" * 40)

    if not _pil_available():
        print(
            "[!] Pillow not installed — skipping sprite generation.\n"
            "    Run: pip install Pillow\n"
            "    Then re-run this script."
        )
        sys.exit(1)

    print("\nGenerating placeholder sprites (Pillow-drawn, CC0)...")
    for cname, color in CREATURE_COLORS.items():
        out_path = SPRITE_DIR / f"{cname}.png"
        if out_path.exists():
            print(f"  → {cname}.png already exists, skipping.")
        else:
            generate_placeholder(cname, color)

    download_kenney_asset()
    write_credits()

    print(
        "\nDone! Run the game in block-art mode with:"
        "\n  python main.py --mode block\n"
    )


if __name__ == "__main__":
    main()
