"""AetherMon battle engine — handles all combat resolution."""
from __future__ import annotations

import math
import random
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities import Creature, Player


class BattleOutcome(Enum):
    ONGOING    = auto()
    PLAYER_WIN = auto()
    PLAYER_LOSE = auto()
    FLED       = auto()
    CAPTURED   = auto()


class TurnResult:
    """Result of a single action in a battle turn."""
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.outcome: BattleOutcome = BattleOutcome.ONGOING
        self.exp_gained: int = 0
        self.level_up_msgs: list[str] = []
        self.captured: bool = False

    def add(self, msg: str) -> None:
        self.messages.append(msg)


class BattleEngine:
    """Manages a single battle between player's active creature and an opponent."""

    def __init__(
        self,
        player: "Player",
        opponent: "Creature",
        is_wild: bool = True,
        trainer_name: str | None = None,
    ) -> None:
        self.player = player
        self.opponent = opponent
        self.is_wild = is_wild
        self.trainer_name = trainer_name
        self.turn: int = 0
        self.outcome: BattleOutcome = BattleOutcome.ONGOING
        self.fled_allowed = is_wild

    @property
    def attacker(self) -> "Creature":
        return self.player.active()  # type: ignore

    def is_over(self) -> bool:
        return self.outcome != BattleOutcome.ONGOING

    # ── Main turn resolution ────────────────────────────────────────────────

    def player_attack(self, move_name: str) -> TurnResult:
        res = TurnResult()
        self.turn += 1
        player_c = self.player.active()
        if player_c is None:
            res.outcome = BattleOutcome.PLAYER_LOSE
            res.add("You have no conscious creatures!")
            return res

        # Reset per-turn protect flags
        player_c.protected_this_turn = False
        self.opponent.protected_this_turn = False

        # Determine turn order based on speed (with priority)
        from src.data import MOVES
        player_move = MOVES.get(move_name) if move_name in MOVES else None
        player_priority = player_move.priority if player_move else 0

        # Simple AI: pick best available move
        enemy_move_name = self._enemy_choose_move()
        enemy_move = MOVES.get(enemy_move_name) if enemy_move_name in MOVES else None
        enemy_priority = enemy_move.priority if enemy_move else 0

        player_goes_first = (
            player_priority > enemy_priority
            or (player_priority == enemy_priority and player_c.spe >= self.opponent.spe)
        )

        if player_goes_first:
            self._execute_move(player_c, self.opponent, move_name, res)
            if not self.opponent.is_fainted():
                self._execute_move(self.opponent, player_c, enemy_move_name, res)
        else:
            self._execute_move(self.opponent, player_c, enemy_move_name, res)
            if not player_c.is_fainted():
                self._execute_move(player_c, self.opponent, move_name, res)

        # End-of-turn effects
        self._end_of_turn(player_c, res)

        # Check battle end
        self._check_end(player_c, res)
        return res

    def player_use_item(self, item: str, target: "Creature") -> TurnResult:
        res = TurnResult()
        success, msg = self.player.use_item(item, target)
        res.add(msg)
        if not success:
            return res
        # Enemy still gets to move
        enemy_move_name = self._enemy_choose_move()
        player_c = self.player.active()
        if player_c:
            self._execute_move(self.opponent, player_c, enemy_move_name, res)
        self._end_of_turn(player_c, res)
        self._check_end(player_c, res)
        return res

    def player_flee(self) -> TurnResult:
        res = TurnResult()
        if not self.fled_allowed:
            res.add("You can't flee from a trainer battle!")
            return res
        # Flee chance based on speed
        player_c = self.player.active()
        if player_c is None:
            res.outcome = BattleOutcome.FLED
            return res
        odds = (player_c.spe * 128 / max(1, self.opponent.spe) + 30) / 256
        if random.random() < odds:
            res.add("Got away safely!")
            self.outcome = BattleOutcome.FLED
            res.outcome = BattleOutcome.FLED
        else:
            res.add("Can't escape!")
            # Enemy attacks
            enemy_move_name = self._enemy_choose_move()
            self._execute_move(self.opponent, player_c, enemy_move_name, res)
            self._check_end(player_c, res)
        return res

    def player_throw_ball(self) -> TurnResult:
        res = TurnResult()
        if not self.is_wild:
            res.add("You can't capture a trainer's creature!")
            return res
        if self.player.bag.get("AetherBall", 0) <= 0:
            res.add("You have no AetherBalls!")
            return res
        self.player.bag["AetherBall"] -= 1
        res.add("You threw an AetherBall!")

        capture_rate = self._calc_capture_rate()
        if random.random() < capture_rate:
            res.add(f"★★  Gotcha! {self.opponent.name} was captured! ★★")
            self.opponent.full_restore()
            self.player.add_to_party(self.opponent)
            self.outcome = BattleOutcome.CAPTURED
            res.outcome = BattleOutcome.CAPTURED
            res.captured = True
        else:
            res.add(f"{self.opponent.name} broke free!")
            enemy_move_name = self._enemy_choose_move()
            player_c = self.player.active()
            if player_c:
                self._execute_move(self.opponent, player_c, enemy_move_name, res)
            self._check_end(player_c, res)
        return res

    # ── Move execution ──────────────────────────────────────────────────────

    def _execute_move(
        self,
        attacker: "Creature",
        defender: "Creature",
        move_name: str,
        res: TurnResult,
    ) -> None:
        from src.data import MOVES, get_effectiveness

        if attacker.is_fainted():
            return

        # Sleep check
        still_sleeping, sleep_msg = attacker.tick_sleep()
        if still_sleeping:
            res.add(sleep_msg)
            return
        elif sleep_msg:
            res.add(sleep_msg)

        # Freeze check
        still_frozen, freeze_msg = attacker.tick_freeze()
        if still_frozen:
            res.add(freeze_msg)
            return
        elif freeze_msg:
            res.add(freeze_msg)

        # Stun: 25% chance to fail
        if attacker.status == "stun" and random.random() < 0.25:
            res.add(f"{attacker.name} is stunned and couldn't move!")
            attacker.status = None  # stun clears after one turn
            return

        # Confusion: 33% chance to hurt self
        if attacker.confused_turns > 0:
            attacker.confused_turns -= 1
            if attacker.confused_turns == 0:
                res.add(f"{attacker.name} is no longer confused.")
            elif random.random() < 0.33:
                self_dmg = max(1, attacker.max_hp // 8)
                attacker.current_hp = max(0, attacker.current_hp - self_dmg)
                res.add(f"{attacker.name} hurt itself in confusion! (-{self_dmg} HP)")
                if attacker.is_fainted():
                    return

        # Flinch
        if attacker.status == "flinch":
            attacker.status = None
            res.add(f"{attacker.name} flinched!")
            return

        # Protect check
        if defender.protected_this_turn:
            res.add(f"{attacker.name} used {move_name} — but {defender.name} is protected!")
            return

        if move_name not in MOVES:
            move_name = "Struggle"
        mv = MOVES[move_name]

        # Consume PP and MP
        attacker.use_move_pp(move_name)
        if mv.category == "special":
            attacker.current_mp = max(0, attacker.current_mp - mv.mp_cost)

        # Accuracy check
        accuracy_mult = 1.0
        if mv.accuracy < 1.0:
            stage_acc = attacker.stages.accuracy - defender.stages.evasion
            accuracy_mult = max(0.33, min(3.0, {
                -6: 0.33, -5: 0.36, -4: 0.43, -3: 0.50, -2: 0.60, -1: 0.75,
                 0: 1.0,
                 1: 1.33,  2: 1.66,  3: 2.0,  4: 2.33,  5: 2.66,  6: 3.0,
            }.get(max(-6, min(6, stage_acc)), 1.0)))
            if random.random() > mv.accuracy * accuracy_mult:
                res.add(f"{attacker.name} used {move_name} — but it missed!")
                return

        res.add(f"{'You' if attacker == self.player.active() else attacker.name} used {move_name}!")

        # Status move
        if mv.category == "status":
            self._apply_effect(mv.effect, attacker, defender, res)
            return

        # Calculate damage
        damage = self._calc_damage(attacker, defender, move_name, res)

        # Protect move
        if mv.effect == "protect":
            attacker.protected_this_turn = True
            res.add(f"{attacker.name} braced itself!")
            return

        # Apply Mage Arcane Surge
        if attacker.creature_class_name == "Mage" and mv.category == "special":
            if random.random() < 0.15:
                damage *= 2
                res.add("★ Arcane Surge! Double damage!")

        # Iron Will
        damage = attacker.check_iron_will(damage) if attacker == defender else damage  # only for self
        # Actually Iron Will is on _defender_ when checking lethal damage
        if defender.creature_class_name == "Warrior":
            damage = defender.check_iron_will(damage)

        defender.current_hp = max(0, defender.current_hp - damage)
        dmg_pct = int((damage / defender.max_hp) * 100)
        res.add(f"{defender.name} took {damage} damage ({dmg_pct}% of max HP).")

        if defender.is_fainted():
            res.add(f"{defender.name} fainted!")
            return

        # Struggle recoil
        if move_name == "Struggle":
            recoil = max(1, attacker.max_hp // 4)
            attacker.current_hp = max(0, attacker.current_hp - recoil)
            res.add(f"{attacker.name} took {recoil} recoil damage!")

        # On-hit effects
        if mv.effect and random.random() < mv.effect_chance:
            self._apply_effect(mv.effect, attacker, defender, res)

    # ── Damage formula ──────────────────────────────────────────────────────

    def _calc_damage(
        self, attacker: "Creature", defender: "Creature", move_name: str, res: TurnResult
    ) -> int:
        from src.data import MOVES, get_effectiveness
        mv = MOVES[move_name]

        # STAB (Same Type Attack Bonus)
        stab = 1.5 if mv.move_type in attacker.types else 1.0

        # Type effectiveness
        eff = get_effectiveness(mv.move_type, defender.types)
        if eff > 1:
            res.add("It's super effective!")
        elif eff == 0:
            res.add(f"It had no effect on {defender.name}!")
            return 0
        elif eff < 1:
            res.add("It's not very effective...")

        # Ranger status accuracy bonus on range stats — skip for damage
        # Shaman class: +10% if super effective
        if attacker.creature_class_name == "Shaman" and eff > 1:
            eff *= 1.10

        # Critical hit (base 6.25%, Rogue +15%)
        crit_chance = 0.0625
        if attacker.creature_class_name == "Rogue":
            crit_chance += 0.15
        crit = 1.5 if random.random() < crit_chance else 1.0
        if crit > 1:
            res.add("A critical hit!")

        # Atk/Def or SPA/SPD
        if mv.category == "physical":
            atk_val = attacker.atk
            def_val = defender.def_
        else:
            atk_val = attacker.spa
            def_val = defender.spd

        # Gen-style formula
        raw = ((attacker.level * 0.4 + 2) * mv.power * atk_val / def_val) / 50 + 2
        dmg = int(raw * stab * eff * crit * random.uniform(0.85, 1.0))
        return max(1, dmg)

    # ── Status effect application ───────────────────────────────────────────

    def _apply_effect(
        self,
        effect: str,
        attacker: "Creature",
        defender: "Creature",
        res: TurnResult,
    ) -> None:
        # Ranger Tracker: status moves +20% accuracy already handled via accuracy check
        target_is_self = effect in (
            "heal_self", "def_up", "spa_up", "spe_up", "cure_self", "protect"
        )
        target = attacker if target_is_self else defender

        if effect == "burn":
            if target.apply_status("burn"):
                res.add(f"{target.name} was burned! 🔥")
        elif effect == "freeze":
            if target.apply_status("freeze", turns=0):
                res.add(f"{target.name} was frozen! ❄")
        elif effect == "poison":
            if target.apply_status("poison"):
                res.add(f"{target.name} was poisoned! ☠")
        elif effect == "bad_poison":
            if target.apply_status("bad_poison"):
                res.add(f"{target.name} was badly poisoned! 💀")
        elif effect == "stun":
            if target.apply_status("stun"):
                res.add(f"{target.name} was stunned! ⚡")
        elif effect == "sleep":
            turns = random.randint(2, 5)
            if target.apply_status("sleep", turns=turns):
                res.add(f"{target.name} fell asleep! 💤")
        elif effect == "confusion":
            if target.apply_status("confusion"):
                res.add(f"{target.name} became confused! 💫")
        elif effect == "flinch":
            target.status = "flinch"
            res.add(f"{target.name} flinched! 😨")
        elif effect == "charm":
            target.stages.atk = max(-6, target.stages.atk - 2)
            res.add(f"{target.name}'s ATK fell sharply! 💗")
        elif effect == "atk_down":
            target.stages.atk = max(-6, target.stages.atk - 1)
            res.add(f"{target.name}'s ATK fell!")
        elif effect == "def_down":
            target.stages.def_ = max(-6, target.stages.def_ - 1)
            res.add(f"{target.name}'s DEF fell!")
        elif effect == "spe_down":
            target.stages.spe = max(-6, target.stages.spe - 1)
            res.add(f"{target.name}'s SPE fell!")
        elif effect == "spd_down":
            target.stages.spd = max(-6, target.stages.spd - 1)
            res.add(f"{target.name}'s SPD fell!")
        elif effect == "accuracy_down":
            target.stages.accuracy = max(-6, target.stages.accuracy - 1)
            res.add(f"{target.name}'s accuracy fell!")
        elif effect == "def_up":
            target.stages.def_ = min(6, target.stages.def_ + 2)
            res.add(f"{target.name}'s DEF rose sharply!")
        elif effect == "spe_up":
            target.stages.spe = min(6, target.stages.spe + 2)
            res.add(f"{target.name}'s SPE rose sharply!")
        elif effect == "heal_self":
            healed = target.partial_heal(target.max_hp // 2)
            res.add(f"{target.name} restored {healed} HP! 💚")
        elif effect == "cure_self":
            if target.status:
                res.add(f"{target.name} was cured of {target.status}! ✨")
                target.status = None
                target.bad_poison_counter = 0
            else:
                res.add(f"{target.name} has no status condition.")
        elif effect == "protect":
            attacker.protected_this_turn = True
            res.add(f"{attacker.name} is protecting itself!")

    # ── End-of-turn processing ──────────────────────────────────────────────

    def _end_of_turn(self, player_c: "Creature | None", res: TurnResult) -> None:
        for msg in self.opponent.tick_status():
            res.add(msg)
        if player_c:
            for msg in player_c.tick_status():
                res.add(msg)

    # ── Battle end check ────────────────────────────────────────────────────

    def _check_end(self, player_c: "Creature | None", res: TurnResult) -> None:
        if self.opponent.is_fainted():
            exp = self._calc_exp()
            res.exp_gained = exp
            if player_c:
                res.level_up_msgs = player_c.gain_exp(exp)
            res.add(f"You earned {exp} EXP!")
            self.outcome = BattleOutcome.PLAYER_WIN
            res.outcome = BattleOutcome.PLAYER_WIN
        elif player_c is None or player_c.is_fainted():
            if not self.player.has_conscious_creature():
                res.add("All your creatures have fainted...")
                self.outcome = BattleOutcome.PLAYER_LOSE
                res.outcome = BattleOutcome.PLAYER_LOSE

    # ── AI move selection ───────────────────────────────────────────────────

    def _enemy_choose_move(self) -> str:
        """Simple AI: prefer super-effective moves, avoid ineffective ones."""
        from src.data import MOVES, get_effectiveness
        player_c = self.player.active()
        available = self.opponent.available_moves()
        if not available:
            return "Struggle"

        best_move = None
        best_score = -1.0
        for move_name in available:
            if move_name not in MOVES:
                continue
            mv = MOVES[move_name]
            eff = 1.0
            if player_c and mv.category != "status":
                eff = get_effectiveness(mv.move_type, player_c.types)
            score = mv.power * eff
            if mv.move_type in self.opponent.types:
                score *= 1.5
            if score > best_score:
                best_score = score
                best_move = move_name

        # 30% chance to use a random move instead (unpredictable AI)
        if random.random() < 0.3:
            return random.choice(available)
        return best_move or random.choice(available)

    # ── Capture rate ────────────────────────────────────────────────────────

    def _calc_capture_rate(self) -> float:
        catch_rate = self.opponent.template.catch_rate / 255
        hp_factor = 1 - (self.opponent.current_hp / self.opponent.max_hp)
        status_bonus = 1.5 if self.opponent.status in ("sleep", "freeze") else 1.0
        return min(0.99, catch_rate * (0.3 + hp_factor * 0.7) * status_bonus)

    # ── EXP calculation ─────────────────────────────────────────────────────

    def _calc_exp(self) -> int:
        base = self.opponent.template.exp_yield
        lvl_ratio = self.opponent.level / max(1, self.player.active().level if self.player.active() else 1)
        return max(5, int(base * lvl_ratio))
