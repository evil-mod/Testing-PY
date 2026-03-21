"""Rich terminal renderer for AetherMon.

Handles three display modes:
  text  — plain text, no colour
  ascii — ASCII art sprites + Rich styled output
  block — pixel-block sprites from PNG files (requires Pillow + sprite PNGs)
"""
from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

from src.ui.art import get_sprite, side_by_side
from src.data import TYPE_COLORS

if TYPE_CHECKING:
    from src.entities import Creature

SPRITE_DIR = Path("assets/sprites/creatures")

console = Console()


class DisplayMode(Enum):
    TEXT  = "text"
    ASCII = "ascii"
    BLOCK = "block"


# ── Colour helpers ──────────────────────────────────────────────────────────

def type_tag(t: str) -> Text:
    color = TYPE_COLORS.get(t, "white")
    return Text(f"[{t}]", style=f"bold {color}")


def hp_bar(current: int, maximum: int, width: int = 20) -> Text:
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * width)
    if ratio > 0.5:
        style = "bold green"
    elif ratio > 0.25:
        style = "bold yellow"
    else:
        style = "bold red"
    bar = "█" * filled + "░" * (width - filled)
    return Text(f"[{bar}] {current}/{maximum}", style=style)


def mp_bar(current: int, maximum: int, width: int = 20) -> Text:
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * width)
    bar = "▓" * filled + "░" * (width - filled)
    return Text(f"[{bar}] {current}/{maximum}", style="bold blue")


# ── Block (pixel) sprite renderer ──────────────────────────────────────────

def _load_block_sprite(name: str, width: int = 20, height: int = 10) -> list[str] | None:
    """Load a PNG and convert to ANSI upper-half-block lines. Returns None if unavailable."""
    try:
        from PIL import Image
    except ImportError:
        return None

    sprite_path = SPRITE_DIR / f"{name.lower()}.png"
    if not sprite_path.exists():
        return None

    img = Image.open(sprite_path).convert("RGBA")
    img = img.resize((width, height * 2), Image.NEAREST)

    lines: list[str] = []
    pixels = img.load()
    for y in range(0, height * 2, 2):
        line = ""
        for x in range(width):
            r1, g1, b1, a1 = pixels[x, y]
            r2, g2, b2, a2 = pixels[x, y + 1] if y + 1 < height * 2 else (0, 0, 0, 0)
            top    = f"\033[38;2;{r1};{g1};{b1}m" if a1 > 10 else "\033[0m"
            bottom = f"\033[48;2;{r2};{g2};{b2}m" if a2 > 10 else "\033[0m"
            line += top + bottom + "▀\033[0m"
        lines.append(line)
    return lines


# ── Main renderer class ─────────────────────────────────────────────────────

