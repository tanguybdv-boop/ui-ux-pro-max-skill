#!/usr/bin/env python3
"""
Système multi-agents personnel.
Usage: python3 agent.py [planning|tasks|email]
"""

import sys
import os
import readline  # noqa: F401 — active l'historique de saisie

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import Orchestrator, AGENTS  # noqa: E402

AGENT_LABELS = {
    "planning": "📅 Planning",
    "tasks": "✅ Tâches",
    "email": "✉️  Email",
}

HELP = """\
Commandes disponibles :
  /planning   — Basculer vers l'agent Planning
  /tasks      — Basculer vers l'agent Tâches
  /email      — Basculer vers l'agent Email
  /auto       — Détection automatique de l'agent (défaut)
  /reset      — Réinitialiser la conversation en cours
  /help       — Afficher cette aide
  /quit       — Quitter

L'agent est sélectionné automatiquement selon votre message.
Tapez directement votre demande en langage naturel.
"""

BANNER = """
╔══════════════════════════════════════════════════════╗
║         🤖  Système Multi-Agents Personnel           ║
║                                                      ║
║   📅 Planning  ·  ✅ Tâches  ·  ✉️  Email           ║
╚══════════════════════════════════════════════════════╝
Tapez /help pour les commandes. Ctrl+C ou /quit pour quitter.
"""


def get_prompt(active: str | None) -> str:
    if active:
        label = AGENT_LABELS.get(active, active)
        return f"\n[{label}] Vous > "
    return "\n[Auto] Vous > "


def main():
    print(BANNER)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY non défini.")
        print("   Exécutez : export ANTHROPIC_API_KEY=sk-ant-...")
        print("   Puis relancez : python3 agent.py\n")
        sys.exit(1)

    initial_agent = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in AGENTS:
            initial_agent = arg

    orchestrator = Orchestrator()

    if initial_agent:
        print(orchestrator.switch(initial_agent))

    while True:
        try:
            user_input = input(get_prompt(orchestrator._active)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nAu revoir ! 👋")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input[1:].split()[0].lower()

            if cmd == "quit":
                print("Au revoir ! 👋")
                break
            elif cmd == "help":
                print(HELP)
            elif cmd in AGENTS:
                print(orchestrator.switch(cmd))
            elif cmd == "auto":
                orchestrator._active = None
                print("Mode détection automatique activé.")
            elif cmd == "reset":
                orchestrator.reset_agent(orchestrator._active)
                print("Conversation réinitialisée.")
            else:
                print(f"Commande inconnue : /{cmd}. Tapez /help.")
            continue

        try:
            response, used_agent = orchestrator.chat(user_input)
            label = AGENT_LABELS.get(used_agent, used_agent)
            print(f"\n[{label}] Agent > {response}")
        except EnvironmentError as e:
            print(f"\n⚠️  {e}")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}")


if __name__ == "__main__":
    main()
