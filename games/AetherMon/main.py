"""AetherMon — entry point.

Usage:
  python main.py                  # ASCII art mode (default)
  python main.py --mode text      # plain text
  python main.py --mode ascii     # ASCII art sprites (default)
  python main.py --mode block     # pixel-block art (requires sprite PNGs)
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH so 'src' package resolves
sys.path.insert(0, str(Path(__file__).parent))

from src.engine.game import Game
from src.ui.renderer import DisplayMode


def main() -> None:
    parser = argparse.ArgumentParser(description="AetherMon — creature battle RPG")
    parser.add_argument(
        "--mode",
        choices=["text", "ascii", "block"],
        default="ascii",
        help="Display mode: text / ascii / block (default: ascii)",
    )
    args = parser.parse_args()

    mode_map = {
        "text":  DisplayMode.TEXT,
        "ascii": DisplayMode.ASCII,
        "block": DisplayMode.BLOCK,
    }

    game = Game(mode=mode_map[args.mode])
    game.run()


if __name__ == "__main__":
    main()