class Renderer:
    def __init__(self, mode: DisplayMode = DisplayMode.ASCII) -> None:
        self.mode = mode

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self, prompt: str = "\nPress [Enter] to continue...") -> None:
        input(prompt)

    def title_screen(self) -> None:
        self.clear()
        title = Text()
        title.append("  ╔══════════════════════════════╗\n", style="bold cyan")
        title.append("  ║       A E T H E R M O N      ║\n", style="bold magenta")
        title.append("  ║  Creature Battle RPG  v1.0   ║\n", style="bold yellow")
        title.append("  ╚══════════════════════════════╝\n", style="bold cyan")
        title.append("\n  Classes · Spells · Creatures\n", style="italic white")
        console.print(title)

    def print(self, msg: str, style: str = "") -> None:
        if style:
            console.print(msg, style=style)
        else:
            console.print(msg)

    def ask(self, prompt: str) -> str:
        return console.input(f"[bold cyan]{prompt}[/bold cyan] ")

    def menu(self, title: str, options: list[str]) -> int:
        """Display a numbered menu and return 0-based selection index."""
        self.print(f"\n[bold yellow]{title}[/bold yellow]")
        for i, opt in enumerate(options, 1):
            self.print(f"  [bold cyan]{i}.[/bold cyan] {opt}")
        while True:
            raw = self.ask(f"Choose (1–{len(options)}): ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return idx
            self.print(f"[red]Please enter a number between 1 and {len(options)}.[/red]")

    # ── Creature card ────────────────────────────────────────────────────────

    def creature_card(self, creature: "Creature", title_prefix: str = "") -> Panel:
        from src.data import TYPE_COLORS
        t = creature
        name_style = TYPE_COLORS.get(t.types[0], "white")
        type_str = " / ".join(t.types)

        content = Text()
        content.append(f"{title_prefix}{t.name}", style=f"bold {name_style}")
        content.append(f"  Lv{t.level}  [{t.creature_class_name}]\n", style="white")
        content.append(f"Type: {type_str}\n", style="dim")
        content.append("HP  ")
        content.append_text(hp_bar(t.current_hp, t.max_hp, 18))
        content.append("\nMP  ")
        content.append_text(mp_bar(t.current_mp, t.max_mp, 18))
        if t.status:
            content.append(f"\nStatus: {t.status.upper()}", style="bold red")

        return Panel(content, border_style="bright_black", padding=(0, 1))

    # ── Battle scene ─────────────────────────────────────────────────────────

    def battle_scene(
        self,
        player_creature: "Creature",
        enemy_creature: "Creature",
    ) -> None:
        self.clear()

        if self.mode == DisplayMode.TEXT:
            pc, ec = player_creature, enemy_creature
            self.print(f"[bold]{'─'*45}[/bold]")
            self.print(
                f"[bold yellow]Enemy:[/bold yellow] {ec.name} Lv{ec.level} "
                f"HP: {ec.current_hp}/{ec.max_hp}"
            )
            self.print(
                f"[bold green]Your:[/bold green]  {pc.name} Lv{pc.level} "
                f"HP: {pc.current_hp}/{pc.max_hp}  "
                f"MP: {pc.current_mp}/{pc.max_mp}"
            )
            self.print(f"[bold]{'─'*45}[/bold]")
            return

        # ASCII / BLOCK mode
        if self.mode == DisplayMode.BLOCK:
            enemy_lines = _load_block_sprite(enemy_creature.name)
            player_lines = _load_block_sprite(player_creature.name)
        else:
            enemy_lines = None
            player_lines = None

        # Fallback to ASCII art
        if enemy_lines is None:
            enemy_lines = get_sprite(enemy_creature.name)
        if player_lines is None:
            player_lines = get_sprite(player_creature.name)

        # Render side-by-side
        combined = side_by_side(enemy_creature.name, player_creature.name, padding=8)
        sprite_text = Text()
        for line in combined:
            sprite_text.append(line + "\n", style="bright_white")

        panel = Panel(
            sprite_text,
            title=f"[bold red]{enemy_creature.name}[/bold red]  vs  [bold green]{player_creature.name}[/bold green]",
            border_style="bright_cyan",
            padding=(0, 2),
        )
        console.print(panel)

        # HP / MP bars
        left = self.creature_card(enemy_creature,  title_prefix="⚔ Enemy: ")
        right = self.creature_card(player_creature, title_prefix="🛡 Yours: ")
        console.print(Columns([left, right], equal=True))

    # ── Move menu ────────────────────────────────────────────────────────────

    def move_menu(self, creature: "Creature") -> str:
        """Interactive move selection. Returns chosen move name."""
        from src.data import MOVES, TYPE_COLORS
        self.print("\n[bold yellow]┌─ BATTLE MENU ─────────────────────┐[/bold yellow]")
        self.print("[bold]  1.[/bold] Fight    [bold]2.[/bold] Spell    [bold]3.[/bold] Item    [bold]4.[/bold] Ball    [bold]5.[/bold] Run")
        self.print("[bold yellow]└────────────────────────────────────┘[/bold yellow]")

        while True:
            choice = self.ask("Action: ").strip()
            if choice in ("1", "2", "3", "4", "5"):
                return choice
            self.print("[red]Enter 1–5[/red]")

    def fight_menu(self, creature: "Creature") -> str | None:
        """Show physical moves, return chosen move name or None (cancel)."""
        from src.data import MOVES, TYPE_COLORS

        phys_moves = [
            m for m in creature.move_pool
            if m in MOVES and MOVES[m].category == "physical"
        ]
        if not phys_moves:
            self.print("[dim]No physical moves available.[/dim]")
            return None

        self.print("\n[bold red]─── FIGHT ──────────────────[/bold red]")
        options = []
        for m in phys_moves:
            mv = MOVES[m]
            pp = creature.move_pp.get(m, 0)
            color = TYPE_COLORS.get(mv.move_type, "white")
            can = "✓" if creature.can_use_move(m) else "✗"
            options.append(
                f"[{color}]{m}[/{color}]  [dim]PP:{pp}/{mv.pp}  Pwr:{mv.power}  {can}[/dim]"
            )
        options.append("[dim]← Back[/dim]")

        idx = self.menu("Choose physical move:", options)
        if idx == len(options) - 1:
            return None
        return phys_moves[idx]

    def spell_menu(self, creature: "Creature") -> str | None:
        """Show magic spells, return chosen move name or None (cancel)."""
        from src.data import MOVES, TYPE_COLORS

        spell_moves = [
            m for m in creature.move_pool
            if m in MOVES and MOVES[m].category in ("special", "status")
        ]
        if not spell_moves:
            self.print("[dim]No spells available.[/dim]")
            return None

        self.print("\n[bold blue]─── SPELLS ─────────────────[/bold blue]")
        options = []
        for m in spell_moves:
            mv = MOVES[m]
            pp = creature.move_pp.get(m, 0)
            color = TYPE_COLORS.get(mv.move_type, "white")
            can = "✓" if creature.can_use_move(m) else "✗"
            mp_cost = f"MP:{mv.mp_cost}" if mv.mp_cost else "free"
            options.append(
                f"[{color}]{m}[/{color}]  [dim]PP:{pp}/{mv.pp}  Pwr:{mv.power}  {mp_cost}  {can}[/dim]"
            )
        options.append("[dim]← Back[/dim]")

        idx = self.menu("Choose spell / status move:", options)
        if idx == len(options) - 1:
            return None
        return spell_moves[idx]

    def item_menu(self, player) -> tuple[str, "Creature"] | None:
        """Choose an item + target. Returns (item, creature) or None."""
        items = [k for k, v in player.bag.items() if v > 0]
        if not items:
            self.print("[dim]Bag is empty.[/dim]")
            return None

        item_opts = [f"{i} × {player.bag[i]}" for i in items] + ["← Back"]
        idx = self.menu("Choose item:", item_opts)
        if idx == len(item_opts) - 1:
            return None
        chosen_item = items[idx]

        party_opts = [f"{c.name} Lv{c.level}  HP:{c.current_hp}/{c.max_hp}" for c in player.party]
        party_opts.append("← Back")
        pidx = self.menu("Use on:", party_opts)
        if pidx == len(party_opts) - 1:
            return None
        return chosen_item, player.party[pidx]

    # ── Battle result ────────────────────────────────────────────────────────

    def battle_result(self, messages: list[str], exp: int = 0, level_ups: list[str] = None) -> None:
        for msg in messages:
            self.print(f"  {msg}")
        if exp:
            self.print(f"\n[bold yellow]EXP gained: {exp}[/bold yellow]")
        for lmsg in (level_ups or []):
            self.print(f"[bold magenta]{lmsg}[/bold magenta]")

    # ── Info panels ──────────────────────────────────────────────────────────

    def show_party(self, party: list["Creature"]) -> None:
        self.print("\n[bold yellow]── Your Party ──────────────────────[/bold yellow]")
        for i, c in enumerate(party, 1):
            fainted = "[dim red]FAINTED[/dim red]" if c.is_fainted() else ""
            self.print(
                f"  {i}. [bold]{c.name}[/bold] Lv{c.level}  "
                f"HP:{c.current_hp}/{c.max_hp}  "
                f"MP:{c.current_mp}/{c.max_mp}  "
                f"[{c.creature_class_name}] {fainted}"
            )

    def show_creature_detail(self, c: "Creature") -> None:
        from src.data import TYPE_COLORS, MOVES
        table = Table(title=f"{c.name}  Lv{c.level}", box=box.ROUNDED)
        table.add_column("Stat", style="bold cyan")
        table.add_column("Value")
        table.add_row("Types", " / ".join(c.types))
        table.add_row("Class", c.creature_class_name)
        table.add_row("HP", f"{c.current_hp} / {c.max_hp}")
        table.add_row("MP", f"{c.current_mp} / {c.max_mp}")
        table.add_row("ATK", str(c.atk))
        table.add_row("DEF", str(c.def_))
        table.add_row("SPA", str(c.spa))
        table.add_row("SPD", str(c.spd))
        table.add_row("SPE", str(c.spe))
        table.add_row("EXP", f"{c.exp} / {c.exp_to_next}")
        table.add_row("Status", c.status or "None")
        table.add_row("Passive", c.creature_class.passive)
        console.print(table)

        # Moves
        self.print("[bold]Move pool:[/bold]")
        for m in c.move_pool:
            if m not in MOVES:
                continue
            mv = MOVES[m]
            pp = c.move_pp.get(m, 0)
            color = TYPE_COLORS.get(mv.move_type, "white")
            avail = "✓" if c.can_use_move(m) else "✗"
            self.print(
                f"  [{color}]{m}[/{color}]  {mv.category}  "
                f"Pwr:{mv.power}  PP:{pp}/{mv.pp}  {avail}  {mv.description}"
            )
