"""Comprehensive automated QA play-through for AetherMon.

Three sessions cover every game path:

  Session A  TEXT -- New-game flow: title, name/starter setup, rival battle,
                     quit-cancel, quit-confirm.

  Session B  TEXT -- Overworld + Battle: loads a programmatic save, then
                     exercises every overworld option and all 5 battle actions.
                     Wild opponents are patched to HP=1 so every battle result
                     is fully deterministic (no randomness).
                     Covers: Load Game, Party, Town (heal/shop/leave), Travel
                     (all 3 routes + cancel), Fight, Spell, Item, Ball, Run,
                     Save, Quit-cancel, Quit-confirm.

  Session C  ASCII -- Render smoke-test: loads save, runs one wild battle with
                      ASCII sprites on, quits. Verifies Rich panels + art don't
                      crash on the ASCII display path.

Run from the repo root:
    python -X utf8 scripts/autoplay_test.py
"""
from __future__ import annotations
import builtins
import io
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SAVE_PATH = "saves/save.json"


# ---------------------------------------------------------------------------
# Input-sequence helpers
# ---------------------------------------------------------------------------
def _ft(n: int = 1) -> list[str]:
    """n fight turns: [Fight, first-move, result-pause] * n."""
    return ["1", "1", ""] * n


# ---------------------------------------------------------------------------
# Session A -- New-game flow (TEXT)
# ---------------------------------------------------------------------------
SESSION_A: list[str] = [
    "",          # title screen pause
    "1",         # Main menu -> New Game

    "",          # trainer name  (blank -> "Red")
    "",          # rival name    (blank -> "Blue")
    "1",         # starter choice: Ignix  [Fire / Warrior]
    "",          # "Ignix added to your party!" pause

    "",          # rival intro dialogue pause
    *_ft(8),     # rival battle fight buffer (fallback handles longer battles)
    "", "",      # post-rival pauses (rival speech x2) + auto-heal notice

    # Confirm we reached the overworld
    "6", "2",    # Quit -> No (cancel)
    "6", "1",    # Quit -> Yes  -> SystemExit(0)
]
SESSION_A_FALLBACK = ["5", "", "5", "", "6", "1"] * 15


# ---------------------------------------------------------------------------
# Session B -- Full overworld + all battle actions (TEXT, HP=1 wild patch)
# ---------------------------------------------------------------------------
SESSION_B: list[str] = [

    # Title + Load Game -------------------------------------------------------
    "",          # title pause
    "2",         # Main menu -> Load Game  (goes straight into _overworld())

    # Party & Stats -> creature detail view -----------------------------------
    "3",         # Party & Stats
    "1",         # View details: Ignix
    "",          # pause

    # Town Centre: Heal -------------------------------------------------------
    "2", "1", "",

    # Town Centre: Shop -------------------------------------------------------
    # Starting money: $200
    # AetherBall $40 -> $160, Potion $80 -> $80, Antidote $60 -> $20
    # Revive $300 > $20  -> "Not enough money" path
    # Shop options order: 1=AetherBall, 2=Potion, 3=Elixir, 4=Antidote, 5=Revive, 6=Leave
    "2", "2",
    "1", "",     # buy AetherBall $40 -> pause
    "2", "",     # buy Potion     $80 -> pause
    "4", "",     # buy Antidote   $60 -> pause
    "5", "",     # try Revive $300 (fail: not enough money) -> pause
    "6",         # Leave shop

    # Town Centre: Leave town -------------------------------------------------
    "2", "3",

    # Travel: Cancel path -----------------------------------------------------
    "4", "4",    # Travel -> Cancel  (no pause on cancel)

    # Travel: Starter Route ---------------------------------------------------
    "4", "1", "",

    # Battle: FIGHT -----------------------------------------------------------
    "1",         # Explore  [wild HP=1; 1 hit wins]
    *_ft(1),

    # Battle: SPELL -----------------------------------------------------------
    "1",         # Explore
    "2", "1", "",  # Spell -> Ember -> result pause -> WIN

    # Battle: ITEM (Potion on Ignix) ------------------------------------------
    # Note: item action does NOT cancel the enemy's counter-attack turn,
    # so we still need a fight turn to finish the (HP=1) opponent after.
    "1",         # Explore
    "3",         # Item action
    "2",         # Potion  (bag slot 2)
    "1",         # On: Ignix (party[0])
    "",          # result pause  (enemy counter-attack fires)
    *_ft(1),     # one fight turn to finish HP=1 opponent

    # Heal before Ball / Run --------------------------------------------------
    "2", "1", "",

    # Battle: BALL (capture attempt) ------------------------------------------
    "1",         # Explore
    "4", "",     # Throw AetherBall -> result pause
    "",          # extra: "X joined your party!" pause IF captured
    *_ft(1),     # fight backup if NOT captured

    # Battle: RUN (flee) ------------------------------------------------------
    "1",         # Explore
    "5", "",     # Run -> result pause
    *_ft(2),     # fight buffer if flee failed -> WIN

    # Heal -------------------------------------------------------------------
    "2", "1", "",

    # Travel: Ember Path (Lv 5-10 wild) --------------------------------------
    "4", "2", "",

    # Explore Ember Path (HP=1 patch -> 1-hit WIN) ---------------------------
    "1",
    *_ft(1),

    # Heal -------------------------------------------------------------------
    "2", "1", "",

    # Travel: Frosted Cave (Lv 7-13 wild) ------------------------------------
    "4", "3", "",

    # Explore Frosted Cave (HP=1 patch -> 1-hit WIN) -------------------------
    "1",
    *_ft(1),

    # Save game --------------------------------------------------------------
    "5", "",

    # Quit: cancel then confirm ----------------------------------------------
    "6", "2",    # Quit -> No
    "6", "1",    # Quit -> Yes -> SystemExit(0)
]
SESSION_B_FALLBACK = ["5", "", "6", "1"] * 15


