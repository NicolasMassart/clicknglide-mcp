"""Petit client MCP stdio de test (lecture seule). Usage :
  .venv/bin/python tests/smoke_client.py [--api] [--messenger]"""
import asyncio, json, os, sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent

def summarize(res):
    txt = "".join(getattr(c, "text", "") for c in res.content)
    try:
        return json.loads(txt)
    except Exception:
        return txt

async def main():
    params = StdioServerParameters(command=str(ROOT / ".venv/bin/python"), args=["-m", "clicknglide_mcp"],
                                   cwd=str(ROOT), env=dict(os.environ))
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print(f"tools/list : {len(tools)} outils")
            for t in tools:
                print("  -", t.name)
            pv = summarize(await s.call_tool("delete_signup", {"signup_id": 1}))
            print("aperçu delete_signup (sans confirm) :", json.dumps(pv, ensure_ascii=False)[:300])
            if "--api" in sys.argv:
                roles = summarize(await s.call_tool("get_roles", {}))
                print("get_roles :", json.dumps(roles, ensure_ascii=False)[:600])
                ev = summarize(await s.call_tool("get_next_events", {}))
                print("get_next_events :", ("dates=" + str(list(ev.get("nextEvents", {}).keys())[:10])) if isinstance(ev, dict) and "nextEvents" in ev else str(ev)[:300])
                fc = summarize(await s.call_tool("get_forum_conversations", {}))
                print("get_forum_conversations :", (f"{len(fc['forumConversations'])} conversations") if isinstance(fc, dict) and "forumConversations" in fc else str(fc)[:300])
                print("get_api_usage :", summarize(await s.call_tool("get_api_usage", {})))
            else:
                print("get_roles :", summarize(await s.call_tool("get_roles", {})))
            if "--messenger" in sys.argv:
                lm = summarize(await s.call_tool("list_messages", {"folder": "inbox", "page_size": 2}))
                print("list_messages :", {k: lm.get(k) for k in ("total", "page", "has_more")} if "total" in lm else lm,
                      [c["title"] for c in lm.get("conversations", [])])
                lr = summarize(await s.call_tool("list_recipients", {}))
                print("list_recipients :", (len(lr["members"]), "membres,", len(lr["groups"]), "groupes") if "members" in lr else lr)
            else:
                print("list_messages :", summarize(await s.call_tool("list_messages", {"page_size": 1})))

asyncio.run(main())
