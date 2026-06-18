<div align="center">

# 🐉 GPT Dungeon Master Kit

**Play D&D-style tabletop RPGs with GPT as your Dungeon Master — with real dice,
real hit points, and a world that remembers.**

*Sources · Tools · Instructions — system-agnostic, runs with any GPT.*

</div>

---

## What this is

A standalone kit for running tabletop roleplaying games where a large language
model is the **Dungeon Master (DM)**. It's built around three pillars:

- **Instructions** — the DM's behavior and system prompt (`instructions/`).
- **Sources** — reference knowledge the DM draws on: GMing procedures, craft, and
  fill-in world/NPC templates (`sources/`).
- **Tools** — a deterministic engine that owns dice, hit points, initiative,
  conditions, inventory, and persistent world state (`tools/`).

The core idea, validated by existing LLM-DM projects: **the model narrates and
judges; code handles the mechanics.** That keeps every roll and HP total *real*
instead of hallucinated, and lets a campaign survive across sessions and context
limits via plain JSON state files.

It is **system-agnostic**: the player chooses the ruleset. Pick a ready-made
system module (5e SRD or a rules-lite original) or describe your own — the tools
never change, only the numbers do.

> Not affiliated with or endorsed by Wizards of the Coast. The 5e module
> paraphrases the CC-BY-licensed SRD (see that file's attribution).

## How it fits together

```
        Instructions (persona)         Sources (knowledge)
        ┌────────────────────┐        ┌──────────────────────┐
        │ DM_SYSTEM_PROMPT    │        │ core-procedures       │
        │ SESSION_ZERO        │        │ dm-craft              │
        │ RULESET_ADAPTER     │  +     │ world/NPC templates   │
        └─────────┬──────────┘        │ system-modules/*  ◄── player picks ruleset
                  │                    └──────────────────────┘
                  ▼
            ┌─────────────┐   calls    ┌──────────────────────────────┐
            │   GPT  (DM) │ ─────────► │ Tools: dm_tools.py (engine)  │
            │            │ ◄───────── │  dice · combat · HP · vars   │
            └─────────────┘  results   │  → campaign_state/*.json     │
                                       └──────────────────────────────┘
```

## Play in your browser (no install)

The fastest way to try it: open **`web/dnd-dm.html`** — a single self-contained
web app where an AI is the DM and the dice/HP/combat panel is real. Add an
OpenAI-compatible API key in ⚙️, pick a ruleset, press **Begin Adventure**. See
[`web/README.md`](web/README.md).

## Quick start (5 minutes)

1. **Pick how the model will reach the tools** and follow that guide:
   - `web/dnd-dm.html` — zero-install browser app; the AI calls the tools for you.
   - `guide/SETUP_CHATGPT.md` — no-code; you run the CLI and paste results back.
   - `guide/SETUP_API.md` — full automation; the model calls the tools itself.
   - `guide/SETUP_MCP.md` — full automation via an MCP server.
2. **Set the persona:** use `instructions/DM_SYSTEM_PROMPT.md` as the system
   prompt, and append a system module from `sources/system-modules/`.
3. **Run Session Zero** (`instructions/SESSION_ZERO.md`): choose the ruleset, agree
   tone & safety, create characters.
4. **Play.** See `guide/EXAMPLE_SESSION.md` for the loop in action.

Try the engine right now:
```
cd tools
python3 dm_tools.py roll "2d6+3"
python3 cli.py            # interactive; type 'help'
python3 test_dm_tools.py # 24 tests, stdlib only
```

## Directory map

```
dnd-dungeon-master/
├── README.md                      ← you are here
├── instructions/                  ← PILLAR: instructions (DM behavior)
│   ├── DM_SYSTEM_PROMPT.md        the master system prompt
│   ├── SESSION_ZERO.md            onboarding: ruleset, tone/safety, party
│   └── RULESET_ADAPTER.md         bridge any game system to the tools
├── sources/                       ← PILLAR: sources (reference knowledge)
│   ├── core-procedures.md         system-neutral adjudication & combat flow
│   ├── dm-craft.md                pacing, improv, NPCs, fail-forward
│   ├── world-and-npc-templates.md fill-in prep scaffolding
│   ├── statblock-template.md      system-neutral creature/NPC format
│   └── system-modules/            the "player picks the ruleset" mechanism
│       ├── _TEMPLATE.md           blank module for any system
│       ├── 5e-srd.md              D&D 5e (SRD, CC-BY) module
│       └── rules-lite-d20.md      minimal original system
├── tools/                         ← PILLAR: tools (deterministic, full automation)
│   ├── dm_tools.py                the engine: dice, combat, HP, vars, save/load
│   ├── tool-schemas.json          function-calling specs (17 tools)
│   ├── cli.py                     human-friendly CLI (solo / paste-in path)
│   ├── mcp_server.py              optional MCP server (stdlib)
│   ├── state-schema.md            the persisted JSON state files
│   └── test_dm_tools.py           tests proving the mechanics
├── guide/
│   ├── SETUP_CHATGPT.md  SETUP_API.md  SETUP_MCP.md
│   └── EXAMPLE_SESSION.md
└── web/                           ← zero-install browser app (AI-powered)
    ├── dnd-dm.html                self-contained: engine + UI + LLM tool-calling
    └── README.md
```

## The tools (what the DM can call)

`roll_dice` · `roll_check` · `encounter_start` · `combatant_add` · `turn_next` ·
`combat_status` · `encounter_end` · `apply_damage` · `heal` · `condition_add` ·
`condition_clear` · `character_set` · `character_get` · `inventory` · `var_set` ·
`var_get` · `table_roll`

All are pure Python standard library, defined once in `dm_tools.py` and exposed
identically to the CLI, the function-calling API path, and the MCP server. State
lives in `campaign_state/` (override with `DM_CAMPAIGN_DIR`). See
`tools/state-schema.md`.

## Design principles

- **Determinism in code, not the model.** Randomness and bookkeeping are
  authoritative; the model is told never to fake a roll or an HP total.
- **System-agnostic.** No ruleset is hardcoded; the player's chosen module
  supplies the numbers via `RULESET_ADAPTER.md`.
- **Persistent & portable.** Plain JSON per campaign; copy the folder to move it.
- **Safety-first.** Session Zero sets binding tone, lines/veils, and a safety word.
- **Zero dependencies.** Runs anywhere with Python 3.8+.

## Credits & license

Part of the emergence-kit project (MIT). The 5e system module paraphrases the
*System Reference Document* © Wizards of the Coast, used under CC-BY-4.0; all other
content here is original. "Dungeons & Dragons" is a trademark of Wizards of the
Coast; this kit is unofficial.
