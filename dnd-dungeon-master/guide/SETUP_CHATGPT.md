# Setup — ChatGPT (Custom GPT or Project)

The no-code path. Works with a ChatGPT Custom GPT, a Project, or even a single
long chat. ChatGPT can't run the Python tools itself here, so **you** run the
dice/state commands locally and paste the results back — this keeps every roll
and HP total real instead of hallucinated.

## 1. Build the persona
1. Create a new **Custom GPT** (ChatGPT → Explore GPTs → Create) or a **Project**.
2. Paste `instructions/DM_SYSTEM_PROMPT.md` into the Instructions field.
3. Append the contents of your chosen system module
   (`sources/system-modules/5e-srd.md`, `rules-lite-d20.md`, or your own filled
   `_TEMPLATE.md`).
4. Optional but recommended: also upload `sources/core-procedures.md` and
   `sources/dm-craft.md` as knowledge files so the DM can reference them.

## 2. Wire up real dice and state
You'll run the tools from a terminal alongside the chat. From `tools/`:
```
# one-shots
python3 cli.py roll 2d6+3
python3 cli.py check 5 15 adv        # modifier 5, DC 15, with advantage

# or an interactive session that remembers state
python3 cli.py
dm> sheet Aria max_hp=24 hp=24 ac=15
dm> enc "Goblin Ambush"
dm> join Goblin 12 7 13
dm> dmg Goblin 6
```
State persists to `./campaign_state` (set `DM_CAMPAIGN_DIR` to keep multiple
campaigns side by side).

## 3. The play rhythm
1. The DM (ChatGPT) describes a scene and, when something is uncertain, **asks for
   a specific roll** — e.g. "Make a Stealth check, DC 15."
2. You run it: `python3 cli.py check 6 15` → `🎯 d20(11) +6 = 17 vs DC 15 → SUCCESS`.
3. Paste that line back into the chat. The DM narrates from the real result.
4. For damage/healing/conditions, run the matching command and paste the result so
   the DM's description matches the tracked HP.

> Tip: tell the DM up front, "I'll paste tool results in this format" so it knows
> to wait for them rather than inventing outcomes.

## 4. Session Zero
Before play, walk through `instructions/SESSION_ZERO.md` with the DM: pick the
ruleset, agree tone/safety, and create character sheets (run the `sheet` and
`inv` commands as you go). Then start the adventure.

## Continuity across chats
Because state lives in `campaign_state/`, you can start a fresh chat any time:
paste the system prompt again, run `python3 cli.py show <name>` and
`python3 cli.py status`, and paste those so the DM can recap and continue.
