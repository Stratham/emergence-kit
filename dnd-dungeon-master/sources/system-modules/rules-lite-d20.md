# System Module: Rules-Lite d20

A minimal, original system you can learn in two minutes. No licensing concerns,
almost no prep, great for one-shots, solo play, or newcomers. One die, three
numbers per character.

---

## Adapter

```
SYSTEM NAME: Rules-Lite d20

RESOLUTION DIE: 1d20
CHECK FORMULA: 1d20 + relevant ability vs DC
  → roll_check(modifier=<ability>, dc=<target>, die="1d20")

DIFFICULTY LADDER:
  easy 8   medium 12   hard 16   very hard 20   heroic 25

SUCCESS RULE: total >= DC succeeds
DEGREES OF SUCCESS:
  beat DC by 10+  → critical success (extra benefit)
  meet/beat DC    → success
  miss by 1-4     → success at a cost (complication / resource spent)
  miss by 5+      → failure (situation worsens)
CRITICALS: natural 20 → always succeed with flair; natural 1 → always fail badly
ADVANTAGE/DISADVANTAGE: yes (advantage = 1 / -1)

ABILITY/STAT KEYS: brawn, agility, wits, charm
  Assign +3, +2, +1, +0 across the four at character creation. Raise one (max +5)
  on advancement.
SKILLS: none — describe the approach; the DM picks the fitting ability.

HIT POINTS: max_hp = 10 + brawn. Track current/max.
0 HP MEANS: out of the fight — dying. roll_check(modifier=brawn, dc=10) at the
            start of each of your turns; success = stabilize at 1 HP, failure =
            you die. Any healing while dying stops the clock.
DEFENSE VALUE (attack DC): Defense = 10 + agility. An attack must meet/beat it.
DAMAGE: light weapon 1d6, heavy weapon 1d10, unarmed 1d4 (+ brawn on melee).
        roll_dice("1d6+2"); critical hit → roll the damage dice twice.
HEALING / REST: a short breather (10 min) heals 1d6+brawn once per scene;
                a full rest restores all HP.

INITIATIVE: 1d20 + agility  → combatant_add ... --init-mod <agility>
TURN STRUCTURE: on your turn, move and take one action (attack, cast/use, help,
                disengage, or something clever). One reaction between turns.

CONDITIONS: prone, grappled, frightened, poisoned, dazed, hidden, bleeding
  (DM rules effects on the fly; e.g. dazed = disadvantage on your next roll)

ADVANCEMENT: milestone. On level up, +1 to one ability (max +5) and +5 max HP.

NOTABLE SUBSYSTEMS:
  Magic — a caster picks one ability as their casting stat; spells are improvised
    effects resolved as checks (attack vs Defense, or a save the target rolls).
  Effort points (optional) — start each session with 3; spend 1 to reroll any
    one die. Track with var_set effort_<name>.
```

## Character creation (60 seconds)
1. Name and concept.
2. Assign +3 / +2 / +1 / +0 to **brawn, agility, wits, charm**.
3. `max_hp = 10 + brawn`; `Defense = 10 + agility`.
4. Pick a weapon and a few items.

`character_set` example:
```
character_set Vex fields={"max_hp":12,"hp":12,"ac":13,
  "stats":{"brawn":2,"agility":3,"wits":1,"charm":0}}
inventory Vex add "light blade"
```
(Here AC stores Defense = 10 + agility = 13.)

## Quick play notes
- Default DC is **12 (medium)**. Set it by fictional difficulty, then roll.
- Attacks: `roll_check(modifier=brawn or agility, dc=target_Defense)`; on a hit,
  `roll_dice("<weapon>")` then `apply_damage`.
- When unsure, ask "how hard is this?", pick a ladder DC, and roll.

## Attribution
Original content for this kit; free to use, modify, and share.
