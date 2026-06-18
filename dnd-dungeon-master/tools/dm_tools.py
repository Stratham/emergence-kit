#!/usr/bin/env python3
"""
dm_tools.py — Deterministic game-mechanics engine for the GPT Dungeon Master Kit.

Philosophy: the language model narrates and judges; THIS code owns everything
mechanical — dice, initiative, HP, conditions, inventory, variables, and random
tables — so game state is authoritative and never hallucinated.

- Pure Python standard library only (runs anywhere with Python 3.8+).
- System-agnostic: all numbers (stats, dice, DCs) are arguments, never hardcoded,
  so the same engine serves any ruleset the player chooses.
- State persists to plain JSON files in a campaign directory, so play survives
  across sessions and across GPT context limits.

Usage (CLI mirrors the subcommand style of emergence-kit's my_brain.py):

    python3 dm_tools.py roll "2d6+3"
    python3 dm_tools.py check --modifier 5 --dc 15 --advantage
    python3 dm_tools.py encounter-start "Goblin Ambush"
    python3 dm_tools.py combatant-add Aria --init-mod 2 --hp 24 --ac 15
    python3 dm_tools.py combatant-add Goblin --initiative 12 --hp 7 --ac 13
    python3 dm_tools.py turn-next
    python3 dm_tools.py damage Goblin 6
    python3 dm_tools.py condition-add Aria poisoned
    python3 dm_tools.py var-set quest_stage 2
    python3 dm_tools.py table-roll wild_magic --entries "Fireball;Teleport;Frog rain"

Every command prints a JSON result on stdout (easy for an LLM/agent to parse) and
auto-saves state to the campaign directory (default: ./campaign_state, override
with --campaign / the DM_CAMPAIGN_DIR environment variable).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Dice                                                                        #
# --------------------------------------------------------------------------- #

# A signed term inside a dice expression, e.g. "2d6", "-1d4kh1", "+3".
_TERM_RE = re.compile(r"(?P<sign>[+-]?)(?P<count>\d*)d(?P<faces>\d+)"
                      r"(?:(?P<keep>kh|kl)(?P<keepn>\d+))?", re.IGNORECASE)
_CONST_RE = re.compile(r"(?P<sign>[+-]?)(?P<value>\d+)")


def _split_terms(expr: str) -> List[str]:
    """Split '2d6+3-1d4' into ['2d6', '+3', '-1d4'] (signs attached)."""
    expr = expr.replace(" ", "")
    if not expr:
        raise ValueError("empty dice expression")
    return re.findall(r"[+-]?[^+-]+", expr)


def _eval_expression(expr: str, rng: random.Random) -> Tuple[int, List[Dict[str, Any]]]:
    """Evaluate a dice expression once. Returns (total, per-term breakdown)."""
    total = 0
    breakdown: List[Dict[str, Any]] = []
    for token in _split_terms(expr):
        sign = -1 if token.startswith("-") else 1
        body = token.lstrip("+-")
        m = _TERM_RE.fullmatch(body)
        if m:
            count = int(m.group("count") or 1)
            faces = int(m.group("faces"))
            if count < 1 or faces < 1:
                raise ValueError(f"invalid dice term: {token!r}")
            rolls = [rng.randint(1, faces) for _ in range(count)]
            kept = rolls
            keep = m.group("keep")
            if keep:
                keepn = int(m.group("keepn"))
                kept = sorted(rolls, reverse=keep.lower() == "kh")[:keepn]
            subtotal = sign * sum(kept)
            total += subtotal
            breakdown.append({
                "term": token, "rolls": rolls, "kept": kept, "subtotal": subtotal,
            })
            continue
        c = _CONST_RE.fullmatch(body)
        if c:
            value = sign * int(c.group("value"))
            total += value
            breakdown.append({"term": token, "modifier": value})
            continue
        raise ValueError(f"could not parse dice term: {token!r}")
    return total, breakdown


def roll_dice(notation: str, advantage: int = 0,
              rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Roll a dice expression like '2d6+3'.

    advantage: 0 normal, 1 advantage (roll twice keep higher total),
               -1 disadvantage (roll twice keep lower total).
    Keep-highest/lowest within a die is supported via notation, e.g. '4d6kh3'.
    """
    rng = rng or random
    if advantage == 0:
        total, breakdown = _eval_expression(notation, rng)
        return {"notation": notation, "total": total, "breakdown": breakdown,
                "advantage": 0}
    t1, b1 = _eval_expression(notation, rng)
    t2, b2 = _eval_expression(notation, rng)
    chosen = max((t1, b1), (t2, b2)) if advantage > 0 else min((t1, b1), (t2, b2))
    return {
        "notation": notation, "advantage": advantage,
        "total": chosen[0], "breakdown": chosen[1],
        "both_totals": [t1, t2],
    }


