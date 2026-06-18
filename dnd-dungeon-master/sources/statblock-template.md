# Statblock template (system-neutral)

A statblock is just the numbers the tools need to run a creature or NPC in a
scene. Keep it minimal; the engine stores `stats` as opaque numbers, so this
format works for any ruleset — only the values change per system module.

## Format
```
NAME: _______________________
ROLE / THREAT: (minion / standard / elite / boss)  — guides HP and damage
DEFENSE (AC): ____            → combatant_add ... --ac <n>; attack DC = this
HIT POINTS: ____              → combatant_add ... --hp <n>
INITIATIVE MOD: ____          → combatant_add ... --init-mod <n>
SPEED / MOVEMENT: ____        (narrative)
ATTACKS:
  - <name>: to-hit +____ , damage ____ (dice notation, e.g. 1d8+3)
    → roll_check(modifier=+__, dc=<target AC>) then roll_dice("1d8+3"), apply_damage
ABILITIES / STATS: { key: mod, ... }   (per the system module's stat keys)
SKILLS / SAVES (optional): perception +__, ...
CONDITIONS IT CAUSES: (e.g. poisoned on hit)  → condition_add(target, "...")
TRAITS: 1-3 special abilities or behaviors (brief)
TACTICS: how it fights / what it wants  (so the DM plays it well)
```

## Bringing it into a fight
```
encounter_start "Bandit Camp"
combatant_add "Bandit Captain" --hp 30 --ac 15 --init-mod 2
combatant_add "Bandit" --hp 11 --ac 12 --init-mod 1
combatant_add "Bandit" --hp 11 --ac 12 --init-mod 1
turn_next
```
For a recurring NPC, also `character_set` them so HP/conditions persist between
scenes; damage/conditions applied by name sync between the sheet and the fight.

## Example (5e-style standard monster)
```
NAME: Goblin
ROLE: minion
DEFENSE (AC): 15
HIT POINTS: 7
INITIATIVE MOD: +2
ATTACKS:
  - Scimitar: to-hit +4, damage 1d6+2 slashing
  - Shortbow: to-hit +4, damage 1d6+2 piercing
STATS: { str: -1, dex: +2, con: 0, int: 0, wis: -1, cha: -1 }
SKILLS: stealth +6
TRAITS: Nimble Escape (can disengage/hide as a bonus action)
TACTICS: ambush from cover, focus the weakest-looking target, flee if losing.
```
