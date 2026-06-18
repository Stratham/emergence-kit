# Setup — API with function calling

The fully automated path. Your client registers the tool schemas, the model
**calls the tools itself**, and you dispatch those calls to `dm_tools.py`. Works
with any function-calling-capable model (OpenAI GPT, and others with the same
tool-calling shape).

## Pieces
- **System prompt**: `instructions/DM_SYSTEM_PROMPT.md` + the chosen system module
  (+ optionally the `sources/*` files as context).
- **Tools**: `tools/tool-schemas.json` — ready to pass as the `tools` parameter.
- **Executor**: `tools/dm_tools.py` — run the requested function and return its
  JSON result as the tool message.

## Minimal Python harness (OpenAI-style)
```python
import json
from openai import OpenAI            # any function-calling client works
import dm_tools as dt                # tools/dm_tools.py on the path

client = OpenAI()
schemas = json.load(open("tools/tool-schemas.json"))
system = open("instructions/DM_SYSTEM_PROMPT.md").read() \
       + "\n\n" + open("sources/system-modules/5e-srd.md").read()
eng = dt.DMEngine("campaign_state")

def execute(name, args):
    fn = {
        "roll_dice":     lambda a: dt.roll_dice(a["notation"], a.get("advantage", 0)),
        "roll_check":    lambda a: dt.roll_check(a.get("modifier", 0), a.get("dc"),
                                                 a.get("advantage", 0), a.get("die", "1d20")),
        "encounter_start": lambda a: eng.encounter_start(a["name"]),
        "encounter_end":   lambda a: eng.encounter_end(),
        "combat_status":   lambda a: eng.combat_status(),
        "combatant_add":   lambda a: eng.combatant_add(a["name"], a.get("initiative"),
                                                       a.get("init_mod", 0), a.get("hp"), a.get("ac")),
        "turn_next":       lambda a: eng.turn_next(),
        "apply_damage":    lambda a: eng.apply_damage(a["name"], a["amount"]),
        "heal":            lambda a: eng.heal(a["name"], a["amount"]),
        "condition_add":   lambda a: eng.condition_add(a["name"], a["condition"]),
        "condition_clear": lambda a: eng.condition_clear(a["name"], a["condition"]),
        "character_set":   lambda a: eng.character_set(a["name"], a.get("fields", {})),
        "character_get":   lambda a: eng.character_get(a["name"]),
        "inventory":       lambda a: eng.inventory(a["name"], a["action"], a.get("item"), a.get("qty", 1)),
        "var_set":         lambda a: eng.var_set(a["key"], a["value"]),
        "var_get":         lambda a: eng.var_get(a["key"]),
        "table_roll":      lambda a: eng.table_roll(a["name"], a.get("entries")),
    }[name](args)
    eng.save()
    return fn

messages = [{"role": "system", "content": system}]

def turn(user_text):
    messages.append({"role": "user", "content": user_text})
    while True:
        resp = client.chat.completions.create(
            model="gpt-4o", messages=messages, tools=schemas)
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content                      # DM's narration
        for call in msg.tool_calls:                 # resolve every tool call
            result = execute(call.function.name, json.loads(call.function.arguments))
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})

print(turn("I sneak up on the goblin and loose an arrow."))
```

## Notes
- `dm_tools.py` is **stdlib-only**; the only external dependency above is your LLM
  SDK. The dispatch table mirrors `tool-schemas.json` exactly (17 tools).
- State persists to `campaign_state/`; set `DM_CAMPAIGN_DIR` for multiple
  campaigns. The same directory is shared by the CLI and MCP paths.
- For reproducible testing, construct the engine and pass a seeded
  `random.Random` into `roll_dice`/`roll_check` (see `test_dm_tools.py`).
- Keep the system prompt's golden rule intact: the model should resolve a tool
  call *before* narrating the outcome.
