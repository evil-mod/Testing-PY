"""AetherMon Creature runtime class.

Instantiated from a CreatureTemplate; holds live combat state.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


@dataclass
class StatStages:
    """In-battle stat stage modifiers (-6 to +6)."""
    atk: int = 0
    def_: int = 0
    spa: int = 0
    spd: int = 0
    spe: int = 0
    accuracy: int = 0
    evasion: int = 0

    def reset(self) -> None:
        self.atk = self.def_ = self.spa = self.spd = self.spe = 0
        self.accuracy = self.evasion = 0


# Stage multiplier table (index 0 = stage 0; negative index wrap-around)
_STAGE_MULT = {
    -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
     0: 1.0,
     1: 3/2,  2: 4/2,  3: 5/2,  4: 6/2,  5: 7/2,  6: 8/2,
}

STATUS_NAMES = {
    "burn":       "🔥 Burned",
    "freeze":     "❄  Frozen",
    "poison":     "☠  Poisoned",
    "bad_poison": "💀 Bad Poison",
    "stun":       "⚡ Stunned",
    "sleep":      "💤 Asleep",
    "confusion":  "💫 Confused",
    "flinch":     "😨 Flinched",
    "charm":      "💗 Charmed",
    "protect":    "🛡  Protected",
}


class Creature:
    """A live AetherMon creature with full combat state."""

    def __init__(
        self,
        template,                    # CreatureTemplate
        level: int = 5,
        nickname: str | None = None,
    ) -> None:
        from src.data import CLASSES, MOVES

        self.template = template
        self.name: str = nickname or template.name
        self.level: int = level
        self.types: list[str] = list(template.types)
        self.creature_class_name: str = template.creature_class
        self.creature_class = CLASSES[template.creature_class]

        # Compute stats from base stats + level + class multipliers
        self._compute_stats()

        # Live HP / MP
        self.current_hp: int = self.max_hp
        self.current_mp: int = self.max_mp

        # Move PP tracking: {move_name: remaining_pp}
        all_moves = list(template.moves) + list(template.spells)
        self.move_pool: list[str] = all_moves
        self.move_pp: dict[str, int] = {
            m: MOVES[m].pp for m in all_moves if m in MOVES
        }

        # Status
        self.status: str | None = None          # primary status
        self.status_turns: int = 0              # turns remaining (0 = indefinite)
        self.bad_poison_counter: int = 0        # escalating poison damage counter
        self.confused_turns: int = 0
        self.protected_this_turn: bool = False

        # In-battle stat stages
        self.stages = StatStages()

        # EXP
        self.exp: int = 0
        self.exp_to_next: int = self._exp_threshold(level + 1)

    # ── Stat computation ────────────────────────────────────────────────────

    def _exp_threshold(self, lvl: int) -> int:
        return int((lvl ** 3) * 0.8)

    def _compute_stats(self) -> None:
        t = self.template
        c = self.creature_class
        lvl = self.level

        def scale(base: int, mult: float) -> int:
            return max(1, int((base * (lvl / 5) + lvl * 2) * mult))

        self.max_hp  = max(10, int((t.base_hp * (lvl / 5) + lvl * 3) * c.hp_mult))
        self.base_atk = scale(t.base_atk, c.atk_mult)
        self.base_def = scale(t.base_def, c.def_mult)
        self.base_spa = scale(t.base_spa, c.spa_mult)
        self.base_spd = scale(t.base_spd, c.spd_mult)
        self.base_spe = scale(t.base_spe, c.spe_mult)
        self.max_mp   = max(10, int((t.base_mp * (lvl / 5) + lvl * 2) * c.mp_mult))

    # ── Live stat getters (apply stage multiplier) ──────────────────────────

    def _apply_stage(self, base_val: int, stage: int) -> int:
        return max(1, int(base_val * _STAGE_MULT.get(max(-6, min(6, stage)), 1.0)))

    @property
    def atk(self) -> int:
        val = self.base_atk
        # Berserker passive: +5% per 10% HP lost
        if self.creature_class_name == "Berserker":
            lost_pct = max(0, 1.0 - self.current_hp / self.max_hp)
            val = int(val * (1 + lost_pct * 0.5))
        return self._apply_stage(val, self.stages.atk)

    @property
    def def_(self) -> int:
        return self._apply_stage(self.base_def, self.stages.def_)

    @property
    def spa(self) -> int:
        return self._apply_stage(self.base_spa, self.stages.spa)

    @property
    def spd(self) -> int:
        return self._apply_stage(self.base_spd, self.stages.spd)

    @property
    def spe(self) -> int:
        base = self.base_spe
        if self.status in ("stun", "freeze"):
            base = base // 2
        return self._apply_stage(base, self.stages.spe)

    # ── Combat helpers ──────────────────────────────────────────────────────

    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def hp_percent(self) -> float:
        return self.current_hp / self.max_hp

    def mp_percent(self) -> float:
        return self.current_mp / self.max_mp

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def can_use_move(self, move_name: str) -> bool:
        from src.data import MOVES
        if move_name not in MOVES:
            return False
        mv = MOVES[move_name]
        if self.move_pp.get(move_name, 0) <= 0:
            return False
        if mv.category == "special" and self.current_mp < mv.mp_cost:
            return False
        return True

    def use_move_pp(self, move_name: str) -> None:
        if move_name in self.move_pp and self.move_pp[move_name] > 0:
            self.move_pp[move_name] -= 1

    def available_moves(self) -> list[str]:
        moves = [m for m in self.move_pool if self.can_use_move(m)]
        return moves if moves else ["Struggle"]

    def apply_status(self, status: str, turns: int = 0) -> bool:
        """Apply a status condition. Returns True if applied."""
        # Can't apply if already has a primary status (except confusion)
        if status in ("burn", "freeze", "poison", "bad_poison", "stun", "sleep"):
            if self.status is not None:
                return False
        if status == "confusion":
            if self.confused_turns > 0:
                return False
            self.confused_turns = random.randint(2, 5)
            return True
        self.status = status
        self.status_turns = turns
        self.bad_poison_counter = 0
        return True

    def tick_status(self) -> list[str]:
        """Process end-of-turn status effects. Returns list of messages."""
        messages: list[str] = []

        if self.status == "burn":
            dmg = max(1, self.max_hp // 16)
            self.current_hp = max(0, self.current_hp - dmg)
            messages.append(f"{self.name} is hurt by burn! (-{dmg} HP)")

        elif self.status == "poison":
            dmg = max(1, self.max_hp // 8)
            self.current_hp = max(0, self.current_hp - dmg)
            messages.append(f"{self.name} is hurt by poison! (-{dmg} HP)")

        elif self.status == "bad_poison":
            self.bad_poison_counter += 1
            dmg = max(1, (self.max_hp * self.bad_poison_counter) // 16)
            self.current_hp = max(0, self.current_hp - dmg)
            messages.append(f"{self.name} is badly poisoned! (-{dmg} HP)")

        # Priest passive: heal 5% max HP each turn
        if self.creature_class_name == "Priest" and self.is_alive():
            heal = max(1, self.max_hp // 20)
            self.current_hp = min(self.max_hp, self.current_hp + heal)
            messages.append(f"{self.name}'s Blessing restored {heal} HP.")

        return messages

    def tick_sleep(self) -> tuple[bool, str]:
        """Returns (still_asleep, message)."""
        if self.status == "sleep":
            self.status_turns = max(0, self.status_turns - 1)
            if self.status_turns == 0:
                self.status = None
                return False, f"{self.name} woke up!"
            return True, f"{self.name} is fast asleep."
        return False, ""

    def tick_freeze(self) -> tuple[bool, str]:
        """20% chance to thaw each turn."""
        if self.status == "freeze":
            if random.random() < 0.2:
                self.status = None
                return False, f"{self.name} thawed out!"
            return True, f"{self.name} is frozen solid!"
        return False, ""

    # ── Leveling ────────────────────────────────────────────────────────────

    def gain_exp(self, amount: int) -> list[str]:
        """Add EXP, level up if threshold reached. Returns event messages."""
        messages: list[str] = []
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            old_hp = self.max_hp
            old_mp = self.max_mp
            self._compute_stats()
            gained_hp = self.max_hp - old_hp
            gained_mp = self.max_mp - old_mp
            self.current_hp = min(self.max_hp, self.current_hp + gained_hp)
            self.current_mp = min(self.max_mp, self.current_mp + gained_mp)
            self.exp_to_next = self._exp_threshold(self.level + 1)
            messages.append(
                f"★ {self.name} grew to level {self.level}! "
                f"(+{gained_hp} HP, +{gained_mp} MP)"
            )
        return messages

    # ── Iron Will passive ───────────────────────────────────────────────────

    def check_iron_will(self, incoming_dmg: int) -> int:
        """Warrior passive: 10% chance to survive lethal hit."""
        if (
            self.creature_class_name == "Warrior"
            and self.current_hp > 1
            and incoming_dmg >= self.current_hp
            and random.random() < 0.10
        ):
            return self.current_hp - 1  # survive at 1 HP
        return incoming_dmg

    # ── Restore (between battles / item use) ───────────────────────────────

    def full_restore(self) -> None:
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        self.status = None
        self.status_turns = 0
        self.bad_poison_counter = 0
        self.confused_turns = 0
        self.stages.reset()
        from src.data import MOVES
        self.move_pp = {m: MOVES[m].pp for m in self.move_pool if m in MOVES}

    def partial_heal(self, amount: int) -> int:
        """Heal HP. Returns actual amount healed."""
        before = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - before

    def __repr__(self) -> str:
        return (
            f"<Creature {self.name} Lv{self.level} "
            f"HP:{self.current_hp}/{self.max_hp} "
            f"MP:{self.current_mp}/{self.max_mp}>"
        )
