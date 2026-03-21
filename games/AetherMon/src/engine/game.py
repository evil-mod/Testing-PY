"""AetherMon world / game state machine.

Drives the overworld: starter selection, rival battle, route exploration,
town healing, shopping, and continuous wild encounters.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from src.engine.battle import BattleOutcome
from src.engine.display import run_battle_ui
from src.entities.creature import Creature
from src.entities.player import Player
from src.data.creatures_data import CREATURES, WILD_ENCOUNTERS
from src.ui.renderer import Renderer, DisplayMode

SAVE_PATH = "saves/save.json"

RIVAL_STARTER_MAP: dict[str, str] = {
    "Ignix":   "Rival_Aqualis",
    "Aqualis": "Rival_Verdari",
    "Verdari": "Rival_Ignix",
}

STARTER_NAMES = ["Ignix", "Aqualis", "Verdari"]

SHOP_ITEMS: dict[str, int] = {
    "AetherBall": 40,
    "Potion": 80,
    "Elixir": 120,
    "Antidote": 60,
    "Revive": 300,
}


class Game:
    def __init__(self, mode: DisplayMode = DisplayMode.ASCII) -> None:
        self.renderer = Renderer(mode)
        self.player: Player | None = None

    # ── Entry points ────────────────────────────────────────────────────────

    def run(self) -> None:
        self.renderer.title_screen()
        self.renderer.print(
            "\n[bold]Display mode:[/bold] "
            f"[cyan]{self.renderer.mode.value}[/cyan]"
            "  (launch with --mode text|ascii|block to change)\n"
        )
        self.renderer.pause()

        choice = self.renderer.menu(
            "Main Menu",
            ["New Game", "Load Game", "How to Play", "Quit"],
        )

        if choice == 0:
            self._new_game()
        elif choice == 1:
            self._load_game()
        elif choice == 2:
            self._how_to_play()
        else:
            self.renderer.print("[dim]See you next time, trainer![/dim]")
            sys.exit(0)

    def _new_game(self) -> None:
        self.renderer.clear()
        self.renderer.print(
            "[bold][cyan]Prof. Aethon:[/cyan][/bold] Welcome, young Trainer, "
            "to the world of [bold magenta]AetherMon[/bold magenta]!\n"
            "Magical creatures dwell everywhere — as companions, as challenges.\n"
            "Pick your partner and begin your journey!\n"
        )
        name = self.renderer.ask("What is your name, Trainer? ").strip() or "Red"
        self.player = Player(name)
        self.renderer.print(f"[bold green]Prof. Aethon:[/bold green] Great — {name}! Let's begin.\n")

        rival_name = self.renderer.ask("Your rival's name? ").strip() or "Blue"
        self.player.rival_name = rival_name

        self._choose_starter()
        self._rival_intro_battle()
        self._overworld()

    def _load_game(self) -> None:
        loaded = Player.load(SAVE_PATH)
        if loaded is None:
            self.renderer.print("[red]No save file found.[/red]")
            self.renderer.pause()
            self.run()
            return
        self.player = loaded
        self.renderer.print(f"[bold green]Welcome back, {self.player.name}![/bold green]")
        self.renderer.pause()
        self._overworld()

    def _how_to_play(self) -> None:
        self.renderer.clear()
        self.renderer.print("""
[bold cyan]HOW TO PLAY[/bold cyan]

[yellow]Battle Menu:[/yellow]
  1. Fight  — choose a physical move (uses PP)
  2. Spell  — choose a magic spell (uses PP + MP)
  3. Item   — use an item from your bag
  4. Ball   — throw an AetherBall to capture wild creatures
  5. Run    — flee from wild battles

[yellow]Creature Classes:[/yellow]
  Warrior   — high ATK/DEF, Iron Will passive
  Mage      — high SPA, Arcane Surge passive
  Rogue     — high SPE, +15% crit chance
  Priest    — high HP, heals 5% per turn
  Ranger    — balanced, status accuracy +20%
  Berserker — ATK rises as HP falls
  Shaman    — elemental + healing hybrid

[yellow]Types:[/yellow]  Fire · Water · Grass · Electric · Ice · Fighting
          Poison · Ground · Flying · Psychic · Bug · Rock
          Ghost · Dragon · Dark · Steel · Arcane · Shadow

