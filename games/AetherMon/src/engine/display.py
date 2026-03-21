"""High-level UI wrapper around BattleEngine + Renderer.

run_battle_ui() drives the entire interactive battle loop.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.engine.battle import BattleEngine, BattleOutcome
from src.ui.renderer import Renderer, DisplayMode

if TYPE_CHECKING:
    from src.entities import Creature, Player


def run_battle_ui(
    player: "Player",
    opponent: "Creature",
    renderer: Renderer,
    is_wild: bool = True,
    trainer_name: str | None = None,
) -> BattleOutcome:
    """Interactive battle loop. Returns the final BattleOutcome."""
    engine = BattleEngine(player, opponent, is_wild=is_wild, trainer_name=trainer_name)

    if trainer_name:
        renderer.print(f"\n[bold red]★  Trainer {trainer_name} wants to battle! ★[/bold red]")
    else:
        renderer.print(f"\n[bold yellow]A wild {opponent.name} appeared![/bold yellow]")
    time.sleep(0.8)

    while not engine.is_over():
        player_c = player.active()
        if player_c is None:
            break

        renderer.battle_scene(player_c, opponent)

        # Main action menu
        action = renderer.move_menu(player_c)
        res = None

        if action == "1":          # FIGHT
            move_name = renderer.fight_menu(player_c)
            if move_name is None:
                continue
            if not player_c.can_use_move(move_name):
                renderer.print("[red]Not enough PP or MP for that move![/red]")
                time.sleep(1)
                continue
            res = engine.player_attack(move_name)

        elif action == "2":        # SPELL
            move_name = renderer.spell_menu(player_c)
            if move_name is None:
                continue
            if not player_c.can_use_move(move_name):
                renderer.print("[red]Not enough PP or MP for that spell![/red]")
                time.sleep(1)
                continue
            res = engine.player_attack(move_name)

        elif action == "3":        # ITEM
            choice = renderer.item_menu(player)
            if choice is None:
                continue
            item, target = choice
            res = engine.player_use_item(item, target)

        elif action == "4":        # BALL
            if not is_wild:
                renderer.print("[red]You can't capture a trainer's creature![/red]")
                time.sleep(1)
                continue
            res = engine.player_throw_ball()

        elif action == "5":        # RUN
            res = engine.player_flee()

        if res:
            renderer.clear()
            renderer.battle_scene(player_c, opponent)
            renderer.battle_result(res.messages, res.exp_gained, res.level_up_msgs)
            renderer.pause()

    return engine.outcome
