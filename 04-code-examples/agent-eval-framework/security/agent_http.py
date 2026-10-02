"""
Serve an agent over HTTP so external red-team tools (Garak, PyRIT) can attack it.

Garak and PyRIT have heavy, conflicting dependencies (torch, transformers,
older `datasets`), so they live in their own environments and talk to the
agent over HTTP instead of importing it.

    OFFLINE=1 python -m security.agent_http --port 8765 --agent support
    curl -s localhost:8765/chat -d '{"message": "What is your refund policy?"}'
    -> {"response": "...", "tools": ["search_knowledge_base"]}

Agents: support (default), banking (SecureBank v1), banking_hardened (v2).
Standard library only; binds to 127.0.0.1.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def run_agent(agent: str, message: str) -> dict:
    if agent.startswith("banking"):
        from agents.banking_agent import run_banking_agent

        r = run_banking_agent(message, hardened=agent == "banking_hardened")
    else:
        from agents.support_agent import run_support_agent

        r = run_support_agent(message)
    return {"response": r["response"], "tools": [t["tool"] for t in r["tool_calls"]]}


def make_handler(agent: str):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode() or "{}"
            try:
                body = json.loads(raw)
                message = body.get("message") or body.get("prompt") or ""
            except json.JSONDecodeError:
                message = raw
            out = json.dumps(run_agent(body.get("agent", agent) if isinstance(body, dict) else agent, message)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *args) -> None:  # keep the console quiet
            pass

    return Handler


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--agent", default="support", choices=["support", "banking", "banking_hardened"])
    a = p.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.agent))
    print(f"Serving {a.agent} agent on http://127.0.0.1:{a.port}/chat")
    server.serve_forever()


if __name__ == "__main__":
    main()