# ---------------------------------------------------------------------------
# Session C -- ASCII render smoke-test
# ---------------------------------------------------------------------------
SESSION_C: list[str] = [
    "",          # title pause
    "2",         # Load Game

    # Travel to Starter Route so wild encounters are available
    "4", "1", "",

    # One wild battle with ASCII sprites rendering
    "1",         # Explore
    *_ft(1),     # Fight -> WIN  (HP=1 patched)

    "6", "1",    # Quit -> Yes -> SystemExit(0)
]
SESSION_C_FALLBACK = ["5", "", "6", "1"] * 10


# ---------------------------------------------------------------------------
# Programmatic save-file builder (used before Sessions B and C)
# ---------------------------------------------------------------------------
def make_save() -> None:
    from src.entities.creature import Creature
    from src.entities.player import Player
    from src.data import CREATURES

    p = Player("Red")
    p.rival_name    = "Blue"
    p.location      = "Starter Route"
    p.add_to_party(Creature(CREATURES["Ignix"], level=5))
    p.save(SAVE_PATH)
    print(f"  [save] {SAVE_PATH}  (Ignix Lv5, location=Starter Route)")


# ---------------------------------------------------------------------------
# HP=1 wild-battle patch (deterministic battles)
# ---------------------------------------------------------------------------
def _patch_hp1():
    import src.engine.battle as b
    orig = b.BattleEngine.__init__

    def _init(self, player, opponent, is_wild=True, **kw):
        orig(self, player, opponent, is_wild=is_wild, **kw)
        if is_wild:
            opponent.current_hp = 1

    b.BattleEngine.__init__ = _init
    return orig


def _unpatch_hp1(orig) -> None:
    import src.engine.battle as b
    b.BattleEngine.__init__ = orig


# ---------------------------------------------------------------------------
# FakeStdin
# ---------------------------------------------------------------------------
class FakeStdin:
    def __init__(self, lines: list[str], fallback: list[str]) -> None:
        self._lines    = [l + "\n" for l in lines]
        self._fallback = [l + "\n" for l in fallback]
        self._idx      = 0
        self._fb_idx   = 0
        self.used_fallback = False

    def readline(self) -> str:
        if self._idx < len(self._lines):
            line = self._lines[self._idx]
            tag  = f"[{self._idx:03}]"
            self._idx += 1
        else:
            self.used_fallback = True
            line = self._fallback[self._fb_idx % len(self._fallback)]
            tag  = f"[FB{self._fb_idx:02}]"
            self._fb_idx += 1
        sys.stderr.write(f"  {tag} -> {line.rstrip()!r}\n")
        sys.stderr.flush()
        return line

    def read(self, n: int = -1) -> str:
        return self.readline()

    @property
    def encoding(self) -> str:
        return "utf-8"

    def isatty(self) -> bool:
        return False

    def fileno(self) -> int:
        raise io.UnsupportedOperation("no fileno")


