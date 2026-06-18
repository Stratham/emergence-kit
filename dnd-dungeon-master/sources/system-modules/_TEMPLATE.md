# System Module: <YOUR SYSTEM NAME>

A **system module** is a pre-filled `RULESET_ADAPTER.md` for one game system,
plus any reference the DM needs to run it. Copy this file, complete every field,
and append it under the DM system prompt. The deterministic tools don't change —
only these values do — which is how the kit supports *any* ruleset the player
picks.

Keep it concise: the DM needs decision rules, not a full rulebook. Do **not**
paste copyrighted rulebook text; summarize mechanics in your own words, or use a
system whose reference is openly licensed (see `5e-srd.md`).

---

## Adapter

```
SYSTEM NAME: __________________________________

RESOLUTION DIE: ____            (e.g. 1d20, 2d6, 1d100)
CHECK FORMULA: RESOLUTION DIE + modifier vs DC
  → roll_check(modifier=<mod>, dc=<target>, die="<RESOLUTION DIE>")

DIFFICULTY LADDER:
  trivial ___  easy ___  medium ___  hard ___  very hard ___  near-impossible ___

SUCCESS RULE: total >= DC
DEGREES OF SUCCESS: ____________________________
CRITICALS: natural high ___ → ____ ; natural low ___ → ____
ADVANTAGE/DISADVANTAGE: yes/no  (advantage = 1 / -1)

ABILITY/STAT KEYS: ____________________________
SKILL LIST (optional): ________________________

HIT POINTS: ____________________________
0 HP MEANS: ____________________________
DEFENSE VALUE (attack DC): ____________________________
DAMAGE: ____________________________  (roll_dice notation per weapon/effect)
HEALING / REST: ____________________________

INITIATIVE: ____________________________  (init_mod for combatant_add)
TURN STRUCTURE: ____________________________

CONDITIONS: ____________________________

ADVANCEMENT: ____________________________

NOTABLE SUBSYSTEMS: ____________________________
```

## Quick reference (optional)
Short notes the DM should keep handy: common DCs, signature mechanics, tone, etc.

## Attribution
If this system's reference is licensed, cite it here.
