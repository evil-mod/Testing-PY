"""AetherMon type effectiveness chart.

Each value is a multiplier (2.0 = super effective, 0.5 = not very, 0.0 = immune).
Defender types not listed default to 1.0.
"""

# TYPE_CHART[attacking_type][defending_type] = multiplier
TYPE_CHART: dict[str, dict[str, float]] = {
    "Normal":   {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Bug": 2.0,
                 "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0, "Ice": 2.0},
    "Water":    {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0,
                 "Rock": 2.0, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5,
                 "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0,
                 "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2.0, "Grass": 0.5, "Electric": 0.5, "Ground": 0.0,
                 "Flying": 2.0, "Dragon": 0.5},
    "Ice":      {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5,
                 "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5,
                 "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0,
                 "Dark": 2.0, "Steel": 2.0},
    "Poison":   {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Bug": 2.0,
                 "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0},
    "Ground":   {"Fire": 2.0, "Grass": 0.5, "Electric": 2.0, "Poison": 2.0,
                 "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying":   {"Grass": 2.0, "Electric": 0.5, "Fighting": 2.0, "Bug": 2.0,
                 "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0,
                 "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5,
                 "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0,
                 "Steel": 0.5},
    "Rock":     {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5,
                 "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost":    {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5,
                 "Steel": 0.5},
    "Dragon":   {"Dragon": 2.0, "Steel": 0.5},
    "Dark":     {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5,
                 "Steel": 0.5},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0,
                 "Rock": 2.0, "Steel": 0.5},
    "Arcane":   {"Normal": 2.0, "Ghost": 2.0, "Steel": 0.5, "Arcane": 0.5},
    "Shadow":   {"Psychic": 2.0, "Ghost": 0.5, "Shadow": 0.5, "Arcane": 2.0},
}

# Elemental colour mapping (for terminal display)
TYPE_COLORS: dict[str, str] = {
    "Normal":   "white",
    "Fire":     "bold red",
    "Water":    "bold blue",
    "Grass":    "bold green",
    "Electric": "bold yellow",
    "Ice":      "bold cyan",
    "Fighting": "red",
    "Poison":   "magenta",
    "Ground":   "yellow",
    "Flying":   "cyan",
    "Psychic":  "bright_magenta",
    "Bug":      "green",
    "Rock":     "dark_orange",
    "Ghost":    "purple",
    "Dragon":   "blue",
    "Dark":     "bright_black",
    "Steel":    "bright_white",
    "Arcane":   "bright_cyan",
    "Shadow":   "bright_magenta",
}


def get_effectiveness(atk_type: str, defender_types: list[str]) -> float:
    """Return combined type multiplier for attacking type vs defending creature."""
    multiplier = 1.0
    move_chart = TYPE_CHART.get(atk_type, {})
    for dtype in defender_types:
        multiplier *= move_chart.get(dtype, 1.0)
    return multiplier
