# Ruleset Adapter

This is the bridge between *any* game system and the deterministic tools. Fill it
in once (or load a ready-made `sources/system-modules/*` file, which is just this
adapter pre-filled) and append it under the DM system prompt. It tells the DM
exactly which dice to call and how to interpret results — which is what makes the
kit system-agnostic and lets the **player choose the ruleset**.

Copy the block below and complete every field.

```
SYSTEM NAME: __________________________________

RESOLUTION DIE: ____   (the die rolled for checks, e.g. 1d20, 2d6, 1d100)
  → maps to the `die` argument of roll_check

CHECK FORMULA: roll RESOLUTION DIE + modifier, compare to a target number
  → call roll_check(modifier=<ability/skill mod>, dc=<target>, die=<RESOLUTION DIE>)

DIFFICULTY LADDER (target numbers / DCs):
  trivial: ___   easy: ___   medium: ___   hard: ___   very hard: ___   near-impossible: ___

SUCCESS RULE: total >= DC means success?  (yes / specify)
DEGREES OF SUCCESS: how margin is read (e.g. beat by 5+ = critical, miss by 5+ = bad)
CRITICALS: natural high = ___ (auto-success / extra effect),  natural low = ___ (auto-fail)
ADVANTAGE/DISADVANTAGE: supported?  (use advantage = 1 / -1 on the roll)

ABILITY / STAT KEYS: ________________________________________
  (the keys stored under a character's `stats`, e.g. str,dex,con,int,wis,cha)
SKILL LIST (optional): ______________________________________

HIT POINTS: how max HP is determined; what 0 HP means (down / dying / dead rule)
DEFENSE VALUE: the stat an attack is compared against (e.g. AC); its `roll_check` DC
DAMAGE: how damage dice are chosen per weapon/effect (feeds roll_dice notation)
HEALING / REST: how HP is restored

INITIATIVE: how it is rolled (the init_mod passed to combatant_add)
TURN STRUCTURE: what a combatant can do on a turn (move/action/etc.)

CONDITIONS: the status conditions this system uses (names you'll pass to condition_add)

ADVANCEMENT: how characters improve (XP / milestone), what changes on level up

NOTABLE SUBSYSTEMS: magic, social, exploration, resources, etc. — brief notes
```

## How the DM uses this
- Every "should I roll?" decision uses the **CHECK FORMULA** + **DIFFICULTY
  LADDER**, executed via `roll_check`.
- Combat uses **DEFENSE VALUE** as the attack DC, **DAMAGE** notation via
  `roll_dice`, **INITIATIVE** via `combatant_add`, and **CONDITIONS** via
  `condition_add`/`condition_clear`.
- Sheets store the **ABILITY/STAT KEYS** under `stats`; the engine treats them as
  opaque numbers, so any system works without code changes.
- Where the adapter is silent, the DM makes a fast, fair ruling and stays
  consistent (record it with `var_set` if it should stick).
