"""Player inventory and progress."""
from __future__ import annotations
import json
import os
from pathlib import Path

from src.entities.creature import Creature
from src.data import CREATURES


class Player:
    PARTY_MAX = 6
    BALL_CATCH_RATE = 0.35       # per-ball base multiplier

    def __init__(self, name: str) -> None:
        self.name = name
        self.party: list[Creature] = []
        self.bag: dict[str, int] = {
            "AetherBall":  10,
            "Potion":       5,
            "Elixir":       2,   # restores MP
            "Antidote":     2,
            "Revive":       1,
        }
        self.money: int = 200
        self.location: str = "Starter Town"
        self.badges: int = 0
        self.rival_name: str = ""
        self.defeated_trainers: set[str] = set()

    # ── Party helpers ───────────────────────────────────────────────────────

    def add_to_party(self, creature: Creature) -> bool:
        if len(self.party) >= self.PARTY_MAX:
            return False
        self.party.append(creature)
        return True

    def active(self) -> Creature | None:
        for c in self.party:
            if not c.is_fainted():
                return c
        return None

    def has_conscious_creature(self) -> bool:
        return any(not c.is_fainted() for c in self.party)

    def heal_all(self) -> None:
        for c in self.party:
            c.full_restore()

    # ── Item usage ──────────────────────────────────────────────────────────

    def use_item(self, item: str, target: Creature) -> tuple[bool, str]:
        """Use an item from bag on target. Returns (success, message)."""
        if self.bag.get(item, 0) <= 0:
            return False, f"You have no {item}s left!"

        if item == "Potion":
            if target.is_fainted():
                return False, f"{target.name} has fainted!"
            healed = target.partial_heal(30)
            if healed == 0:
                return False, f"{target.name}'s HP is already full!"
            self.bag[item] -= 1
            return True, f"Used Potion → {target.name} restored {healed} HP."

        if item == "Elixir":
            if target.is_fainted():
                return False, f"{target.name} has fainted!"
            before = target.current_mp
            target.current_mp = min(target.max_mp, target.current_mp + 25)
            gained = target.current_mp - before
            if gained == 0:
                return False, f"{target.name}'s MP is already full!"
            self.bag[item] -= 1
            return True, f"Used Elixir → {target.name} restored {gained} MP."

        if item == "Antidote":
            if target.status not in ("poison", "bad_poison"):
                return False, f"{target.name} isn't poisoned."
            target.status = None
            target.bad_poison_counter = 0
            self.bag[item] -= 1
            return True, f"Used Antidote → {target.name} is cured of poison."

        if item == "Revive":
            if not target.is_fainted():
                return False, f"{target.name} hasn't fainted."
            target.current_hp = target.max_hp // 2
            target.status = None
            self.bag[item] -= 1
            return True, f"Used Revive → {target.name} was revived with {target.current_hp} HP!"

        return False, f"Can't use {item} here."

    # ── Save / Load ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "money": self.money,
            "location": self.location,
            "badges": self.badges,
            "rival_name": self.rival_name,
            "defeated_trainers": list(self.defeated_trainers),
            "bag": self.bag,
            "party": [
                {
                    "template": c.template.name,
                    "level": c.level,
                    "nickname": c.name if c.name != c.template.name else None,
                    "current_hp": c.current_hp,
                    "current_mp": c.current_mp,
                    "exp": c.exp,
                    "status": c.status,
                    "move_pp": c.move_pp,
                }
                for c in self.party
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        player = cls(data["name"])
        player.money = data["money"]
        player.location = data["location"]
        player.badges = data["badges"]
        player.rival_name = data.get("rival_name", "")
        player.defeated_trainers = set(data.get("defeated_trainers", []))
        player.bag = data["bag"]
        for cd in data["party"]:
            template = CREATURES[cd["template"]]
            creature = Creature(template, level=cd["level"], nickname=cd.get("nickname"))
            creature.current_hp = cd["current_hp"]
            creature.current_mp = cd["current_mp"]
            creature.exp = cd["exp"]
            creature.status = cd.get("status")
            creature.move_pp = cd.get("move_pp", creature.move_pp)
            player.party.append(creature)
        return player

    def save(self, path: str = "saves/save.json") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str = "saves/save.json") -> "Player | None":
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
