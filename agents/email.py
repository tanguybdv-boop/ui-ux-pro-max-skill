import uuid
from datetime import datetime
from .base import BaseAgent, load_data, save_data

FILE = "emails.json"

SYSTEM = """Tu es un assistant de gestion des emails expert. Tu rédiges, améliores et organises les emails.

Tes responsabilités :
- Rédiger des emails professionnels ou personnels
- Améliorer le ton, la clarté et la structure d'un email
- Suggérer des réponses à des emails reçus
- Traduire des emails
- Résumer des emails longs
- Créer des modèles réutilisables

Réponds toujours en français sauf si une autre langue est demandée.
Tes emails sont clairs, concis et professionnels.
La date actuelle est : """ + datetime.now().strftime("%A %d %B %Y")


class EmailAgent(BaseAgent):
    name = "Email"
    system_prompt = SYSTEM
    tools = [
        {
            "name": "draft_email",
            "description": "Rédiger un email et le sauvegarder dans les brouillons",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Destinataire"},
                    "subject": {"type": "string", "description": "Objet"},
                    "body": {"type": "string", "description": "Corps de l'email"},
                    "tone": {
                        "type": "string",
                        "enum": ["formel", "professionnel", "amical", "urgent"],
                        "description": "Ton de l'email",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags pour organiser",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
        {
            "name": "list_drafts",
            "description": "Lister les emails brouillons",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "Filtrer par tag"},
                },
            },
        },
        {
            "name": "get_draft",
            "description": "Récupérer le contenu complet d'un brouillon",
            "input_schema": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
            },
        },
        {
            "name": "delete_draft",
            "description": "Supprimer un brouillon",
            "input_schema": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
            },
        },
        {
            "name": "save_template",
            "description": "Sauvegarder un email comme modèle réutilisable",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nom du modèle"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "description": {"type": "string", "description": "Description de l'utilisation"},
                },
                "required": ["name", "subject", "body"],
            },
        },
        {
            "name": "list_templates",
            "description": "Lister les modèles d'emails disponibles",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    def handle_tool(self, tool_name: str, tool_input: dict):
        data = load_data(FILE)
        drafts = [d for d in data if d.get("type") == "draft"]
        templates = [d for d in data if d.get("type") == "template"]

        if tool_name == "draft_email":
            draft = {
                "id": str(uuid.uuid4())[:8],
                "type": "draft",
                "to": tool_input["to"],
                "subject": tool_input["subject"],
                "body": tool_input["body"],
                "tone": tool_input.get("tone", "professionnel"),
                "tags": tool_input.get("tags", []),
                "created_at": datetime.now().isoformat(),
            }
            data.append(draft)
            save_data(FILE, data)
            return {"success": True, "draft": draft}

        elif tool_name == "list_drafts":
            tag = tool_input.get("tag", "")
            filtered = drafts
            if tag:
                filtered = [d for d in filtered if tag in d.get("tags", [])]
            return {
                "drafts": [
                    {"id": d["id"], "to": d["to"], "subject": d["subject"],
                     "tone": d.get("tone"), "tags": d.get("tags", []),
                     "created_at": d["created_at"]}
                    for d in filtered
                ],
                "count": len(filtered),
            }

        elif tool_name == "get_draft":
            for draft in drafts:
                if draft["id"] == tool_input["draft_id"]:
                    return draft
            return {"error": "Brouillon introuvable"}

        elif tool_name == "delete_draft":
            original = len(data)
            data = [d for d in data if d.get("id") != tool_input["draft_id"]]
            if len(data) == original:
                return {"success": False, "error": "Brouillon introuvable"}
            save_data(FILE, data)
            return {"success": True}

        elif tool_name == "save_template":
            template = {
                "id": str(uuid.uuid4())[:8],
                "type": "template",
                "name": tool_input["name"],
                "subject": tool_input["subject"],
                "body": tool_input["body"],
                "description": tool_input.get("description", ""),
                "created_at": datetime.now().isoformat(),
            }
            data.append(template)
            save_data(FILE, data)
            return {"success": True, "template": template}

        elif tool_name == "list_templates":
            return {
                "templates": [
                    {"id": t["id"], "name": t["name"], "description": t.get("description"),
                     "subject": t["subject"]}
                    for t in templates
                ],
                "count": len(templates),
            }

        raise NotImplementedError(f"Outil inconnu: {tool_name}")
