# Example session — the loop in action

A short worked transcript showing the **decide → call → narrate** loop with real
tool results (the dice values below are actual seeded outputs from `dm_tools.py`,
not invented). System: `5e-srd`. Tool calls are shown in `code blocks`; in the API
or MCP paths the model emits these itself, in the ChatGPT path you run them and
paste the result back.

---

**Session Zero (already done):** ruleset = 5e-srd; tone = heroic with real
danger; safety word = "amber"; one player, Aria.

```
character_set Aria fields={"max_hp":24,"hp":24,"ac":15,"level":3,
  "stats":{"str":1,"dex":3,"con":2,"int":0,"wis":2,"perception":5}}
→ {"name":"Aria","max_hp":24,"hp":24,"ac":15,...}
var_set quest_stage 1
```

---

**DM:** The forest trail narrows. Through the ferns you spot a lone goblin
crouched over a snare, its back to you, scimitar across its knees. The wind covers
small sounds.
*What do you do?*

**Player:** I creep closer along the moss, keeping low, and ready my shortbow.

**DM (decide):** Moving unseen over soft ground, no time pressure — uncertain,
both outcomes interesting. Stealth check, DC 13 (medium, but the wind helps).

```
roll_check  modifier=6  dc=13
→ {"natural":11,"modifier":6,"total":17,"dc":13,"success":true,"margin":4}
```

**DM (narrate):** Total **17** — success. You melt into the undergrowth; the
goblin never lifts its head. You're fifteen feet away with a clear shot. Loose the
arrow?

**Player:** Yes — I take the shot.

**DM (decide):** A surprise attack. Set up the encounter so initiative and HP are
tracked, then resolve the attack vs the goblin's AC 15.

```
encounter_start "Forest Snare"
combatant_add Aria   --initiative 99 --hp 24 --ac 15      # surprise: acts first
combatant_add Goblin --init-mod 2 --hp 7 --ac 15
→ order: ["Aria","Goblin"]
turn_next        → {"round":1,"current":{"name":"Aria"}}

roll_check  modifier=5  dc=15                              # attack vs AC 15
→ {"natural":15,"modifier":5,"total":20,"success":true,"margin":5}
roll_dice  "1d6+3"                                         # shortbow damage
→ {"total":7,...}
apply_damage  Goblin  7
→ {"name":"Goblin","hp":0,"down":true}
```

**DM (narrate):** Your arrow leaps the gap and takes the goblin clean through the
shoulder — **7 damage**, and it drops without a sound (0 HP, down). The snare it
was setting hangs half-finished in the bracken. The forest is quiet again... but
the snare means others were expected.

```
encounter_end
var_set quest_stage 2
```
*The trail forks ahead — left toward woodsmoke, right deeper into shadow. Which
way?*

---

## What to notice
- Every uncertain outcome went through a tool; **no number was invented**. The
  natural rolls (11, 15) and damage (7) are real seeded results.
- HP reached 0 via `apply_damage`, which flagged `down` — the narration follows
  the tracked state, not the other way around.
- The encounter tools handled order and turns; world progress was saved with
  `var_set` so the next session can recap from `combat_status`/`var_get`.
- The DM kept narration tight, respected agency (asked before the kill shot), and
  ended on a hook.
