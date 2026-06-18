# Setup — MCP server

For clients that speak the **Model Context Protocol** (Claude Desktop, MCP-enabled
GPT clients, various IDE/agent tools). The model calls the DM tools directly over
MCP; you don't write any dispatch code.

`tools/mcp_server.py` is a pure-stdlib stdio MCP server. It serves the same 17
tools (loaded from `tool-schemas.json`) and shares the same `campaign_state/`
directory as the CLI and API paths.

## 1. Sanity check it runs
```
cd tools
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | python3 mcp_server.py
```
You should see an `initialize` result and a `tools/list` of 17 tools.

## 2. Register it with your client
Add it as an stdio server. Typical JSON config (paths absolute):
```json
{
  "mcpServers": {
    "dnd-dm": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/dnd-dungeon-master/tools/mcp_server.py"],
      "env": { "DM_CAMPAIGN_DIR": "/ABSOLUTE/PATH/my-campaign" }
    }
  }
}
```
- `command`/`args` — how the client launches the server.
- `DM_CAMPAIGN_DIR` — where this campaign's state lives (one directory per
  campaign).

## 3. Provide the persona
Give the model the DM persona as its system/instructions: paste
`instructions/DM_SYSTEM_PROMPT.md` + your chosen `sources/system-modules/*` file.
The MCP server provides the *tools*; the system prompt provides the *behavior*.

## 4. Play
Ask the model to run a game. It will call `roll_dice`, `roll_check`,
`combatant_add`, `apply_damage`, etc. as needed. State persists between sessions
in `DM_CAMPAIGN_DIR`; on a new session the DM can call `combat_status`,
`character_get`, and `var_get` to recap and continue.

## Protocol notes
- Transport: newline-delimited JSON-RPC 2.0 over stdio (MCP `2024-11-05`).
- Implements `initialize`, `tools/list`, `tools/call`, and `ping`; notifications
  are accepted and ignored.
- Stateless rolls (`roll_dice`, `roll_check`) don't touch disk; all other tools
  load, mutate, and save the campaign directory atomically per call.
