"""Hardcoded ASCII art sprites for all AetherMon creatures.

Each sprite is a list of strings (lines). Aim for ~12 chars wide × 10 lines.
"""

SPRITES: dict[str, list[str]] = {
    "Ignix": [
        r"   /\\  ",
        r"  / \\ \\",
        r" | o o |",
        r"  \\___/ ",
        r" /|   |\\ ",
        r"/ |===| \\",
        r"  || ||  ",
        r"  /\\ /\\ ",
    ],
    "Aqualis": [
        r"  (\\_/) ",
        r"  (o . o)",
        r"  (> <)  ",
        r" /|   |\\ ",
        r"| |~~~| |",
        r"|  \\_/  |",
        r" \\ vvv / ",
        r"  ~~_~~  ",
    ],
    "Verdari": [
        r"  (*)(*) ",
        r" ( leaf ) ",
        r"  (o ~ o)",
        r"  | ||| |",
        r" /|| ||\\ ",
        r"| || || |",
        r"  \\ | /  ",
        r"~~~\\|/~~~",
    ],
    "Voltix": [
        r"  /\\  /\\ ",
        r" / *  * \\",
        r"| o  . o|",
        r" \\  :  / ",
        r"  |~~~|  ",
        r"  (( ))  ",
        r" //_|_\\\\ ",
        r"           ",
    ],
    "Galebird": [
        r"    /\\   ",
        r"   /  \\  ",
        r"~~/ o  \\~~",
        r" /  ^   \\ ",
        r"|   |   |",
        r" \\  |  / ",
        r"  \\ | /  ",
        r" __\\|/__ ",
    ],
    "Shadowrat": [
        r"  /\\  /\\ ",
        r" /  \\/  \\",
        r"| . .  . |",
        r"|   ___  |",
        r" \\  \\_/  /",
        r"  |   |  ",
        r" /|   |\\ ",
        r"~~ ~~~ ~~ ",
    ],
    "Spikeon": [
        r" /^\\/^\\ ",
        r"|/||\\||\\|",
        r"| [o o] |",
        r"|  ---  |",
        r"|/|===|\\|",
        r" \\||||/  ",
        r"  || ||  ",
        r" _||_||_ ",
    ],
    "Venombug": [
        r"  (   )  ",
        r" (( * )) ",
        r"((o . o))",
        r" (( B )) ",
        r" //|||\\  ",
        r"//// \\\\  ",
        r" /(\\ /)\\  ",
        r"  \\___/  ",
    ],
    "Clawer": [
        r"  /\\__/\\ ",
        r" /  --  \\",
        r"| (o)(o) |",
        r"| /    \\ |",
        r"|/  !!  \\|",
        r" \\ /\\/\\ / ",
        r"  |    |  ",
        r"  (____) ",
    ],
    "Seedling": [
        r"   *  *  ",
        r"  (~~~~) ",
        r" |(o  o)| ",
        r" | \\__/ | ",
        r"  \\|~~|/ ",
        r"   |  |  ",
        r"   |  |  ",
        r" __|  |__",
    ],
    "Frostfin": [
        r"   >><   ",
        r"  >o  o< ",
        r" > (  ) < ",
        r"  \\~~~~/ ",
        r"   |  |  ",
        r"  /|  |\\ ",
        r" \\\\|  |// ",
        r"  \\\\_\\_//  ",
    ],
    "Pyrowolf": [
        r"  /\\ /\\ ",
        r" / o  o \\",
        r"|  /--\\  |",
        r"|_/ ** \\_|",
        r" /      \\  ",
        r"| ~~||~~ |",
        r" \\  ||  / ",
        r"  \\_||_/  ",
    ],
    "Glowshroom": [
        r" (  ***  )",
        r"(*       *)",
        r"( * o o * )",
        r" (*  ~  *) ",
        r"  \\|   |/ ",
        r"   |   |  ",
        r"   |   |  ",
        r" ~~|___|~~ ",
    ],
    "Arceon": [
        r"  /\\   ",
        r" /  \\  ",
        r"|*  *|  ",
        r"|o..o|  ",
        r" \\^^/ ~~",
        r" /  \\ ~~",
        r"/    \\  ",
        r"\\____/  ",
    ],
    "UNKNOWN": [
        r" ??????? ",
        r"?       ?",
        r"? o   o ?",
        r"?   _   ?",
        r"?  ~~~  ?",
        r"?       ?",
        r" ??????? ",
        r"         ",
    ],
}


def get_sprite(name: str) -> list[str]:
    """Return ASCII art lines for a creature. Falls back to UNKNOWN."""
    return SPRITES.get(name, SPRITES["UNKNOWN"])


def sprite_width(name: str) -> int:
    lines = get_sprite(name)
    return max(len(l) for l in lines) if lines else 10


def side_by_side(left_name: str, right_name: str, padding: int = 4) -> list[str]:
    """Return lines with two sprites placed side-by-side."""
    left = get_sprite(left_name)
    right = get_sprite(right_name)
    max_h = max(len(left), len(right))
    lw = max(len(l) for l in left) if left else 10
    rw = max(len(r) for r in right) if right else 10

    left  = left  + [""] * (max_h - len(left))
    right = right + [""] * (max_h - len(right))
    gap = " " * padding

    return [
        l.ljust(lw) + gap + r.ljust(rw)
        for l, r in zip(left, right)
    ]
