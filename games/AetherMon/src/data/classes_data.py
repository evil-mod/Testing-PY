"""AetherMon creature class definitions.

A creature's CLASS is separate from its elemental TYPE.
Classes give passive bonuses and unlock class-specific moves.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreatureClass:
    name: str
    description: str
    # Stat multipliers applied at creature creation and on level-up
    atk_mult: float = 1.0
    def_mult: float = 1.0
    spa_mult: float = 1.0   # special attack
    spd_mult: float = 1.0   # special defense
    spe_mult: float = 1.0   # speed
    hp_mult: float = 1.0
    mp_mult: float = 1.0    # mana pool multiplier
    # Passive ability description
    passive: str = ""
    color: str = "white"


CLASSES: dict[str, CreatureClass] = {
    "Warrior": CreatureClass(
        name="Warrior",
        description="Masters of physical combat. High ATK and DEF.",
        atk_mult=1.3,
        def_mult=1.2,
        hp_mult=1.1,
        mp_mult=0.6,
        passive="Iron Will: 10% chance to survive a lethal hit with 1 HP.",
        color="bold red",
    ),
    "Mage": CreatureClass(
        name="Mage",
        description="Arcane scholars. High SPA, large mana pool.",
        spa_mult=1.4,
        spd_mult=1.1,
        mp_mult=1.8,
        hp_mult=0.85,
        passive="Arcane Surge: Spells have 15% chance to deal double damage.",
        color="bold blue",
    ),
    "Rogue": CreatureClass(
        name="Rogue",
        description="Swift and cunning. High speed, crits more often.",
        spe_mult=1.4,
        atk_mult=1.1,
        hp_mult=0.9,
        passive="Shadowstep: +15% critical hit chance on all moves.",
        color="bold magenta",
    ),
    "Priest": CreatureClass(
        name="Priest",
        description="Healers and support. High HP, healing spells.",
        hp_mult=1.3,
        spd_mult=1.2,
        mp_mult=1.5,
        atk_mult=0.8,
        passive="Blessing: Heal 5% max HP at end of each turn.",
        color="bold yellow",
    ),
    "Ranger": CreatureClass(
        name="Ranger",
        description="Versatile hunters. Balanced stats, status moves.",
        atk_mult=1.1,
        spe_mult=1.1,
        mp_mult=1.0,
        passive="Tracker: Status moves have +20% accuracy.",
        color="bold green",
    ),
    "Berserker": CreatureClass(
        name="Berserker",
        description="Reckless powerhouse. ATK rises as HP falls.",
        atk_mult=1.5,
        def_mult=0.85,
        hp_mult=1.0,
        mp_mult=0.5,
        passive="Rage: Each 10% HP lost grants +5% ATK (stacks).",
        color="bold dark_orange",
    ),
    "Shaman": CreatureClass(
        name="Shaman",
        description="Nature-bound caster. Mix of elemental and healing.",
        spa_mult=1.2,
        hp_mult=1.1,
        mp_mult=1.4,
        passive="Nature's Wrath: Type-bonus moves deal +10% extra damage.",
        color="bold green",
    ),
}
