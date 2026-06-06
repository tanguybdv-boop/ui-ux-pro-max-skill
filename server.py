#!/usr/bin/env python3
"""
Serveur web pour le système multi-agents.
Usage: python3 server.py
Puis ouvrir: http://localhost:8080
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import Orchestrator, AGENTS  # noqa: E402

orchestrator = Orchestrator()

HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence les logs HTTP

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(HTML_FILE, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/status":
            self.send_json({"status": "ok", "agents": list(AGENTS.keys())})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/chat":
            message = body.get("message", "").strip()
            agent_lock = body.get("agent")  # "planning" | "tasks" | "email" | None

            if not message:
                self.send_json({"error": "Message vide"}, 400)
                return

            if agent_lock and agent_lock in AGENTS:
                orchestrator._active = agent_lock
            else:
                orchestrator._active = None

            try:
                response, used_agent = orchestrator.chat(message)
                self.send_json({"response": response, "agent": used_agent})
            except EnvironmentError as e:
                self.send_json({"error": str(e)}, 500)
            except Exception as e:
                self.send_json({"error": f"Erreur: {e}"}, 500)

        elif self.path == "/reset":
            agent = body.get("agent")
            orchestrator.reset_agent(agent)
            self.send_json({"success": True})

        else:
            self.send_json({"error": "Route inconnue"}, 404)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY non défini.")
        print("   Exécutez : export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n🚀 Serveur démarré → http://localhost:{port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")


if __name__ == "__main__":
    main()
