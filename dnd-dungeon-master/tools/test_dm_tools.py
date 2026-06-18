#!/usr/bin/env python3
"""
Tests for dm_tools.py — prove the mechanics are deterministic and correct.

Run:  python3 test_dm_tools.py
Exits non-zero on the first failure. Stdlib only (unittest).
"""

import os
import random
import shutil
import tempfile
import unittest

import dm_tools as dt


class DiceTests(unittest.TestCase):
    def test_constant_only(self):
        r = dt.roll_dice("5", rng=random.Random(1))
        self.assertEqual(r["total"], 5)

    def test_seeded_is_reproducible(self):
        a = dt.roll_dice("3d6+2", rng=random.Random(42))
        b = dt.roll_dice("3d6+2", rng=random.Random(42))
        self.assertEqual(a["total"], b["total"])
        self.assertEqual(a["breakdown"], b["breakdown"])

    def test_bounds(self):
        rng = random.Random(7)
        for _ in range(200):
            total = dt.roll_dice("2d6+3", rng=rng)["total"]
            self.assertGreaterEqual(total, 5)   # 1+1+3
            self.assertLessEqual(total, 15)      # 6+6+3

    def test_subtraction_term(self):
        r = dt.roll_dice("10-1d4", rng=random.Random(3))
        self.assertTrue(6 <= r["total"] <= 9)

    def test_keep_highest(self):
        # 4d6kh3 must drop the single lowest die.
        rng = random.Random(99)
        r = dt.roll_dice("4d6kh3", rng=rng)
        term = r["breakdown"][0]
        self.assertEqual(len(term["rolls"]), 4)
        self.assertEqual(len(term["kept"]), 3)
        self.assertEqual(sorted(term["kept"]), sorted(sorted(term["rolls"])[1:]))

    def test_advantage_picks_higher(self):
        # With a fixed seed, advantage total >= disadvantage total for same seed.
        adv = dt.roll_dice("1d20", advantage=1, rng=random.Random(5))
        dis = dt.roll_dice("1d20", advantage=-1, rng=random.Random(5))
        self.assertGreaterEqual(adv["total"], dis["total"])
        self.assertEqual(adv["total"], max(adv["both_totals"]))
        self.assertEqual(dis["total"], min(dis["both_totals"]))

    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            dt.roll_dice("abc", rng=random.Random(1))


