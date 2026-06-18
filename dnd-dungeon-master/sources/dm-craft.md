# DM craft — running a great game

Techniques for the *art* of DMing, distilled from established tabletop guidance
(fail-forward design, telegraphing, "lazy" prep, and spotlight management) and
adapted for an LLM running the table. The mechanics live in the tools; this is
about judgment and feel.

## Prepare situations, not plots
Prep **problems, places, and people** — not a fixed sequence of events. A strong
prep kit is: a compelling hook, a handful of NPCs with clear wants, a few
locations, an active threat with a plan, and some secrets to discover. Let player
choices determine the path. Keep a "fronts" list of off-screen threats advancing
on their own.

## Telegraph danger and consequences
Players make good decisions only with good information. Foreshadow traps, tough
fights, and moral stakes *before* they trigger. Surprises should feel earned in
hindsight, never arbitrary. Hidden DCs are fine; hidden *stakes* are not.

## Improvisation toolkit
- **"Yes, and / Yes, but / No, but."** Reward creativity; attach costs instead of
  flat refusals.
- **Ask leading questions.** "What does your character notice first?" pulls
  players in and offloads worldbuilding.
- **Reincorporate.** Bring back an earlier NPC, item, or detail — it makes the
  world feel coherent and authored.
- **Random tables.** Use `table_roll` for unexpected sparks (rumors, loot,
  complications); define tables on the fly with the `entries` argument.

## NPCs that feel alive
Give each a **want**, a **flaw**, and a **voice** (a verbal tic, cadence, or
attitude). Track their state and memory in `vars`/sheets so they react to past
events. A recurring rival or ally is worth more than a dozen nameless extras.

## Pacing and the spotlight
- **Cut to the action.** Skip the boring parts; "you travel three days without
  incident — by dusk you reach the gates."
- **Rotate the spotlight** so every player gets meaningful moments across the
  three pillars.
- **Vary intensity.** Alternate tension and release: a tough fight, then a quiet
  scene; a mystery beat, then a payoff.
- **End on a hook.** Close sessions on a question or cliffhanger.

## Make failure fun
Never let a failed roll stall the story (see `core-procedures.md` "fail forward").
Failure spends a resource, raises the stakes, reveals a cost, or opens a new path
— the story always moves.

## Solo and small-table play
With one player, the DM carries more of the world. Lean on `table_roll` and
"ask/answer" oracles for surprise, give the lone hero an NPC companion or two for
banter and tactical depth, and check in more often about spotlight and tone.

## Continuity discipline (especially for an LLM)
- **Trust the tools, not memory.** Re-read state (`combat_status`,
  `character_get`, key `var_get`s) at the start of each session and before big
  decisions; recap from the `log`.
- **Write important facts down** with `var_set` the moment they're established —
  names, promises, debts, unlocked doors, faction standing.
- **Stay consistent.** If you made a ruling or revealed a fact, honor it later.

## Anti-patterns to avoid
- Railroading (forcing one outcome regardless of choices).
- "Rocket-tag" lethality or trivial cakewalks — calibrate DCs and HP to the
  party.
- Narrating the players' internal states or decisions for them.
- Info-dumping lore; reveal it through play.
- Inventing dice/HP results instead of calling the tools.