def roll_check(modifier: int = 0, dc: Optional[int] = None, advantage: int = 0,
               die: str = "1d20", crit_high: Optional[int] = None,
               crit_low: int = 1, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Resolve a d20-style check/save/attack against a difficulty class.

    Returns the natural die, the modified total, success/failure vs dc, and
    critical flags. `die` defaults to 1d20 but any single-die notation works,
    so non-d20 systems are supported. crit_high defaults to the die's max face.
    """
    rng = rng or random
    base = roll_dice(die, advantage=advantage, rng=rng)
    # The natural roll = sum of kept dice on the chosen evaluation (no modifier).
    natural = sum(part["subtotal"] for part in base["breakdown"] if "subtotal" in part)
    faces_match = re.search(r"d(\d+)", die)
    faces = int(faces_match.group(1)) if faces_match else 20
    if crit_high is None:
        crit_high = faces
    total = natural + modifier
    result: Dict[str, Any] = {
        "die": die, "natural": natural, "modifier": modifier, "total": total,
        "advantage": advantage,
        "critical_success": natural >= crit_high,
        "critical_failure": natural <= crit_low,
    }
    if dc is not None:
        result["dc"] = dc
        result["success"] = total >= dc
        result["margin"] = total - dc
    return result


# --------------------------------------------------------------------------- #
# Persistent state                                                            #
# --------------------------------------------------------------------------- #

DEFAULT_CAMPAIGN = os.environ.get("DM_CAMPAIGN_DIR", "campaign_state")


class DMEngine:
    """Loads/saves campaign, character, and combat state from a directory."""

    def __init__(self, campaign_dir: str = DEFAULT_CAMPAIGN):
        self.dir = campaign_dir
        self.campaign = self._load("campaign.json", {
            "name": "Untitled Campaign", "system": None, "vars": {},
            "tables": {}, "log": [],
        })
        self.characters = self._load("characters.json", {})
        self.combat = self._load("combat.json", {
            "active": False, "name": None, "round": 0, "turn_index": 0,
            "combatants": [],
        })

    # -- io ----------------------------------------------------------------- #
    def _path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def _load(self, name: str, default: Any) -> Any:
        try:
            with open(self._path(name), encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def save(self) -> None:
        os.makedirs(self.dir, exist_ok=True)
        for name, data in (("campaign.json", self.campaign),
                           ("characters.json", self.characters),
                           ("combat.json", self.combat)):
            with open(self._path(name), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def log(self, event: str) -> None:
        self.campaign.setdefault("log", []).append(event)

    # -- helpers ------------------------------------------------------------ #
    def _find_char(self, name: str) -> Optional[str]:
        """Resolve a character/combatant by case-insensitive name; return key."""
        for key in self.characters:
            if key.lower() == name.lower():
                return key
        return None

    def _find_combatant(self, name: str) -> Optional[Dict[str, Any]]:
        for c in self.combat["combatants"]:
            if c["name"].lower() == name.lower():
                return c
        return None

    # -- characters --------------------------------------------------------- #
    def character_set(self, name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        key = self._find_char(name) or name
        sheet = self.characters.setdefault(key, {
            "name": name, "hp": None, "max_hp": None, "temp_hp": 0,
            "conditions": [], "inventory": [], "stats": {},
        })
        for k, v in fields.items():
            if k == "stats" and isinstance(v, dict):
                sheet.setdefault("stats", {}).update(v)
            else:
                sheet[k] = v
        self.log(f"updated sheet for {name}: {', '.join(fields)}")
        return sheet

    def character_get(self, name: str) -> Dict[str, Any]:
        key = self._find_char(name)
        if key is None:
            raise KeyError(f"no character named {name!r}")
        return self.characters[key]

    def _apply_hp(self, name: str, delta: int) -> Dict[str, Any]:
        """Apply HP change to a character sheet AND its combatant entry if any."""
        targets: List[Dict[str, Any]] = []
        key = self._find_char(name)
        if key is not None:
            targets.append(self.characters[key])
        comb = self._find_combatant(name)
        if comb is not None:
            targets.append(comb)
        if not targets:
            raise KeyError(f"no character or combatant named {name!r}")
        result = None
        for sheet in targets:
            hp = sheet.get("hp")
            if hp is None:
                hp = sheet.get("max_hp") or 0
            temp = sheet.get("temp_hp", 0) or 0
            remaining = delta
            if delta < 0 and temp > 0:  # damage absorbed by temp HP first
                absorbed = min(temp, -delta)
                temp -= absorbed
                remaining = delta + absorbed
                sheet["temp_hp"] = temp
            hp += remaining
            max_hp = sheet.get("max_hp")
            if max_hp is not None:
                hp = min(hp, max_hp)
            sheet["hp"] = hp
            down = hp <= 0
            sheet["down"] = down
            result = {"name": sheet.get("name", name), "hp": hp,
                      "temp_hp": sheet.get("temp_hp", 0), "max_hp": max_hp,
                      "down": down}
        return result

    def apply_damage(self, name: str, amount: int) -> Dict[str, Any]:
        if amount < 0:
            raise ValueError("damage amount must be non-negative")
        res = self._apply_hp(name, -amount)
        self.log(f"{name} took {amount} damage -> {res['hp']} HP")
        return res

    def heal(self, name: str, amount: int) -> Dict[str, Any]:
        if amount < 0:
            raise ValueError("heal amount must be non-negative")
        res = self._apply_hp(name, amount)
        self.log(f"{name} healed {amount} -> {res['hp']} HP")
        return res

    def condition_add(self, name: str, condition: str) -> Dict[str, Any]:
        sheet = self.character_set(name, {})
        conds = sheet.setdefault("conditions", [])
        if condition not in conds:
            conds.append(condition)
        comb = self._find_combatant(name)
        if comb is not None:
            cc = comb.setdefault("conditions", [])
            if condition not in cc:
                cc.append(condition)
        self.log(f"{name} gained condition: {condition}")
        return {"name": name, "conditions": conds}

    def condition_clear(self, name: str, condition: str) -> Dict[str, Any]:
        sheet = self.character_get(name)
        sheet["conditions"] = [c for c in sheet.get("conditions", []) if c != condition]
        comb = self._find_combatant(name)
        if comb is not None:
            comb["conditions"] = [c for c in comb.get("conditions", []) if c != condition]
        self.log(f"{name} lost condition: {condition}")
        return {"name": name, "conditions": sheet["conditions"]}

    # -- inventory ---------------------------------------------------------- #
    def inventory(self, name: str, action: str, item: Optional[str] = None,
                  qty: int = 1) -> Dict[str, Any]:
        sheet = self.character_set(name, {})
        inv: List[Dict[str, Any]] = sheet.setdefault("inventory", [])
        if action == "list":
            return {"name": name, "inventory": inv}
        if item is None:
            raise ValueError("item required for add/remove")
        existing = next((i for i in inv if i["item"].lower() == item.lower()), None)
        if action == "add":
            if existing:
                existing["qty"] += qty
            else:
                inv.append({"item": item, "qty": qty})
            self.log(f"{name} gained {qty}x {item}")
        elif action == "remove":
            if existing:
                existing["qty"] -= qty
                if existing["qty"] <= 0:
                    inv.remove(existing)
            self.log(f"{name} lost {qty}x {item}")
        else:
            raise ValueError(f"unknown inventory action: {action}")
        return {"name": name, "inventory": inv}

    # -- combat ------------------------------------------------------------- #
    def encounter_start(self, name: str) -> Dict[str, Any]:
        self.combat = {"active": True, "name": name, "round": 0,
                       "turn_index": 0, "combatants": []}
        self.log(f"encounter started: {name}")
        return self.combat

    def encounter_end(self) -> Dict[str, Any]:
        name = self.combat.get("name")
        self.combat = {"active": False, "name": None, "round": 0,
                       "turn_index": 0, "combatants": []}
        self.log(f"encounter ended: {name}")
        return self.combat

    def combatant_add(self, name: str, initiative: Optional[int] = None,
                      init_mod: int = 0, hp: Optional[int] = None,
                      ac: Optional[int] = None,
                      rng: Optional[random.Random] = None) -> Dict[str, Any]:
        rng = rng or random
        roll_info = None
        if initiative is None:
            roll_info = roll_check(modifier=init_mod, rng=rng)
            initiative = roll_info["total"]
        combatant = {"name": name, "initiative": initiative,
                     "hp": hp, "max_hp": hp, "temp_hp": 0, "ac": ac,
                     "conditions": []}
        self.combat["combatants"].append(combatant)
        # Stable sort by initiative desc; ties keep insertion order.
        self.combat["combatants"].sort(key=lambda c: c["initiative"], reverse=True)
        self.log(f"{name} joined combat (init {initiative})")
        return {"combatant": combatant, "initiative_roll": roll_info,
                "order": [c["name"] for c in self.combat["combatants"]]}

    def turn_next(self) -> Dict[str, Any]:
        if not self.combat.get("active") or not self.combat["combatants"]:
            raise ValueError("no active encounter with combatants")
        if self.combat["round"] == 0:
            self.combat["round"] = 1
            self.combat["turn_index"] = 0
        else:
            self.combat["turn_index"] += 1
            if self.combat["turn_index"] >= len(self.combat["combatants"]):
                self.combat["turn_index"] = 0
                self.combat["round"] += 1
        current = self.combat["combatants"][self.combat["turn_index"]]
        self.log(f"round {self.combat['round']}: {current['name']}'s turn")
        return {"round": self.combat["round"],
                "turn_index": self.combat["turn_index"],
                "current": current,
                "order": [c["name"] for c in self.combat["combatants"]]}

    def combat_status(self) -> Dict[str, Any]:
        return self.combat

    # -- variables & tables ------------------------------------------------- #
    def var_set(self, key: str, value: Any) -> Dict[str, Any]:
        self.campaign.setdefault("vars", {})[key] = value
        self.log(f"var {key} = {value}")
        return {"key": key, "value": value}

    def var_get(self, key: str) -> Dict[str, Any]:
        return {"key": key, "value": self.campaign.get("vars", {}).get(key)}

    def table_roll(self, name: str, entries: Optional[List[str]] = None,
                   rng: Optional[random.Random] = None) -> Dict[str, Any]:
        rng = rng or random
        tables = self.campaign.setdefault("tables", {})
        if entries:
            tables[name] = entries  # save/overwrite a named table
        table = tables.get(name)
        if not table:
            raise KeyError(f"no table named {name!r}; pass entries to define it")
        roll = roll_dice(f"1d{len(table)}", rng=rng)
        idx = roll["total"] - 1
        result = table[idx]
        self.log(f"table {name} -> {result}")
        return {"table": name, "roll": roll["total"], "result": result,
                "size": len(table)}


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #

def _emit(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _coerce(value: str) -> Any:
    """Turn a CLI string into int/float/bool/json when it obviously is one."""
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            pass
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic DM game-mechanics engine")
    p.add_argument("--campaign", default=DEFAULT_CAMPAIGN,
                   help="campaign state directory (default: %(default)s)")
    p.add_argument("--seed", type=int, default=None,
                   help="seed the RNG for reproducible rolls (testing)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("roll", help="roll a dice expression e.g. 2d6+3")
    s.add_argument("notation")
    s.add_argument("--advantage", action="store_const", const=1, default=0)
    s.add_argument("--disadvantage", dest="advantage", action="store_const", const=-1)

    s = sub.add_parser("check", help="resolve a check/save/attack vs a DC")
    s.add_argument("--modifier", type=int, default=0)
    s.add_argument("--dc", type=int, default=None)
    s.add_argument("--die", default="1d20")
    s.add_argument("--advantage", action="store_const", const=1, default=0)
    s.add_argument("--disadvantage", dest="advantage", action="store_const", const=-1)

    s = sub.add_parser("encounter-start"); s.add_argument("name")
    sub.add_parser("encounter-end")
    sub.add_parser("combat-status")

    s = sub.add_parser("combatant-add")
    s.add_argument("name")
    s.add_argument("--initiative", type=int, default=None)
    s.add_argument("--init-mod", type=int, default=0)
    s.add_argument("--hp", type=int, default=None)
    s.add_argument("--ac", type=int, default=None)

    sub.add_parser("turn-next")

    s = sub.add_parser("damage"); s.add_argument("name"); s.add_argument("amount", type=int)
    s = sub.add_parser("heal"); s.add_argument("name"); s.add_argument("amount", type=int)
    s = sub.add_parser("condition-add"); s.add_argument("name"); s.add_argument("condition")
    s = sub.add_parser("condition-clear"); s.add_argument("name"); s.add_argument("condition")

    s = sub.add_parser("character-set", help="set/update sheet fields: key=value ...")
    s.add_argument("name"); s.add_argument("fields", nargs="+")

    s = sub.add_parser("character-get"); s.add_argument("name")

    s = sub.add_parser("inventory")
    s.add_argument("name")
    s.add_argument("action", choices=["add", "remove", "list"])
    s.add_argument("item", nargs="?", default=None)
    s.add_argument("--qty", type=int, default=1)

    s = sub.add_parser("var-set"); s.add_argument("key"); s.add_argument("value")
    s = sub.add_parser("var-get"); s.add_argument("key")

    s = sub.add_parser("table-roll")
    s.add_argument("name")
    s.add_argument("--entries", default=None,
                   help="define/overwrite table with ';'-separated entries")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    rng = random.Random(args.seed) if args.seed is not None else random
    eng = DMEngine(args.campaign)
    cmd = args.command

    try:
        if cmd == "roll":
            _emit(roll_dice(args.notation, advantage=args.advantage, rng=rng))
            return 0  # stateless, no save
        if cmd == "check":
            _emit(roll_check(modifier=args.modifier, dc=args.dc, die=args.die,
                             advantage=args.advantage, rng=rng))
            return 0

        if cmd == "encounter-start":
            _emit(eng.encounter_start(args.name))
        elif cmd == "encounter-end":
            _emit(eng.encounter_end())
        elif cmd == "combat-status":
            _emit(eng.combat_status()); return 0
        elif cmd == "combatant-add":
            _emit(eng.combatant_add(args.name, initiative=args.initiative,
                                    init_mod=args.init_mod, hp=args.hp, ac=args.ac,
                                    rng=rng))
        elif cmd == "turn-next":
            _emit(eng.turn_next())
        elif cmd == "damage":
            _emit(eng.apply_damage(args.name, args.amount))
        elif cmd == "heal":
            _emit(eng.heal(args.name, args.amount))
        elif cmd == "condition-add":
            _emit(eng.condition_add(args.name, args.condition))
        elif cmd == "condition-clear":
            _emit(eng.condition_clear(args.name, args.condition))
        elif cmd == "character-set":
            fields: Dict[str, Any] = {}
            for pair in args.fields:
                if "=" not in pair:
                    raise ValueError(f"expected key=value, got {pair!r}")
                k, v = pair.split("=", 1)
                fields[k] = _coerce(v)
            _emit(eng.character_set(args.name, fields))
        elif cmd == "character-get":
            _emit(eng.character_get(args.name)); return 0
        elif cmd == "inventory":
            _emit(eng.inventory(args.name, args.action, args.item, args.qty))
        elif cmd == "var-set":
            _emit(eng.var_set(args.key, _coerce(args.value)))
        elif cmd == "var-get":
            _emit(eng.var_get(args.key)); return 0
        elif cmd == "table-roll":
            entries = args.entries.split(";") if args.entries else None
            _emit(eng.table_roll(args.name, entries=entries, rng=rng))
        else:  # pragma: no cover
            raise ValueError(f"unknown command: {cmd}")
    except (KeyError, ValueError) as exc:
        _emit({"error": str(exc)})
        return 1

    eng.save()
    return 0


if __name__ == "__main__":
    sys.exit(main())
