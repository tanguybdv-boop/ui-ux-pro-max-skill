#!/usr/bin/env python3
"""
Serveur web pour le système multi-agents (via Ollama — sans clé API).
Usage: python3 server.py
Puis ouvrir: http://localhost:8080
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.base import ollama_available, list_local_models, OLLAMA_URL, OLLAMA_MODEL  # noqa
from agents.orchestrator import Orchestrator, AGENTS  # noqa

orchestrator = Orchestrator()
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

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
            models = list_local_models()
            self.send_json({
                "ollama": ollama_available(),
                "model": OLLAMA_MODEL,
                "models": models,
                "agents": list(AGENTS.keys()),
            })

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/chat":
            message = body.get("message", "").strip()
            agent_lock = body.get("agent")
            model = body.get("model")

            if not message:
                self.send_json({"error": "Message vide"}, 400)
                return

            # Allow per-request model override
            if model:
                import agents.base as base_module
                base_module.OLLAMA_MODEL = model
                for a in orchestrator._agents.values():
                    a.model = model

            orchestrator._active = agent_lock if agent_lock in AGENTS else None

            try:
                response, used_agent = orchestrator.chat(message)
                self.send_json({"response": response, "agent": used_agent})
            except ConnectionError as e:
                self.send_json({"error": str(e)}, 503)
            except Exception as e:
                self.send_json({"error": f"Erreur: {e}"}, 500)

        elif self.path == "/reset":
            agent = body.get("agent")
            orchestrator.reset_agent(agent)
            self.send_json({"success": True})

        else:
            self.send_json({"error": "Route inconnue"}, 404)


def main():
    port = int(os.environ.get("PORT", 8080))

    print(f"\n🤖 Système Multi-Agents — Ollama ({OLLAMA_URL})")
    print(f"   Modèle : {OLLAMA_MODEL}")

    if not ollama_available():
        print("\n⚠️  Ollama n'est pas lancé.")
        print("   1. Installez Ollama : https://ollama.com")
        print(f"   2. Téléchargez un modèle : ollama pull {OLLAMA_MODEL}")
        print("   3. Relancez ce serveur.")
        print("\n   Le serveur démarre quand même — relancez Ollama puis rechargez la page.\n")
    else:
        models = list_local_models()
        print(f"   Modèles disponibles : {', '.join(models) if models else 'aucun'}")

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n🚀 Serveur démarré → http://localhost:{port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")


if __name__ == "__main__":
    main()
