"""A minimal client for the ScraperCompany MCP server, using only the Python standard library.

Most people connect through an MCP client (Claude, Cursor, ChatGPT...). This file shows what
those clients do underneath: each tool call is one JSON-RPC POST to the Streamable HTTP endpoint.
The server is stateless, so there is no session to open first.
"""

import json
import os
import sys
import urllib.error
import urllib.request

MCP_URL = os.environ.get("SCRAPERCOMPANY_MCP_URL", "https://api.scrapercompany.com/mcp")


def _api_key() -> str:
    key = os.environ.get("SCRAPERCOMPANY_API_KEY")
    if not key:
        sys.exit("Set SCRAPERCOMPANY_API_KEY first. Get a key at https://scrapercompany.com/pricing")
    return key


def _post(payload: dict) -> dict:
    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "x-api-key": _api_key(),
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            body = response.read().decode()
    except urllib.error.HTTPError as err:
        sys.exit(f"HTTP {err.code} from {MCP_URL}: {err.read().decode()[:300]}")
    # The server answers with plain JSON; an SSE-framed answer is unwrapped just in case.
    if not body.lstrip().startswith("{"):
        body = "\n".join(line[5:] for line in body.splitlines() if line.startswith("data:"))
    return json.loads(body)


def list_tools() -> list[dict]:
    """The tools this connection can see. Free."""
    return _post({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]


def call(tool: str, **arguments) -> dict:
    """Call one tool and return its JSON result. Raises RuntimeError when the tool reports an error."""
    reply = _post({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": arguments}})
    if "error" in reply:
        raise RuntimeError(f"{tool}: {reply['error'].get('message')}")
    result = reply["result"]
    text = "".join(part.get("text", "") for part in result.get("content", []) if part.get("type") == "text")
    if result.get("isError"):
        raise RuntimeError(f"{tool}: {text[:500]}")
    if "structuredContent" in result:
        return result["structuredContent"]
    return json.loads(text) if text else {}


if __name__ == "__main__":
    for t in list_tools():
        print(f"{t['name']:<28} {t.get('title', '')}")