class CheckTests(unittest.TestCase):
    def test_success_and_margin(self):
        # Force natural via seed-independent path: use die '1d1' so natural==1.
        r = dt.roll_check(modifier=14, dc=15, die="1d1")
        self.assertEqual(r["natural"], 1)
        self.assertEqual(r["total"], 15)
        self.assertTrue(r["success"])
        self.assertEqual(r["margin"], 0)

    def test_critical_flags(self):
        crit = dt.roll_check(modifier=0, dc=10, die="1d1", crit_high=1)
        self.assertTrue(crit["critical_success"])   # natural 1 == crit_high 1
        fail = dt.roll_check(modifier=0, dc=10, die="1d1")  # natural 1 == crit_low
        self.assertTrue(fail["critical_failure"])

    def test_non_d20_die(self):
        r = dt.roll_check(modifier=2, dc=8, die="1d6", rng=random.Random(1))
        self.assertEqual(r["die"], "1d6")
        self.assertIn("success", r)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def eng(self):
        return dt.DMEngine(self.tmp)

    def test_save_load_roundtrip(self):
        e = self.eng()
        e.var_set("quest_stage", 3)
        e.character_set("Aria", {"max_hp": 24, "hp": 24, "ac": 15})
        e.save()
        e2 = self.eng()
        self.assertEqual(e2.var_get("quest_stage")["value"], 3)
        self.assertEqual(e2.character_get("Aria")["ac"], 15)

    def test_damage_temp_hp_then_hp(self):
        e = self.eng()
        e.character_set("Aria", {"max_hp": 20, "hp": 20, "temp_hp": 5})
        res = e.apply_damage("Aria", 8)  # 5 temp absorbed, 3 to hp
        self.assertEqual(res["temp_hp"], 0)
        self.assertEqual(res["hp"], 17)
        self.assertFalse(res["down"])

    def test_damage_marks_down(self):
        e = self.eng()
        e.character_set("Goblin", {"max_hp": 7, "hp": 7})
        res = e.apply_damage("Goblin", 10)
        self.assertLessEqual(res["hp"], 0)
        self.assertTrue(res["down"])

    def test_heal_capped_at_max(self):
        e = self.eng()
        e.character_set("Aria", {"max_hp": 20, "hp": 5})
        res = e.heal("Aria", 100)
        self.assertEqual(res["hp"], 20)

    def test_conditions(self):
        e = self.eng()
        e.character_set("Aria", {"max_hp": 10, "hp": 10})
        e.condition_add("Aria", "poisoned")
        e.condition_add("Aria", "poisoned")  # idempotent
        self.assertEqual(e.character_get("Aria")["conditions"], ["poisoned"])
        e.condition_clear("Aria", "poisoned")
        self.assertEqual(e.character_get("Aria")["conditions"], [])

    def test_inventory(self):
        e = self.eng()
        e.inventory("Aria", "add", "torch", qty=2)
        e.inventory("Aria", "add", "torch", qty=1)
        inv = e.inventory("Aria", "list")["inventory"]
        self.assertEqual(inv, [{"item": "torch", "qty": 3}])
        e.inventory("Aria", "remove", "torch", qty=3)
        self.assertEqual(e.inventory("Aria", "list")["inventory"], [])

    def test_initiative_order_desc(self):
        e = self.eng()
        e.encounter_start("Ambush")
        e.combatant_add("Slow", initiative=5)
        e.combatant_add("Fast", initiative=20)
        e.combatant_add("Mid", initiative=12)
        order = [c["name"] for c in e.combat["combatants"]]
        self.assertEqual(order, ["Fast", "Mid", "Slow"])

    def test_turn_cycle_increments_round(self):
        e = self.eng()
        e.encounter_start("Fight")
        e.combatant_add("A", initiative=20)
        e.combatant_add("B", initiative=10)
        t1 = e.turn_next()
        self.assertEqual((t1["round"], t1["current"]["name"]), (1, "A"))
        t2 = e.turn_next()
        self.assertEqual((t2["round"], t2["current"]["name"]), (1, "B"))
        t3 = e.turn_next()  # wraps -> round 2
        self.assertEqual((t3["round"], t3["current"]["name"]), (2, "A"))

    def test_damage_syncs_combatant_and_sheet(self):
        e = self.eng()
        e.character_set("Goblin", {"max_hp": 7, "hp": 7})
        e.encounter_start("Fight")
        e.combatant_add("Goblin", initiative=10, hp=7)
        e.apply_damage("Goblin", 4)
        self.assertEqual(e.character_get("Goblin")["hp"], 3)
        self.assertEqual(e._find_combatant("Goblin")["hp"], 3)

    def test_table_roll_in_bounds(self):
        e = self.eng()
        entries = ["a", "b", "c", "d"]
        for _ in range(50):
            res = e.table_roll("loot", entries=entries, rng=random.Random())
            self.assertIn(res["result"], entries)
            self.assertTrue(1 <= res["roll"] <= 4)

    def test_table_requires_definition(self):
        e = self.eng()
        with self.assertRaises(KeyError):
            e.table_roll("unknown")


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_roll_via_cli(self):
        code = dt.main(["--campaign", self.tmp, "--seed", "1", "roll", "2d6+3"])
        self.assertEqual(code, 0)

    def test_error_returns_nonzero(self):
        code = dt.main(["--campaign", self.tmp, "character-get", "Nobody"])
        self.assertEqual(code, 1)

    def test_full_flow_persists(self):
        base = ["--campaign", self.tmp]
        dt.main(base + ["character-set", "Aria", "max_hp=24", "hp=24", "ac=15"])
        dt.main(base + ["encounter-start", "Ambush"])
        dt.main(base + ["combatant-add", "Aria", "--initiative", "18", "--hp", "24"])
        dt.main(base + ["damage", "Aria", "6"])
        e = dt.DMEngine(self.tmp)
        self.assertEqual(e.character_get("Aria")["hp"], 18)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "campaign.json")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
