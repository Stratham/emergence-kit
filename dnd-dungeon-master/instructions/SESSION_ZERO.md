# Session Zero — onboarding the table

Session Zero happens once, before play. It sets expectations and produces the
inputs the DM needs: the **ruleset**, the **tone/safety agreement**, and the
**party**. The DM should walk the player(s) through this conversationally and
record the outcomes with the tools (`var_set`) and a filled `RULESET_ADAPTER.md`.

## 1. Choose the ruleset (player decides)

Ask the player which system they want to play. Options shipped with this kit:

- **5e SRD** (`sources/system-modules/5e-srd.md`) — familiar d20 fantasy, ability
  checks vs DCs, the CC-licensed core of the world's most popular RPG.
- **Rules-Lite d20** (`sources/system-modules/rules-lite-d20.md`) — a minimal
  original system; fast to learn, no prep.
- **Any other system** — copy `sources/system-modules/_TEMPLATE.md`, fill in the
  dice convention, stats, check resolution, and combat shape, and use that.

Load the chosen module's text into the conversation (append it under the system
prompt) and record it: `var_set system "<module-name>"`.

## 2. Agree on tone and safety

Establish and record (`var_set tone ...`, `var_set safety_word ...`):

- **Genre & tone** — heroic, gritty, horror, comedic, mystery, etc.
- **Lines** (never appear in the game) and **veils** (happen off-screen / fade to
  black). Ask explicitly; respect them for the whole campaign.
- **Safety word** — a word any player can say to pause, rewind, or skip a scene,
  no questions asked.
- **Spotlight & pace** — solo play, or a party; combat-heavy vs roleplay-heavy.

## 3. Build the party

For each player character, create a sheet with `character_set`, using the stat
keys defined by the chosen system module. Minimum useful fields:

- `name`
- `max_hp` and `hp` (start equal)
- `ac` (or the system's defense value)
- `stats` — ability scores / skill modifiers per the module
- starting `inventory` (via the `inventory` tool)

Example (5e-style):
```
character_set  name=Aria  fields={"max_hp":24,"hp":24,"ac":15,"level":3,
   "stats":{"str":1,"dex":3,"con":2,"int":0,"wis":2,"cha":1,"perception":5}}
inventory      Aria add "shortbow"
inventory      Aria add "torch" --qty 5
```

## 4. Establish the opening

Set the starting situation and a hook: where the characters are, why they're
together, and the immediate problem. Record campaign facts with `var_set`
(e.g. `quest_stage`, `day`, `location`). Then begin play with the DM system
prompt's narration style.

## Quick checklist
- [ ] System module chosen and loaded; `system` recorded
- [ ] Tone, lines/veils, and safety word agreed and recorded
- [ ] Each character sheet created (HP, AC, stats, inventory)
- [ ] Opening scene and hook set; campaign vars initialized
