"""Tests for creature mechanics."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.entities.creature import Creature
from src.data.creatures_data import CREATURES
from src.data.classes_data import CLASSES


@pytest.fixture
def ignix():
    return Creature(CREATURES["Ignix"], level=10)


@pytest.fixture
def verdari():
    return Creature(CREATURES["Verdari"], level=10)


class TestCreatureCreation:
    def test_stats_computed(self, ignix):
        assert ignix.max_hp > 0
        assert ignix.max_mp > 0
        assert ignix.base_atk > 0

    def test_warrior_atk_mult(self, ignix):
        # Ignix is a Warrior with 1.3 atk mult
        base = CREATURES["Ignix"].base_atk
        expected_min = int(base * 1.0)   # at minimum
        assert ignix.base_atk >= expected_min

    def test_mage_mp_mult(self, verdari):
        # Verdari is a Mage with 1.8 mp mult
        assert verdari.max_mp > verdari.max_hp * 0.3  # rough check

    def test_hp_equals_max_on_create(self, ignix):
        assert ignix.current_hp == ignix.max_hp

    def test_types_correct(self, verdari):
        assert "Grass" in verdari.types
        assert "Poison" in verdari.types


class TestStatusEffects:
    def test_burn_applied(self, ignix):
        result = ignix.apply_status("burn")
        assert result is True
        assert ignix.status == "burn"

    def test_burn_tick_damage(self, ignix):
        ignix.apply_status("burn")
        hp_before = ignix.current_hp
        msgs = ignix.tick_status()
        assert ignix.current_hp < hp_before
        assert any("burn" in m.lower() for m in msgs)

    def test_double_status_blocked(self, ignix):
        ignix.apply_status("burn")
        result = ignix.apply_status("poison")
        assert result is False
        assert ignix.status == "burn"

    def test_bad_poison_escalates(self, ignix):
        ignix.apply_status("bad_poison")
        ignix.tick_status()
        dmg1 = ignix.max_hp - ignix.current_hp
        ignix.tick_status()
        dmg2 = ignix.max_hp - ignix.current_hp - dmg1
        assert dmg2 > dmg1  # escalating

    def test_priest_passive_heals(self):
        seedling = Creature(CREATURES["Seedling"], level=10)
        seedling.current_hp = seedling.max_hp // 2
        pre = seedling.current_hp
        msgs = seedling.tick_status()
        # Priest passive should restore HP
        assert seedling.current_hp > pre

    def test_sleep_turns(self, ignix):
        ignix.apply_status("sleep", turns=3)
        for _ in range(3):
            still_asleep, _ = ignix.tick_sleep()
        # After 3 turns sleep counter should be exhausted
        still_asleep, msg = ignix.tick_sleep()
        assert not still_asleep


class TestLeveling:
    def test_gain_exp_levels_up(self):
        c = Creature(CREATURES["Galebird"], level=5)
        # Force a level-up by feeding huge EXP
        msgs = c.gain_exp(9999)
        assert c.level > 5
        assert any("grew to level" in m for m in msgs)

    def test_stats_increase_on_levelup(self):
        c = Creature(CREATURES["Voltix"], level=5)
        old_hp = c.max_hp
        c.gain_exp(9999)
        assert c.max_hp > old_hp


class TestMoveUsability:
    def test_can_use_physical_no_mp(self, ignix):
        assert ignix.can_use_move("Scratch")

    def test_cannot_use_spell_no_mp(self, ignix):
        ignix.current_mp = 0
        # Fireball costs 20 MP
        assert not ignix.can_use_move("Fireball")

    def test_pp_decrements(self, ignix):
        pp_before = ignix.move_pp.get("Scratch", 0)
        ignix.use_move_pp("Scratch")
        assert ignix.move_pp["Scratch"] == pp_before - 1

    def test_struggle_when_no_pp(self, ignix):
        for m in ignix.move_pp:
            ignix.move_pp[m] = 0
        ignix.current_mp = 0
        available = ignix.available_moves()
        assert available == ["Struggle"]


class TestCapture:
    def test_hp_affects_capture_rate(self):
        from src.engine.battle import BattleEngine
        from src.entities.player import Player

        player = Player("TestPlayer")
        wild = Creature(CREATURES["Galebird"], level=5)
        player.add_to_party(Creature(CREATURES["Ignix"], level=5))
        engine = BattleEngine(player, wild, is_wild=True)

        wild.current_hp = wild.max_hp
        rate_full = engine._calc_capture_rate()

        wild.current_hp = 1
        rate_low = engine._calc_capture_rate()

        assert rate_low > rate_full

    def test_sleep_bonus(self):
        from src.engine.battle import BattleEngine
        from src.entities.player import Player

        player = Player("TestPlayer")
        wild = Creature(CREATURES["Galebird"], level=5)
        player.add_to_party(Creature(CREATURES["Ignix"], level=5))
        engine = BattleEngine(player, wild, is_wild=True)

        wild.current_hp = wild.max_hp // 2
        rate_normal = engine._calc_capture_rate()

        wild.apply_status("sleep", turns=3)
        rate_sleep = engine._calc_capture_rate()

        assert rate_sleep > rate_normal
