#!/usr/bin/env python3
"""
mcp_server.py — Expose the DM engine as a Model Context Protocol (MCP) server.

Lets any MCP-capable client (Claude Desktop, MCP-enabled GPT clients, IDE agents,
etc.) call the deterministic DM tools directly. Pure stdlib: implements the MCP
stdio transport (newline-delimited JSON-RPC 2.0) with no third-party packages.

Run:        python3 mcp_server.py
Configure your client to launch this file as an stdio MCP server. The campaign
directory comes from the DM_CAMPAIGN_DIR environment variable (default ./campaign_state).

Tool definitions are loaded from tool-schemas.json so they never drift from the
function-calling specs used by the API path.
"""

import json
import os
import sys
from typing import Any, Dict, List

import dm_tools as dt

PROTOCOL_VERSION = "2024-11-05"
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_schemas() -> List[Dict[str, Any]]:
    with open(os.path.join(HERE, "tool-schemas.json"), encoding="utf-8") as f:
        return json.load(f)


def _dispatch(name: str, args: Dict[str, Any]) -> Any:
    """Route an MCP tool call to the engine. Stateless rolls skip persistence."""
    if name == "roll_dice":
        return dt.roll_dice(args["notation"], advantage=args.get("advantage", 0))
    if name == "roll_check":
        return dt.roll_check(modifier=args.get("modifier", 0), dc=args.get("dc"),
                             die=args.get("die", "1d20"),
                             advantage=args.get("advantage", 0))

    eng = dt.DMEngine(os.environ.get("DM_CAMPAIGN_DIR", "campaign_state"))
    if name == "encounter_start":
        out = eng.encounter_start(args["name"])
    elif name == "encounter_end":
        out = eng.encounter_end()
    elif name == "combat_status":
        return eng.combat_status()
    elif name == "combatant_add":
        out = eng.combatant_add(args["name"], initiative=args.get("initiative"),
                                init_mod=args.get("init_mod", 0),
                                hp=args.get("hp"), ac=args.get("ac"))
    elif name == "turn_next":
        out = eng.turn_next()
    elif name == "apply_damage":
        out = eng.apply_damage(args["name"], args["amount"])
    elif name == "heal":
        out = eng.heal(args["name"], args["amount"])
    elif name == "condition_add":
        out = eng.condition_add(args["name"], args["condition"])
    elif name == "condition_clear":
        out = eng.condition_clear(args["name"], args["condition"])
    elif name == "character_set":
        out = eng.character_set(args["name"], args.get("fields", {}))
    elif name == "character_get":
        return eng.character_get(args["name"])
    elif name == "inventory":
        out = eng.inventory(args["name"], args["action"], args.get("item"),
                            args.get("qty", 1))
    elif name == "var_set":
        out = eng.var_set(args["key"], args["value"])
    elif name == "var_get":
        return eng.var_get(args["key"])
    elif name == "table_roll":
        out = eng.table_roll(args["name"], entries=args.get("entries"))
    else:
        raise ValueError(f"unknown tool: {name}")
    eng.save()
    return out


def _handle(req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    rid = req.get("id")

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "dnd-dungeon-master", "version": "1.0.0"},
        }
    elif method == "tools/list":
        tools = [{
            "name": s["function"]["name"],
            "description": s["function"]["description"],
            "inputSchema": s["function"]["parameters"],
        } for s in _load_schemas()]
        result = {"tools": tools}
    elif method == "tools/call":
        params = req.get("params", {})
        try:
            data = _dispatch(params["name"], params.get("arguments", {}))
            result = {"content": [{"type": "text",
                                   "text": json.dumps(data, ensure_ascii=False)}]}
        except (KeyError, ValueError) as exc:
            result = {"content": [{"type": "text", "text": f"error: {exc}"}],
                      "isError": True}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": rid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}

    return {"jsonrpc": "2.0", "id": rid, "result": result}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        if req.get("id") is None and req.get("method", "").startswith("notifications/"):
            continue  # notifications need no response
        response = _handle(req)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
