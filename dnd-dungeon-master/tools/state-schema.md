# State schema

`dm_tools.py` persists each campaign as three JSON files inside a campaign
directory (default `./campaign_state`, override with `--campaign` or the
`DM_CAMPAIGN_DIR` environment variable). Everything mechanical lives here, so a
campaign can be paused, version-controlled, backed up, or resumed at any time.

## `campaign.json`
```json
{
  "name": "The Sunken Crown",
  "system": "5e-srd",
  "vars": { "quest_stage": 2, "town_reputation": 5, "day": 4 },
  "tables": { "wild_magic": ["Fireball", "Teleport", "Frog rain"] },
  "log": ["encounter started: Goblin Ambush", "Goblin took 6 damage -> 1 HP"]
}
```
- **vars** — arbitrary persistent world/plot state set via `var_set`/`var_get`.
- **tables** — named random tables; once defined they can be re-rolled by name.
- **log** — append-only audit trail of every mechanical event (useful for recaps).

## `characters.json`
Keyed by character name. Created/updated by `character_set`; HP touched by
`apply_damage`/`heal`; conditions and inventory by their respective tools.
```json
{
  "Aria": {
    "name": "Aria",
    "max_hp": 24, "hp": 18, "temp_hp": 0,
    "ac": 15, "down": false,
    "conditions": ["poisoned"],
    "inventory": [{ "item": "torch", "qty": 3 }],
    "stats": { "str": 1, "dex": 3, "perception": 5 }
  }
}
```
- **stats** is free-form: store ability scores, skill modifiers, or whatever the
  chosen ruleset uses. The engine never assumes specific keys.
- **down** is set true when `hp <= 0`.

## `combat.json`
Managed by the encounter/turn tools. Combatants are kept sorted by initiative
(descending). Damage/conditions applied by name sync between here and
`characters.json` when a name matches a known character.
```json
{
  "active": true,
  "name": "Goblin Ambush",
  "round": 1,
  "turn_index": 0,
  "combatants": [
    { "name": "Aria", "initiative": 18, "hp": 24, "max_hp": 24, "temp_hp": 0, "ac": 15, "conditions": [] },
    { "name": "Goblin", "initiative": 12, "hp": 1, "max_hp": 7, "temp_hp": 0, "ac": 13, "conditions": [] }
  ]
}
```

## Design guarantees
- **Authoritative state** — the model reads these values; it never invents HP,
  initiative, or dice outcomes.
- **System-agnostic** — no field hardcodes a ruleset; numbers come from the
  chosen system module and from tool arguments.
- **Portable** — stdlib JSON only; copy the directory to move a campaign.
