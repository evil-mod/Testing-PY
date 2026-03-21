"""Automated play-through script for QA testing.

Drives a full new-game session without human input by feeding a
pre-scripted input sequence through sys.stdin (which Rich reads directly).
Raises EOFError when inputs are exhausted to cleanly break input loops.

Run from repo root:
    python scripts/autoplay_test.py
"""
from __future__ import annotations
import io
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Input script ─────────────────────────────────────────────────────────────
# Each line is fed to the next readline() / input() call.
INPUTS = [
    # Title pause
    "",
    # Main menu → 1 New Game
    "1",
    # Trainer name (blank = Red)
    "",
    # Rival name (blank = Blue)
    "",
    # Starter menu → 1 Ignix
    "1",
    # "Starter added" pause
    "",
    # Rival intro dialogue pause
    "",
    # ─── Rival battle: up to 12 turns of Fight → Tackle → result-pause ───
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    # ─── Post-rival pauses ────────────────────────────────────────────────
    "", "",
    # ─── Overworld: Explore (battle) × 2, then Quit ──────────────────────
    # Explore #1
    "1",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    # Explore #2
    "1",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    "1","1","",  "1","1","",  "1","1","",  "1","1","",
    # Town heal
    "2", "1", "",
    # Party info
    "3", "1", "",
    # Save
    "5", "",
    # Quit → confirm yes
    "6", "1",
]


class FakeStdin:
    """A sys.stdin replacement that plays back INPUTS, then raises EOFError."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = [l + "\n" for l in lines]
        self._idx = 0

    def readline(self) -> str:
        if self._idx >= len(self._lines):
            raise EOFError("AutoPlay: input script exhausted")
        line = self._lines[self._idx]
        self._idx += 1
        label = f"[{self._idx-1:03}]"
        # Echo so we can follow along
        sys.stderr.write(f"  {label} → {line.rstrip()!r}\n")
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


def run() -> bool:
    fake = FakeStdin(INPUTS)
    orig_stdin = sys.stdin
    sys.stdin = fake

    # Also patch builtins.input as a fallback
    import builtins
    orig_input = builtins.input

    def _scripted_input(prompt: str = "") -> str:
        sys.stdout.write(str(prompt))
        sys.stdout.flush()
        try:
            line = fake.readline().rstrip("\n")
        except EOFError:
            raise
        sys.stdout.write(line + "\n")
        return line

    builtins.input = _scripted_input

    success = True
    try:
        from src.engine.game import Game
        from src.ui.renderer import DisplayMode
        game = Game(mode=DisplayMode.TEXT)
        game.run()
    except SystemExit as e:
        print(f"\n✅  Game exited cleanly (SystemExit code={e.code})")
    except EOFError as e:
        print(f"\n⚠️   Script exhausted: {e}")
        success = False
    except Exception:
        print(f"\n❌  EXCEPTION during play-through:")
        traceback.print_exc()
        success = False
    finally:
        sys.stdin = orig_stdin
        builtins.input = orig_input

    print(f"\n{'='*60}")
    print(f"Inputs consumed: {fake._idx}/{len(INPUTS)}")
    print(f"Status: {'PASS ✅' if success else 'FAIL ❌'}")
    return success


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)


# ── Input script ─────────────────────────────
# Each entry is fed to the next input() / console.input() call.
# Blank = press Enter.   Digit = menu choice.
INPUTS = [
    # Title screen pause
    "",
    # Main menu → 1 New Game
    "1",
    # Trainer name (blank = Red)
    "",
    # Rival name (blank = Blue)
    "",
    # Starter menu → 1 Ignix
    "1",
    # "Starter added" pause
    "",
    # Rival intro dialogue pause
    "",
    # ─── Rival battle (fight until one side faints) ───────────────────
    # Turn 1: action=Fight(1), move=Tackle(1)
    "1", "1", "",
    # Turn 2: action=Fight(1), move=Tackle(1)
    "1", "1", "",
    # Turn 3: Fight, Tackle
    "1", "1", "",
    # Turn 4: Fight, Tackle
    "1", "1", "",
    # Turn 5: Fight, Tackle (usually enough to end lv-5 battle)
    "1", "1", "",
    # Turn 6-8 safety buffer
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    # ─── Post-rival pauses ────────────────────────────────────────────
    "", "",
    # ─── Overworld loop ──────────────────────────────────────────────
    # Choice 1 = Explore
    "1",
    # Wild battle: Fight(1), first move(1), result pause
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    # ─── Back at overworld ───────────────────────────────────────────
    # Explore another random encounter
    "1",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    "1", "1", "",
    # ─── Party check ─────────────────────────────────────────────────
    "3",  # Party & Stats
    "1",  # View Ignix detail
    "",   # pause
    # ─── Town → heal ─────────────────────────────────────────────────
    "2",  # Town Centre
    "1",  # Heal all
    "",   # pause
    # ─── Save ────────────────────────────────────────────────────────
    "4",  # Travel (test menu)
    "1",  # go to first route
    "",   # pause
    "4",  # Save game  (now choice 4 after travel changed location to slot 1)
    # Wait - after travel the overworld menu is the same.
    # overworld: Save = choice 4
    "",   # pause
    # ─── Quit ────────────────────────────────────────────────────────
    "5",  # Save game (slot 5 is Save)
    "",
    "6",  # Quit
    "1",  # Yes, quit
]


class ScriptedInput:
    """Replaces builtins.input and console.input with scripted responses."""

    def __init__(self, responses: list[str]) -> None:
        self._resp = list(responses)
        self._idx = 0
        self._log: list[tuple[str, str]] = []   # (prompt, answer)

    def __call__(self, prompt: str = "") -> str:
        if self._idx >= len(self._resp):
            answer = ""
            label = "[AUTO-EXTRA]"
        else:
            answer = self._resp[self._idx]
            label = f"[{self._idx:03}]"
            self._idx += 1
        self._log.append((prompt.strip(), answer))
        # Print so output is visible
        sys.stdout.write(f"\n{label} PROMPT: {prompt!r}  → INPUT: {answer!r}\n")
        sys.stdout.flush()
        return answer


def run() -> bool:
    scripted = ScriptedInput(INPUTS)

    # Patch both builtins.input and Rich console.input
    import builtins
    original_input = builtins.input
    builtins.input = scripted

    try:
        import rich.console as _rc
        original_console_input = _rc.Console.input
        _rc.Console.input = lambda self, prompt="", **kw: scripted(prompt)
    except Exception:
        original_console_input = None

    success = True
    try:
        from src.engine.game import Game
        from src.ui.renderer import DisplayMode
        game = Game(mode=DisplayMode.TEXT)
        game.run()
    except SystemExit as e:
        print(f"\n✅  Game exited cleanly (SystemExit code={e.code})")
    except Exception:
        print(f"\n❌  EXCEPTION during play-through:")
        traceback.print_exc()
        success = False
    finally:
        builtins.input = original_input
        if original_console_input is not None:
            import rich.console as _rc
            _rc.Console.input = original_console_input

    print(f"\n{'='*60}")
    print(f"Inputs consumed: {scripted._idx}/{len(INPUTS)}")
    print(f"Status: {'PASS ✅' if success else 'FAIL ❌'}")
    return success


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