[yellow]Status Effects:[/yellow]
  Burn      — 1/16 HP each turn
  Poison    — 1/8 HP each turn
  Bad Poison — escalating damage
  Freeze    — can't move (20% thaw/turn)
  Stun      — 25% can't move this turn
  Sleep     — can't move until wake (2–5 turns)
  Confusion — 33% chance hurt self each turn

[yellow]Tips:[/yellow]
  • Spells cost MP — manage your mana carefully.
  • Weaken wild creatures before throwing AetherBalls.
  • Heal at any Town — it's free!
  • Save often via the world menu.
        """)
        self.renderer.pause()
        self.run()

    # ── Starter selection ───────────────────────────────────────────────────

    def _choose_starter(self) -> None:
        self.renderer.clear()
        self.renderer.print(
            "[bold]Prof. Aethon:[/bold] Three AetherMon await you. "
            "Choose your partner!\n"
        )

        starters = [CREATURES[n] for n in STARTER_NAMES]
        options: list[str] = []
        for s in starters:
            color = {"Fire": "red", "Water": "blue", "Grass": "green"}.get(s.types[0], "white")
            options.append(
                f"[bold {color}]{s.name}[/bold {color}]  "
                f"[{'/'.join(s.types)}] {s.creature_class}  — {s.description}"
            )

        idx = self.renderer.menu("Your starter:", options)
        chosen_template = starters[idx]
        starter = Creature(chosen_template, level=5)
        self.player.add_to_party(starter)  # type: ignore
        self.renderer.print(f"\n[bold green]{starter.name} added to your party![/bold green]")
        if self.renderer.mode.value != "text":
            for line in __import__("src.ui.art", fromlist=["get_sprite"]).get_sprite(starter.name):
                self.renderer.print(f"  [bright_white]{line}[/bright_white]")
        self.renderer.pause()

    # ── Rival intro battle ──────────────────────────────────────────────────

    def _rival_intro_battle(self) -> None:
        if not self.player:
            return
        player_starter_name = self.player.party[0].name
        rival_template_key = RIVAL_STARTER_MAP.get(player_starter_name)
        if not rival_template_key:
            return

        self.renderer.clear()
        rival = self.player.rival_name
        self.renderer.print(
            f"\n[bold red]{rival}:[/bold red] Hey {self.player.name}! "
            f"I already have my partner. Let's see who's better right now!\n"
        )
        self.renderer.pause()

        rival_creature = Creature(CREATURES[rival_template_key], level=5)
        outcome = run_battle_ui(
            self.player, rival_creature, self.renderer,
            is_wild=False, trainer_name=rival,
        )

        if outcome == BattleOutcome.PLAYER_WIN:
            self.renderer.print(f"\n[bold red]{rival}:[/bold red] WHAT?! Unbelievable!")
        else:
            self.renderer.print(f"\n[bold red]{rival}:[/bold red] Yeah! I'm great, aren't I?")

        self.renderer.print(
            f"\n[bold red]{rival}:[/bold red] "
            "Don't think this is over. See you out there, trainer!\n"
        )
        self.renderer.pause()

        # Auto-heal after intro
        for c in self.player.party:
            c.full_restore()
        self.renderer.print("[bold green]Your creatures were healed before departure.[/bold green]")
        self.renderer.pause()

    # ── Overworld ───────────────────────────────────────────────────────────

    def _overworld(self) -> None:
        assert self.player is not None
        while True:
            self.renderer.clear()
            self.renderer.print(
                f"\n[bold]Trainer:[/bold] [cyan]{self.player.name}[/cyan]  "
                f"Location: [yellow]{self.player.location}[/yellow]  "
                f"Badges: [magenta]{self.player.badges}[/magenta]  "
                f"Money: [green]${self.player.money}[/green]\n"
            )

            options = [
                f"Explore  [{self.player.location}]",
                "Town Centre  (heal, shop)",
                "Party & Stats",
                "Travel to new route",
                "Save game",
                "Quit",
            ]
            choice = self.renderer.menu("What will you do?", options)

            if choice == 0:
                self._explore()
            elif choice == 1:
                self._town()
            elif choice == 2:
                self._party_menu()
            elif choice == 3:
                self._travel()
            elif choice == 4:
                self._save()
            else:
                self._quit_confirm()

    def _explore(self) -> None:
        assert self.player
        location = self.player.location
        table = WILD_ENCOUNTERS.get(location)
        if not table:
            self.renderer.print(f"[dim]There are no wild creatures on {location} yet.[/dim]")
            self.renderer.pause()
            return

        steps = random.randint(1, 5)
        self.renderer.print(f"[dim]You venture into {location}...[/dim]")
        time.sleep(0.6)

        for _ in range(steps):
            time.sleep(0.3)

        # Wild encounter!
        name, min_lv, max_lv, _ = random.choices(
            table,
            weights=[w for *_, w in table],
        )[0]
        lvl = random.randint(min_lv, max_lv)
        wild = Creature(CREATURES[name], level=lvl)
        time.sleep(0.5)

        outcome = run_battle_ui(self.player, wild, self.renderer, is_wild=True)

        if outcome == BattleOutcome.PLAYER_LOSE:
            self.renderer.print(
                "\n[bold red]You blacked out! Your creatures were healed at the Aether Centre.[/bold red]"
            )
            for c in self.player.party:
                c.full_restore()
            self.renderer.pause()
        elif outcome == BattleOutcome.CAPTURED:
            self.renderer.print(f"[bold green]{wild.name} joined your party![/bold green]")
            self.renderer.pause()

    def _town(self) -> None:
        assert self.player
        self.renderer.clear()
        self.renderer.print("[bold green]── Aether Town Centre ──────────────────[/bold green]")

        choice = self.renderer.menu(
            "Town options:",
            ["Heal all creatures (free)", "Shop", "Leave town"],
        )

        if choice == 0:
            for c in self.player.party:
                c.full_restore()
            self.renderer.print("[bold green]All your creatures have been fully healed![/bold green]")
            self.renderer.pause()
        elif choice == 1:
            self._shop()

    def _shop(self) -> None:
        assert self.player
        while True:
            self.renderer.clear()
            self.renderer.print(f"[bold]Shop  ── Your money: [green]${self.player.money}[/green][/bold]\n")
            options = [
                f"{item}  [green]${price}[/green]  (have: {self.player.bag.get(item, 0)})"
                for item, price in SHOP_ITEMS.items()
            ]
            options.append("Leave")
            idx = self.renderer.menu("Buy:", options)
            if idx == len(options) - 1:
                break
            item = list(SHOP_ITEMS.keys())[idx]
            price = SHOP_ITEMS[item]
            if self.player.money < price:
                self.renderer.print("[red]Not enough money.[/red]")
            else:
                self.player.money -= price
                self.player.bag[item] = self.player.bag.get(item, 0) + 1
                self.renderer.print(f"[bold green]Bought {item}![/bold green]")
            self.renderer.pause()

    def _party_menu(self) -> None:
        assert self.player
        self.renderer.clear()
        self.renderer.show_party(self.player.party)
        options = [
            f"View details: {c.name}" for c in self.player.party
        ] + ["Back"]
        idx = self.renderer.menu("Party:", options)
        if idx < len(self.player.party):
            self.renderer.clear()
            self.renderer.show_creature_detail(self.player.party[idx])
        self.renderer.pause()

    def _travel(self) -> None:
        assert self.player
        locations = list(WILD_ENCOUNTERS.keys())
        options = locations + ["← Cancel"]
        idx = self.renderer.menu("Travel to:", options)
        if idx < len(locations):
            self.player.location = locations[idx]
            self.renderer.print(f"[bold cyan]Arrived at {self.player.location}![/bold cyan]")
            self.renderer.pause()

    def _save(self) -> None:
        assert self.player
        self.player.save(SAVE_PATH)
        self.renderer.print(f"[bold green]Game saved![/bold green]")
        self.renderer.pause()

    def _quit_confirm(self) -> None:
        choice = self.renderer.menu("Really quit?", ["Yes, quit", "No, continue"])
        if choice == 0:
            self.renderer.print("[dim]Thanks for playing AetherMon![/dim]")
            sys.exit(0)
