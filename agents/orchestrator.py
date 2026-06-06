import os
import re
from .planning import PlanningAgent
from .tasks import TaskAgent
from .email import EmailAgent

AGENTS = {
    "planning": PlanningAgent,
    "tasks": TaskAgent,
    "email": EmailAgent,
}

ROUTING_KEYWORDS = {
    "planning": [
        r"\b(rendez-vous|réunion|meeting|agenda|calendrier|planning|créneau|horaire|"
        r"événement|event|rappel|reminder|schedule|disponib|libre|occupé|"
        r"demain|aujourd'hui|semaine|mois|heure|matin|après-midi|soir)\b"
    ],
    "tasks": [
        r"\b(tâche|task|todo|to-do|faire|priorité|priority|projet|project|"
        r"urgent|important|liste|deadline|échéance|terminer|complet|finir|"
        r"réorganis|reorganis|backlog)\b"
    ],
    "email": [
        r"\b(mail|email|e-mail|message|envoyer|rédiger|répondre|reply|objet|"
        r"destinataire|brouillon|draft|template|modèle|cc|bcc|sujet|"
        r"newsletter|courrier)\b"
    ],
}


def detect_agent(message: str) -> str | None:
    msg_lower = message.lower()
    scores = {}
    for agent_name, patterns in ROUTING_KEYWORDS.items():
        count = sum(len(re.findall(p, msg_lower)) for p in patterns)
        if count > 0:
            scores[agent_name] = count
    if scores:
        return max(scores, key=scores.get)
    return None


class Orchestrator:
    def __init__(self):
        self._agents: dict[str, object] = {}
        self._active: str | None = None

    def _get_agent(self, name: str):
        if name not in self._agents:
            self._agents[name] = AGENTS[name]()
        return self._agents[name]

    def switch(self, agent_name: str) -> str:
        if agent_name not in AGENTS:
            return f"Agent inconnu. Disponibles : {', '.join(AGENTS.keys())}"
        self._active = agent_name
        return f"Basculé vers l'agent **{AGENTS[agent_name].name}**."

    def chat(self, message: str) -> tuple[str, str]:
        if self._active:
            agent_name = self._active
        else:
            agent_name = detect_agent(message)
            if not agent_name:
                agent_name = "tasks"

        agent = self._get_agent(agent_name)
        response = agent.chat(message)
        return response, agent_name

    def reset_agent(self, agent_name: str | None = None):
        if agent_name:
            if agent_name in self._agents:
                self._agents[agent_name].reset()
        else:
            for a in self._agents.values():
                a.reset()
