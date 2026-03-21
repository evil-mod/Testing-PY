"""AetherMon creature definitions.

Each creature entry defines base stats (level 5 equivalents) plus its
elemental types, creature class, and available move/spell lists.
"""
from dataclasses import dataclass, field


@dataclass
class CreatureTemplate:
    name: str
    types: list[str]
    creature_class: str          # key into CLASSES dict
    # Base stats (at level 1; scaled by level formula)
    base_hp: int
    base_atk: int
    base_def: int
    base_spa: int                # special attack
    base_spd: int                # special defense
    base_spe: int                # speed
    base_mp: int                 # base mana pool
    moves: list[str]             # physical/status moves available
    spells: list[str]            # special/spell moves available
    catch_rate: int = 180        # 0–255; higher = easier
    exp_yield: int = 60
    description: str = ""
    sprite_file: str = ""        # filename in assets/sprites/creatures/


CREATURES: dict[str, CreatureTemplate] = {
    # ── Starter trio ─────────────────────────────────────────────────────────
    "Ignix": CreatureTemplate(
        name="Ignix",
        types=["Fire"],
        creature_class="Warrior",
        base_hp=45, base_atk=55, base_def=45,
        base_spa=50, base_spd=40, base_spe=60, base_mp=30,
        moves=["Scratch", "Slash", "Flame Punch", "Iron Tail"],
        spells=["Ember", "Fireball"],
        catch_rate=45, exp_yield=100,
        description="A hot-blooded lizard warrior wreathed in smoldering embers.",
        sprite_file="ignix.png",
    ),
    "Aqualis": CreatureTemplate(
        name="Aqualis",
        types=["Water"],
        creature_class="Ranger",
        base_hp=50, base_atk=48, base_def=60,
        base_spa=50, base_spd=55, base_spe=50, base_mp=40,
        moves=["Tackle", "Bite", "Wing Attack"],
        spells=["Bubble", "Water Pulse", "Psybeam"],
        catch_rate=45, exp_yield=100,
        description="A sleek water rabbit ranger that rides ocean currents with ease.",
        sprite_file="aqualis.png",
    ),
    "Verdari": CreatureTemplate(
        name="Verdari",
        types=["Grass", "Poison"],
        creature_class="Mage",
        base_hp=45, base_atk=45, base_def=50,
        base_spa=58, base_spd=50, base_spe=42, base_mp=65,
        moves=["Vine Whip", "Poison Sting"],
        spells=["Seed Bomb", "Solar Blast", "Poison Spore", "Venom Strike"],
        catch_rate=45, exp_yield=100,
        description="A verdant plant mage that channels nature's arcane energies.",
        sprite_file="verdari.png",
    ),

    # ── Common wild creatures ─────────────────────────────────────────────────
    "Voltix": CreatureTemplate(
        name="Voltix",
        types=["Electric"],
        creature_class="Rogue",
        base_hp=38, base_atk=52, base_def=30,
        base_spa=55, base_spd=35, base_spe=92, base_mp=45,
        moves=["Scratch", "Quick Strike", "Thunder Punch"],
        spells=["Thunder Shock", "Thunderbolt"],
        catch_rate=190, exp_yield=80,
        description="A lightning-quick electric rodent that shocks first and asks later.",
        sprite_file="voltix.png",
    ),
    "Galebird": CreatureTemplate(
        name="Galebird",
        types=["Normal", "Flying"],
        creature_class="Ranger",
        base_hp=42, base_atk=46, base_def=42,
        base_spa=40, base_spd=42, base_spe=58, base_mp=30,
        moves=["Peck", "Wing Attack", "Quick Strike"],
        spells=["Gust", "Razor Wind"],
        catch_rate=255, exp_yield=55,
        description="A swift wind bird that scouts ahead and strikes from above.",
        sprite_file="galebird.png",
    ),
    "Shadowrat": CreatureTemplate(
        name="Shadowrat",
        types=["Dark"],
        creature_class="Rogue",
        base_hp=32, base_atk=58, base_def=32,
        base_spa=38, base_spd=35, base_spe=72, base_mp=30,
        moves=["Tackle", "Bite", "Crunch", "Shadow Claw"],
        spells=["Dark Pulse", "Shadow Ball"],
        catch_rate=220, exp_yield=60,
        description="A sneaky dark rodent that ambushes prey from the shadows.",
        sprite_file="shadowrat.png",
    ),
    "Spikeon": CreatureTemplate(
        name="Spikeon",
        types=["Rock", "Ground"],
        creature_class="Warrior",
        base_hp=48, base_atk=80, base_def=100,
        base_spa=30, base_spd=30, base_spe=20, base_mp=20,
        moves=["Tackle", "Rock Throw", "Iron Tail"],
        spells=["Rock Blast"],
        catch_rate=200, exp_yield=70,
        description="A walking boulder warrior with razor-sharp stone spines.",
        sprite_file="spikeon.png",
    ),
    "Venombug": CreatureTemplate(
        name="Venombug",
        types=["Bug", "Poison"],
        creature_class="Mage",
        base_hp=40, base_atk=32, base_def=35,
        base_spa=55, base_spd=38, base_spe=48, base_mp=55,
        moves=["Poison Sting", "Bite"],
        spells=["Bug Buzz", "Poison Spore", "Venom Strike", "Toxic Powder"],
        catch_rate=230, exp_yield=55,
        description="A venomous insect mage that brews toxic spells from its own venom.",
        sprite_file="venombug.png",
    ),
    "Clawer": CreatureTemplate(
        name="Clawer",
        types=["Fighting"],
        creature_class="Berserker",
        base_hp=42, base_atk=80, base_def=35,
        base_spa=35, base_spd=35, base_spe=70, base_mp=20,
        moves=["Scratch", "Karate Chop", "Slash Combo", "Fury Swipes"],
        spells=["Arcane Bolt"],
        catch_rate=180, exp_yield=70,
        description="An aggressive fighting simian that goes berserk when cornered.",
        sprite_file="clawer.png",
    ),
    "Seedling": CreatureTemplate(
        name="Seedling",
        types=["Grass"],
        creature_class="Priest",
        base_hp=52, base_atk=32, base_def=45,
        base_spa=42, base_spd=52, base_spe=40, base_mp=70,
        moves=["Tackle", "Vine Whip", "Growl"],
        spells=["Seed Bomb", "Heal", "Cleanse", "Spore"],
        catch_rate=235, exp_yield=50,
        description="A gentle plant priest that heals allies and puts enemies to sleep.",
        sprite_file="seedling.png",
    ),
    "Frostfin": CreatureTemplate(
        name="Frostfin",
        types=["Water", "Ice"],
        creature_class="Mage",
        base_hp=46, base_atk=42, base_def=42,
        base_spa=60, base_spd=48, base_spe=46, base_mp=60,
        moves=["Tackle", "Bite", "Ice Punch"],
        spells=["Bubble", "Ice Shard", "Blizzard", "Water Pulse"],
        catch_rate=190, exp_yield=85,
        description="A frozen fish mage that flash-freezes foes with crystalline spells.",
        sprite_file="frostfin.png",
    ),
    "Pyrowolf": CreatureTemplate(
        name="Pyrowolf",
        types=["Fire", "Dark"],
        creature_class="Berserker",
        base_hp=44, base_atk=72, base_def=38,
        base_spa=52, base_spd=40, base_spe=68, base_mp=35,
        moves=["Bite", "Crunch", "Flame Punch"],
        spells=["Ember", "Dark Pulse", "Fireball"],
        catch_rate=160, exp_yield=95,
        description="A berserker wolf of fire and shadow — beautiful and terrifying.",
        sprite_file="pyrowolf.png",
    ),
    "Glowshroom": CreatureTemplate(
        name="Glowshroom",
        types=["Grass", "Arcane"],
        creature_class="Shaman",
        base_hp=50, base_atk=38, base_def=48,
        base_spa=65, base_spd=52, base_spe=35, base_mp=75,
        moves=["Tackle", "Vine Whip"],
        spells=["Seed Bomb", "Arcane Bolt", "Arcane Torrent", "Heal", "Spore"],
        catch_rate=150, exp_yield=90,
        description="A bioluminescent mushroom shaman channeling forest arcane energy.",
        sprite_file="glowshroom.png",
    ),
    "Arceon": CreatureTemplate(
        name="Arceon",
        types=["Arcane"],
        creature_class="Mage",
        base_hp=42, base_atk=40, base_def=42,
        base_spa=75, base_spd=55, base_spe=55, base_mp=90,
        moves=["Shadow Claw", "Quick Strike"],
        spells=["Arcane Bolt", "Arcane Torrent", "Psychic Burst", "Shadow Ball"],
        catch_rate=75, exp_yield=130,
        description="A rare arcane fox overflowing with magical energy.",
        sprite_file="arceon.png",
    ),

    # ── Rival starter (always opposite to player) ─────────────────────────────
    "Rival_Ignix": CreatureTemplate(
        name="Ignix",
        types=["Fire"],
        creature_class="Warrior",
        base_hp=45, base_atk=55, base_def=45,
        base_spa=50, base_spd=40, base_spe=60, base_mp=30,
        moves=["Scratch", "Ember", "Slash"],
        spells=["Ember", "Fireball"],
        catch_rate=45, exp_yield=100,
        description="Your rival's Ignix.",
        sprite_file="ignix.png",
    ),
    "Rival_Aqualis": CreatureTemplate(
        name="Aqualis",
        types=["Water"],
        creature_class="Ranger",
        base_hp=50, base_atk=48, base_def=60,
        base_spa=50, base_spd=55, base_spe=50, base_mp=40,
        moves=["Tackle", "Bubble", "Bite"],
        spells=["Bubble", "Water Pulse"],
        catch_rate=45, exp_yield=100,
        description="Your rival's Aqualis.",
        sprite_file="aqualis.png",
    ),
    "Rival_Verdari": CreatureTemplate(
        name="Verdari",
        types=["Grass", "Poison"],
        creature_class="Mage",
        base_hp=45, base_atk=45, base_def=50,
        base_spa=58, base_spd=50, base_spe=42, base_mp=65,
        moves=["Vine Whip", "Seed Bomb", "Poison Sting"],
        spells=["Seed Bomb", "Poison Spore"],
        catch_rate=45, exp_yield=100,
        description="Your rival's Verdari.",
        sprite_file="verdari.png",
    ),
}

# Wild encounter tables  [location_name] -> [(creature_name, min_level, max_level, weight)]
WILD_ENCOUNTERS: dict[str, list[tuple[str, int, int, int]]] = {
    "Starter Route": [
        ("Galebird",   3,  6, 35),
        ("Shadowrat",  3,  6, 35),
        ("Venombug",   3,  5, 20),
        ("Seedling",   4,  6, 10),
    ],
    "Ember Path": [
        ("Voltix",     5, 10, 30),
        ("Clawer",     5,  9, 30),
        ("Pyrowolf",   6, 10, 15),
        ("Spikeon",    5,  8, 25),
    ],
    "Frosted Cave": [
        ("Frostfin",   7, 12, 30),
        ("Spikeon",    7, 11, 30),
        ("Glowshroom", 8, 12, 20),
        ("Arceon",    10, 13,  5),
    ],
}
