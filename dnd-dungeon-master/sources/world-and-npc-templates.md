# World & NPC templates

Fill-in scaffolding for prep. Keep entries short — a few evocative lines beat a
novel. Store anything that must persist with `var_set`, and give recurring NPCs a
character sheet (`character_set`) so the tools track their HP/conditions in
scenes.

## Setting brief
```
WORLD/REGION: _______________________
TONE: ____________ (e.g. heroic, grim, weird, comedic)
THE SITUATION: one paragraph on what's happening right now and why it matters
THE HOOK: the immediate problem pulling the party in
TRUTHS: 3 facts that define the place (e.g. "magic is feared", "the king is dying")
```

## Faction
```
NAME: _______________________
WANTS: their goal
METHODS: how they pursue it
ASSET / WEAKNESS: ________ / ________
REPUTATION VAR: var_set faction_<name>_rep <number>   # track standing in play
CLOCK: what they accomplish off-screen if unopposed
```

## NPC card
```
NAME: _______________________
ROLE: (ally / rival / patron / villain / bystander)
WANT: the one thing they're after
FLAW: the thing that trips them up
VOICE: a tic, cadence, or attitude to play them by
LEVERAGE: what they can offer or threaten
SECRET: something they're hiding (reveal through play)
# If they may fight, also make a statblock (see statblock-template.md):
#   character_set <name> fields={"max_hp":..,"hp":..,"ac":..,"stats":{...}}
```

## Location
```
NAME: _______________________
FIRST IMPRESSION: the sensory hit on arrival (sight, sound, smell)
POINTS OF INTEREST: 2-4 things to examine, use, or fear
DANGER / TWIST: what could go wrong here (telegraph it)
EXITS / CONNECTIONS: where it leads
```

## Quest / scenario
```
TITLE: _______________________
GOAL: what success looks like for the party
STAKES: what happens on failure / inaction (tie to a faction clock)
OBSTACLES: 2-3 challenges across exploration / social / combat
REWARD: treasure, allies, information, advancement
STAGE VAR: var_set quest_<id>_stage <number>          # track progress in play
```

## Encounter
```
NAME: _______________________
COMPOSITION: who/what is here (link statblocks)
SITUATION: what they're doing when found; can it be avoided or talked down?
TERRAIN: features that matter (cover, hazards, verticality)
TWIST: a mid-fight change (reinforcements, collapsing floor, hostage)
SETUP: encounter_start -> combatant_add each side -> turn_next
```

## Treasure / random table
```
TABLE NAME: _______________________
ENTRIES: item;item;item;...
# Define and roll in one step:
#   table_roll <name> --entries "Potion of healing;200 gold;A cryptic map;Nothing"
# Re-roll later by name alone.
```
