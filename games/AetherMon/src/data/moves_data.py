"""AetherMon moves & spells database.

category:
  "physical" — uses ATK / DEF
  "special"  — uses SPA / SPD (consumes MP)
  "status"   — applies an effect, no direct damage

effect: optional status effect applied on hit.
effect_chance: probability (0.0–1.0) the effect triggers.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MoveData:
    name: str
    move_type: str          # elemental type
    category: str           # physical / special / status
    power: int              # base damage (0 for status moves)
    accuracy: float         # hit chance 0.0–1.0
    pp: int                 # power points (uses)
    mp_cost: int = 0        # mana cost (special moves)
    effect: str = ""        # status effect name, e.g. "burn"
    effect_chance: float = 0.0
    description: str = ""
    priority: int = 0       # higher = goes first regardless of speed


MOVES: dict[str, MoveData] = {
    # ── Physical moves ──────────────────────────────────────────────────────
    "Tackle": MoveData(
        "Tackle", "Normal", "physical", 8, 1.0, 35,
        description="A straightforward tackle.",
    ),
    "Quick Strike": MoveData(
        "Quick Strike", "Normal", "physical", 6, 1.0, 40,
        priority=1, description="Always goes first.",
    ),
    "Slash": MoveData(
        "Slash", "Normal", "physical", 14, 0.95, 20,
        description="High crit ratio slash.",
    ),
    "Iron Tail": MoveData(
        "Iron Tail", "Steel", "physical", 16, 0.75, 15,
        effect="def_down", effect_chance=0.3,
        description="Heavy steel tail. May lower DEF.",
    ),
    "Rock Throw": MoveData(
        "Rock Throw", "Rock", "physical", 12, 0.9, 20,
        description="Hurls a sharp rock.",
    ),
    "Karate Chop": MoveData(
        "Karate Chop", "Fighting", "physical", 12, 0.95, 25,
        description="A focused chop. High crit ratio.",
    ),
    "Shadow Claw": MoveData(
        "Shadow Claw", "Ghost", "physical", 14, 1.0, 15,
        description="Rakes with a shadowy claw.",
    ),
    "Bite": MoveData(
        "Bite", "Dark", "physical", 12, 1.0, 25,
        effect="flinch", effect_chance=0.3,
        description="A sharp bite. May cause flinch.",
    ),
    "Wing Attack": MoveData(
        "Wing Attack", "Flying", "physical", 12, 1.0, 35,
        description="Strikes with powerful wings.",
    ),
    "Peck": MoveData(
        "Peck", "Flying", "physical", 10, 1.0, 35,
        description="A sharp beak strike.",
    ),
    "Vine Whip": MoveData(
        "Vine Whip", "Grass", "physical", 12, 1.0, 25,
        description="Lashes with sharp vines.",
    ),
    "Poison Sting": MoveData(
        "Poison Sting", "Poison", "physical", 10, 1.0, 35,
        effect="poison", effect_chance=0.3,
        description="A venomous sting. May poison.",
    ),
    "Scratch": MoveData(
        "Scratch", "Normal", "physical", 8, 1.0, 35,
        description="Rakes with sharp claws.",
    ),
    "Flame Punch": MoveData(
        "Flame Punch", "Fire", "physical", 14, 1.0, 15,
        effect="burn", effect_chance=0.1,
        description="A fiery punch. May burn.",
    ),
    "Thunder Punch": MoveData(
        "Thunder Punch", "Electric", "physical", 14, 1.0, 15,
        effect="stun", effect_chance=0.1,
        description="Electric punch. May stun.",
    ),
    "Ice Punch": MoveData(
        "Ice Punch", "Ice", "physical", 14, 1.0, 15,
        effect="freeze", effect_chance=0.1,
        description="Ice-cold punch. May freeze.",
    ),
    "Fury Swipes": MoveData(
        "Fury Swipes", "Normal", "physical", 6, 0.8, 15,
        description="2–5 rapid claw swipes.",
    ),
    "Crunch": MoveData(
        "Crunch", "Dark", "physical", 16, 1.0, 15,
        effect="def_down", effect_chance=0.2,
        description="A powerful bite. May lower DEF.",
    ),
    "Slash Combo": MoveData(
        "Slash Combo", "Normal", "physical", 18, 0.85, 10,
        description="A devastating two-hit slash.",
    ),

    # ── Special / Spell moves ────────────────────────────────────────────────
    "Ember": MoveData(
        "Ember", "Fire", "special", 12, 1.0, 25, mp_cost=8,
        effect="burn", effect_chance=0.1,
        description="A small flame. May burn.",
    ),
    "Fireball": MoveData(
        "Fireball", "Fire", "special", 22, 0.9, 10, mp_cost=20,
        effect="burn", effect_chance=0.25,
        description="Launches a blazing fireball. May burn.",
    ),
    "Inferno": MoveData(
        "Inferno", "Fire", "special", 30, 0.75, 5, mp_cost=35,
        effect="burn", effect_chance=0.5,
        description="A catastrophic blaze. Burns reliably.",
    ),
    "Bubble": MoveData(
        "Bubble", "Water", "special", 10, 1.0, 30, mp_cost=6,
        effect="spe_down", effect_chance=0.1,
        description="Bursting bubbles. May lower SPE.",
    ),
    "Water Pulse": MoveData(
        "Water Pulse", "Water", "special", 18, 1.0, 20, mp_cost=14,
        effect="confusion", effect_chance=0.2,
        description="A pulsing water wave. May confuse.",
    ),
    "Hydro Cannon": MoveData(
        "Hydro Cannon", "Water", "special", 35, 0.9, 5, mp_cost=40,
        description="Devastating water blast.",
    ),
    "Gust": MoveData(
        "Gust", "Flying", "special", 10, 1.0, 35, mp_cost=5,
        description="A sharp burst of wind.",
    ),
    "Razor Wind": MoveData(
        "Razor Wind", "Flying", "special", 20, 1.0, 10, mp_cost=20,
        description="A charging wind slash.",
    ),
    "Thunder Shock": MoveData(
        "Thunder Shock", "Electric", "special", 12, 1.0, 30, mp_cost=8,
        effect="stun", effect_chance=0.1,
        description="A jolt of electricity. May stun.",
    ),
    "Thunderbolt": MoveData(
        "Thunderbolt", "Electric", "special", 22, 1.0, 15, mp_cost=22,
        effect="stun", effect_chance=0.1,
        description="A strong bolt. May stun.",
    ),
    "Thunder": MoveData(
        "Thunder", "Electric", "special", 30, 0.7, 10, mp_cost=35,
        effect="stun", effect_chance=0.3,
        description="Wild lightning. Lower accuracy; high stun chance.",
    ),
    "Seed Bomb": MoveData(
        "Seed Bomb", "Grass", "special", 16, 1.0, 15, mp_cost=14,
        description="Exploding seed barrage.",
    ),
    "Solar Blast": MoveData(
        "Solar Blast", "Grass", "special", 28, 0.85, 10, mp_cost=28,
        description="Charged solar energy beam.",
    ),
    "Ice Shard": MoveData(
        "Ice Shard", "Ice", "special", 14, 1.0, 20, mp_cost=12,
        priority=1, effect="freeze", effect_chance=0.1,
        description="Icy shard, goes first. May freeze.",
    ),
    "Blizzard": MoveData(
        "Blizzard", "Ice", "special", 28, 0.7, 5, mp_cost=35,
        effect="freeze", effect_chance=0.1,
        description="Howling snowstorm.",
    ),
    "Psybeam": MoveData(
        "Psybeam", "Psychic", "special", 15, 1.0, 20, mp_cost=14,
        effect="confusion", effect_chance=0.1,
        description="Colorful psychic beam. May confuse.",
    ),
    "Psychic Burst": MoveData(
        "Psychic Burst", "Psychic", "special", 26, 0.9, 10, mp_cost=28,
        effect="spd_down", effect_chance=0.1,
        description="Psychic shockwave. May lower SPD.",
    ),
    "Shadow Ball": MoveData(
        "Shadow Ball", "Ghost", "special", 20, 1.0, 15, mp_cost=18,
        effect="spd_down", effect_chance=0.2,
        description="Dark energy orb. May lower SPD.",
    ),
    "Dark Pulse": MoveData(
        "Dark Pulse", "Dark", "special", 20, 1.0, 15, mp_cost=18,
        effect="flinch", effect_chance=0.2,
        description="A pulse of dark energy. May flinch.",
    ),
    "Arcane Bolt": MoveData(
        "Arcane Bolt", "Arcane", "special", 20, 1.0, 20, mp_cost=18,
        description="Pure magical bolt.",
    ),
    "Arcane Torrent": MoveData(
        "Arcane Torrent", "Arcane", "special", 30, 0.9, 10, mp_cost=30,
        effect="burn", effect_chance=0.15,
        description="Torrent of arcane fire.",
    ),
    "Bug Buzz": MoveData(
        "Bug Buzz", "Bug", "special", 18, 1.0, 10, mp_cost=14,
        effect="spd_down", effect_chance=0.1,
        description="Resonant buzz attack.",
    ),
    "Poison Spore": MoveData(
        "Poison Spore", "Poison", "special", 12, 0.85, 15, mp_cost=10,
        effect="poison", effect_chance=0.4,
        description="Toxic spores. High poison chance.",
    ),
    "Venom Strike": MoveData(
        "Venom Strike", "Poison", "special", 20, 0.9, 10, mp_cost=20,
        effect="poison", effect_chance=0.5,
        description="Venomous strike. Good poison chance.",
    ),
    "Dragon Pulse": MoveData(
        "Dragon Pulse", "Dragon", "special", 24, 1.0, 10, mp_cost=26,
        description="Dragon energy pulse.",
    ),
    "Rock Blast": MoveData(
        "Rock Blast", "Rock", "special", 16, 0.9, 10, mp_cost=12,
        description="Blasts in rock shards.",
    ),

    # ── Status / Support moves ───────────────────────────────────────────────
    "Heal": MoveData(
        "Heal", "Normal", "status", 0, 1.0, 10, mp_cost=25,
        effect="heal_self", effect_chance=1.0,
        description="Restores ~50% of own max HP.",
    ),
    "Barrier": MoveData(
        "Barrier", "Psychic", "status", 0, 1.0, 20, mp_cost=15,
        effect="def_up", effect_chance=1.0,
        description="Sharply raises own DEF.",
    ),
    "Agility": MoveData(
        "Agility", "Psychic", "status", 0, 1.0, 30, mp_cost=10,
        effect="spe_up", effect_chance=1.0,
        description="Sharply raises own SPE.",
    ),
    "Growl": MoveData(
        "Growl", "Normal", "status", 0, 1.0, 40,
        effect="atk_down", effect_chance=1.0,
        description="A cute growl. Lowers opponent ATK.",
    ),
    "Smokescreen": MoveData(
        "Smokescreen", "Normal", "status", 0, 1.0, 20,
        effect="accuracy_down", effect_chance=1.0,
        description="Obscures vision. Lowers accuracy.",
    ),
    "Spore": MoveData(
        "Spore", "Grass", "status", 0, 0.75, 15, mp_cost=10,
        effect="sleep", effect_chance=1.0,
        description="Puts the target to sleep.",
    ),
    "Charm": MoveData(
        "Charm", "Normal", "status", 0, 1.0, 20,
        effect="charm", effect_chance=1.0,
        description="Adorable. Lowers opponent ATK sharply.",
    ),
    "Sand Attack": MoveData(
        "Sand Attack", "Ground", "status", 0, 1.0, 15,
        effect="accuracy_down", effect_chance=1.0,
        description="Blinds with sand. Lowers accuracy.",
    ),
    "Toxic Powder": MoveData(
        "Toxic Powder", "Poison", "status", 0, 0.75, 35,
        effect="bad_poison", effect_chance=1.0,
        description="Badly poisons target (escalating damage).",
    ),
    "Cleanse": MoveData(
        "Cleanse", "Normal", "status", 0, 1.0, 10, mp_cost=12,
        effect="cure_self", effect_chance=1.0,
        description="Removes own status conditions.",
    ),
    "Protective Ward": MoveData(
        "Protective Ward", "Psychic", "status", 0, 1.0, 10, mp_cost=20,
        effect="protect", effect_chance=1.0,
        description="Protects self this turn from damage.",
    ),
    "Struggle": MoveData(
        "Struggle", "Normal", "physical", 8, 1.0, 999,
        description="Emergency struggle. User takes recoil.",
    ),
}