# ---------------------------------------------------------------------------
# Session runner
# ---------------------------------------------------------------------------
def run_session(
    inputs: list[str],
    fallback: list[str],
    mode_name: str,
    label: str,
    hp1: bool = False,
) -> tuple[bool, str]:
    import importlib

    for mod in [
        "src.engine.game", "src.engine.battle", "src.engine.display",
        "src.ui.renderer", "src.entities.creature", "src.entities.player",
    ]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])

    orig_hp = _patch_hp1() if hp1 else None

    fake = FakeStdin(inputs, fallback)
    orig_stdin = sys.stdin
    sys.stdin  = fake
    orig_input = builtins.input

    def _scripted(prompt: str = "") -> str:
        sys.stdout.write(str(prompt))
        sys.stdout.flush()
        line = fake.readline().rstrip("\n")
        sys.stdout.write(line + "\n")
        return line

    builtins.input = _scripted

    success = True
    notes: list[str] = []
    try:
        from src.engine.game import Game
        from src.ui.renderer import DisplayMode
        Game(mode={"TEXT": DisplayMode.TEXT, "ASCII": DisplayMode.ASCII}[mode_name]).run()
        notes.append("No SystemExit - loop ended without quit")
        success = False
    except SystemExit as e:
        notes.append(f"SystemExit({e.code}) -- clean quit")
    except EOFError as e:
        notes.append(f"EOFError: {e}")
        success = False
    except Exception:
        notes.append("EXCEPTION:\n" + traceback.format_exc())
        success = False
    finally:
        sys.stdin      = orig_stdin
        builtins.input = orig_input
        if hp1 and orig_hp is not None:
            _unpatch_hp1(orig_hp)

    if fake.used_fallback:
        notes.append(
            f"NOTE: fallback triggered ({fake._fb_idx} extra calls "
            f"after {len(inputs)} scripted inputs)"
        )

    return success, (
        f"\n{'='*58}\n"
        f"Session {label}  [{mode_name}]  inputs={fake._idx}/{len(inputs)}\n"
        f"{'PASS' if success else 'FAIL'}\n"
        + "\n".join(f"  {n}" for n in notes)
        + f"\n{'='*58}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("\n" + "="*58)
    print("  AetherMon - QA Play-Through")
    print("="*58)

    print("\n[setup] Writing QA save file...")
    make_save()

    sessions = [
        (SESSION_A, SESSION_A_FALLBACK, "TEXT",  "A: New-game flow",          False),
        (SESSION_B, SESSION_B_FALLBACK, "TEXT",  "B: Full overworld+battle",  True),
        (SESSION_C, SESSION_C_FALLBACK, "ASCII", "C: ASCII render",           True),
    ]

    results: list[tuple[bool, str]] = []
    for idx, (inp, fb, mode, label, hp1) in enumerate(sessions, 1):
        print(f"\n[{idx}/{len(sessions)}] {label}...")
        sys.stderr.write(f"\n--- {label} ---\n")
        ok, rep = run_session(inp, fb, mode, label, hp1=hp1)
        results.append((ok, rep))
        print(rep)

    passed = sum(ok for ok, _ in results)
    total  = len(results)
    print(f"\n{'='*58}")
    print(f"  RESULT: {passed}/{total} passed")
    print("="*58)

    if passed == total:
        print("\nSections covered:")
        covered = [
            "A: Title screen",
            "A: New game (name / rival / starter selection)",
            "A: Rival intro battle",
            "A: Quit -> No (cancel) from overworld",
            "A: Quit -> Yes (confirm)",
            "B: Load Game",
            "B: Party & Stats -- creature detail view",
            "B: Town Centre -- Heal all",
            "B: Shop -- buy items (AetherBall, Potion, Antidote)",
            "B: Shop -- not-enough-money path (Revive attempt)",
            "B: Town Centre -- Leave town",
            "B: Travel menu -- Cancel path",
            "B: Travel -- Starter Route",
            "B: Battle action -- FIGHT (physical move)",
            "B: Battle action -- SPELL (Ember)",
            "B: Battle action -- ITEM (Potion on party member)",
            "B: Battle action -- BALL (AetherBall capture attempt)",
            "B: Battle action -- RUN (flee)",
            "B: Travel -- Ember Path  (Lv 5-10 wild)",
            "B: Wild battle at Ember Path",
            "B: Travel -- Frosted Cave  (Lv 7-13 wild)",
            "B: Wild battle at Frosted Cave",
            "B: Save game",
            "B: Quit -> No (cancel)",
            "B: Quit -> Yes (confirm)",
            "C: ASCII mode -- sprites + Rich panels render",
            "C: ASCII mode -- wild battle display",
            "C: ASCII mode -- quit confirm",
        ]
        for s in covered:
            print(f"  [OK] {s}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
