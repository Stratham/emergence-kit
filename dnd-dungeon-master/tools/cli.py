#!/usr/bin/env python3
"""
cli.py — Human-friendly front end for the DM engine.

For the "paste-into-ChatGPT" and solo-play paths: when GPT asks for a roll or a
state change, you run it here and paste the readable one-liner back into the chat.
It reuses dm_tools.DMEngine — no game logic lives here, only presentation.

Interactive:   python3 cli.py
One-shot:      python3 cli.py roll 2d6+3
               python3 cli.py check 5 15            # modifier 15? no: modifier DC
               python3 cli.py dmg Goblin 6

Type 'help' inside the REPL for the command list.
"""

import shlex
import sys
from typing import List

import dm_tools as dt

HELP = """\
commands (everything persists to the campaign):
  roll <notation> [adv|dis]        roll dice, e.g. roll 2d6+3 / roll 1d20 adv
  check <mod> <dc> [adv|dis]       resolve a check vs a DC
  enc <name>                       start an encounter
  end                              end the encounter
  join <name> [init] [hp] [ac]     add a combatant (omit init to auto-roll)
  next                             advance to the next turn
  status                           show the initiative tracker
  dmg <name> <amount>              apply damage
  heal <name> <amount>             restore HP
  cond <name> <condition>          add a condition
  uncond <name> <condition>        remove a condition
  sheet <name> key=value ...       set/update sheet fields
  show <name>                      show a character sheet
  inv <name> add|remove|list [item] [qty]
  set <key> <value>                set a campaign variable
  get <key>                        read a campaign variable
  table <name> [a;b;c]             roll on a (named) random table
  help / quit
"""


def _adv(tokens: List[str]) -> int:
    if "adv" in tokens:
        return 1
    if "dis" in tokens:
        return -1
    return 0


def run(eng: dt.DMEngine, tokens: List[str]) -> str:
    if not tokens:
        return ""
    cmd, args = tokens[0].lower(), tokens[1:]

    if cmd == "roll":
        r = dt.roll_dice(args[0], advantage=_adv(args))
        rolls = ", ".join(str(p.get("rolls") or p.get("modifier")) for p in r["breakdown"])
        return f"🎲 {args[0]} = {r['total']}  [{rolls}]"

    if cmd == "check":
        r = dt.roll_check(modifier=int(args[0]),
                          dc=int(args[1]) if len(args) > 1 and args[1].lstrip("-").isdigit() else None,
                          advantage=_adv(args))
        line = f"🎯 d20({r['natural']}) {r['modifier']:+d} = {r['total']}"
        if "success" in r:
            line += f" vs DC {r['dc']} → {'SUCCESS' if r['success'] else 'FAILURE'} (margin {r['margin']:+d})"
        if r["critical_success"]:
            line += "  ✦ CRITICAL!"
        if r["critical_failure"]:
            line += "  ✗ critical fail"
        return line

    if cmd == "enc":
        eng.encounter_start(" ".join(args)); eng.save()
        return f"⚔️  Encounter started: {' '.join(args)}"
    if cmd == "end":
        eng.encounter_end(); eng.save()
        return "🕊️  Encounter ended."
    if cmd == "join":
        name = args[0]
        init = int(args[1]) if len(args) > 1 else None
        hp = int(args[2]) if len(args) > 2 else None
        ac = int(args[3]) if len(args) > 3 else None
        res = eng.combatant_add(name, initiative=init, hp=hp, ac=ac); eng.save()
        return f"➕ {name} joins (init {res['combatant']['initiative']}). Order: {', '.join(res['order'])}"
    if cmd == "next":
        t = eng.turn_next(); eng.save()
        return f"▶️  Round {t['round']} — {t['current']['name']}'s turn"
    if cmd == "status":
        c = eng.combat_status()
        if not c.get("active"):
            return "No active encounter."
        lines = [f"⚔️  {c['name']} — round {c['round']}"]
        for i, m in enumerate(c["combatants"]):
            mark = "→" if i == c["turn_index"] and c["round"] else " "
            cond = f" [{', '.join(m['conditions'])}]" if m.get("conditions") else ""
            lines.append(f" {mark} {m['name']}: init {m['initiative']}, hp {m.get('hp')}{cond}")
        return "\n".join(lines)

    if cmd == "dmg":
        r = eng.apply_damage(args[0], int(args[1])); eng.save()
        down = "  💀 DOWN" if r["down"] else ""
        return f"💥 {args[0]} takes {args[1]} → {r['hp']} HP{down}"
    if cmd == "heal":
        r = eng.heal(args[0], int(args[1])); eng.save()
        return f"💚 {args[0]} heals {args[1]} → {r['hp']} HP"
    if cmd == "cond":
        r = eng.condition_add(args[0], args[1]); eng.save()
        return f"🌀 {args[0]} is now: {', '.join(r['conditions'])}"
    if cmd == "uncond":
        r = eng.condition_clear(args[0], args[1]); eng.save()
        return f"✨ {args[0]} conditions: {', '.join(r['conditions']) or 'none'}"

    if cmd == "sheet":
        fields = {}
        for pair in args[1:]:
            k, v = pair.split("=", 1)
            fields[k] = dt._coerce(v)
        eng.character_set(args[0], fields); eng.save()
        return f"📝 {args[0]} updated: {', '.join(fields)}"
    if cmd == "show":
        s = eng.character_get(args[0])
        return (f"📝 {s['name']}: HP {s.get('hp')}/{s.get('max_hp')} "
                f"(temp {s.get('temp_hp', 0)}), AC {s.get('ac')}, "
                f"conditions {s.get('conditions') or 'none'}, "
                f"items {[i['item'] for i in s.get('inventory', [])] or 'none'}")
    if cmd == "inv":
        action = args[1]
        item = args[2] if len(args) > 2 else None
        qty = int(args[3]) if len(args) > 3 else 1
        r = eng.inventory(args[0], action, item, qty); eng.save()
        return f"🎒 {args[0]}: " + ", ".join(f"{i['qty']}x {i['item']}" for i in r["inventory"]) or "(empty)"

    if cmd == "set":
        eng.var_set(args[0], dt._coerce(args[1])); eng.save()
        return f"🔧 {args[0]} = {args[1]}"
    if cmd == "get":
        return f"🔧 {args[0]} = {eng.var_get(args[0])['value']}"
    if cmd == "table":
        entries = args[1].split(";") if len(args) > 1 else None
        r = eng.table_roll(args[0], entries=entries); eng.save()
        return f"📜 {args[0]} ({r['roll']}/{r['size']}) → {r['result']}"

    if cmd in ("help", "?"):
        return HELP
    return f"unknown command: {cmd} (type 'help')"


def main() -> int:
    import os
    eng = dt.DMEngine(os.environ.get("DM_CAMPAIGN_DIR", "campaign_state"))
    if len(sys.argv) > 1:  # one-shot
        try:
            print(run(eng, sys.argv[1:]))
        except (KeyError, ValueError, IndexError) as e:
            print(f"error: {e}"); return 1
        return 0
    print("DM tools CLI — type 'help', 'quit' to exit.")
    while True:
        try:
            line = input("dm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if line in ("quit", "exit"):
            break
        if not line:
            continue
        try:
            print(run(eng, shlex.split(line)))
        except (KeyError, ValueError, IndexError) as e:
            print(f"error: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
