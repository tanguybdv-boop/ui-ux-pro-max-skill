import uuid
from datetime import datetime
from .base import BaseAgent, load_data, save_data

FILE = "tasks.json"

SYSTEM = """Tu es un assistant de gestion des tâches expert. Tu gères une liste de tâches personnelle.

Tes responsabilités :
- Ajouter, modifier, supprimer des tâches
- Réorganiser les priorités (haute, moyenne, basse)
- Marquer les tâches comme terminées
- Regrouper les tâches par projet ou catégorie
- Identifier les tâches urgentes et importantes (matrice Eisenhower)
- Suggérer un ordre d'exécution optimal

Réponds toujours en français, de façon concise et structurée.
La date actuelle est : """ + datetime.now().strftime("%A %d %B %Y")


PRIORITIES = {"haute": 1, "moyenne": 2, "basse": 3}


class TaskAgent(BaseAgent):
    name = "Tâches"
    system_prompt = SYSTEM
    tools = [
        {
            "name": "add_task",
            "description": "Ajouter une nouvelle tâche",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titre de la tâche"},
                    "priority": {
                        "type": "string",
                        "enum": ["haute", "moyenne", "basse"],
                        "description": "Priorité",
                    },
                    "due_date": {"type": "string", "description": "Date limite YYYY-MM-DD"},
                    "project": {"type": "string", "description": "Projet/catégorie"},
                    "notes": {"type": "string", "description": "Notes supplémentaires"},
                },
                "required": ["title"],
            },
        },
        {
            "name": "list_tasks",
            "description": "Lister les tâches avec filtres optionnels",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["todo", "done", "all"],
                        "description": "Filtrer par statut",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["haute", "moyenne", "basse"],
                    },
                    "project": {"type": "string"},
                },
            },
        },
        {
            "name": "complete_task",
            "description": "Marquer une tâche comme terminée",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "update_task",
            "description": "Modifier une tâche existante",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "priority": {"type": "string", "enum": ["haute", "moyenne", "basse"]},
                    "due_date": {"type": "string"},
                    "project": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "delete_task",
            "description": "Supprimer une tâche",
            "input_schema": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
            },
        },
        {
            "name": "reprioritize",
            "description": "Réorganiser automatiquement les priorités selon les dates limite et l'importance",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_today_tasks",
            "description": "Obtenir les tâches à faire aujourd'hui (dues ou haute priorité)",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    def handle_tool(self, tool_name: str, tool_input: dict):
        tasks = load_data(FILE)

        if tool_name == "add_task":
            task = {
                "id": str(uuid.uuid4())[:8],
                "title": tool_input["title"],
                "priority": tool_input.get("priority", "moyenne"),
                "due_date": tool_input.get("due_date", ""),
                "project": tool_input.get("project", ""),
                "notes": tool_input.get("notes", ""),
                "status": "todo",
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
            }
            tasks.append(task)
            save_data(FILE, tasks)
            return {"success": True, "task": task}

        elif tool_name == "list_tasks":
            status_filter = tool_input.get("status", "todo")
            filtered = tasks
            if status_filter != "all":
                filtered = [t for t in filtered if t["status"] == status_filter]
            if "priority" in tool_input:
                filtered = [t for t in filtered if t["priority"] == tool_input["priority"]]
            if "project" in tool_input:
                filtered = [
                    t for t in filtered
                    if tool_input["project"].lower() in t["project"].lower()
                ]
            filtered.sort(key=lambda t: (PRIORITIES.get(t["priority"], 9), t.get("due_date", "9999")))
            return {"tasks": filtered, "count": len(filtered)}

        elif tool_name == "complete_task":
            for task in tasks:
                if task["id"] == tool_input["task_id"]:
                    task["status"] = "done"
                    task["completed_at"] = datetime.now().isoformat()
                    save_data(FILE, tasks)
                    return {"success": True, "task": task}
            return {"success": False, "error": "Tâche introuvable"}

        elif tool_name == "update_task":
            for task in tasks:
                if task["id"] == tool_input["task_id"]:
                    for key in ["title", "priority", "due_date", "project", "notes"]:
                        if key in tool_input:
                            task[key] = tool_input[key]
                    save_data(FILE, tasks)
                    return {"success": True, "task": task}
            return {"success": False, "error": "Tâche introuvable"}

        elif tool_name == "delete_task":
            original = len(tasks)
            tasks = [t for t in tasks if t["id"] != tool_input["task_id"]]
            if len(tasks) == original:
                return {"success": False, "error": "Tâche introuvable"}
            save_data(FILE, tasks)
            return {"success": True}

        elif tool_name == "reprioritize":
            today = datetime.now().date().isoformat()
            for task in tasks:
                if task["status"] == "done":
                    continue
                due = task.get("due_date", "")
                if due and due <= today:
                    task["priority"] = "haute"
                elif due and due <= (datetime.now().date().isoformat()[:7] + "-31"):
                    if task["priority"] == "basse":
                        task["priority"] = "moyenne"
            save_data(FILE, tasks)
            todo = [t for t in tasks if t["status"] == "todo"]
            todo.sort(key=lambda t: (PRIORITIES.get(t["priority"], 9), t.get("due_date", "9999")))
            return {"success": True, "reordered_tasks": todo}

        elif tool_name == "get_today_tasks":
            today = datetime.now().date().isoformat()
            relevant = [
                t for t in tasks
                if t["status"] == "todo"
                and (t["priority"] == "haute" or (t.get("due_date") and t["due_date"] <= today))
            ]
            relevant.sort(key=lambda t: (PRIORITIES.get(t["priority"], 9), t.get("due_date", "9999")))
            return {"date": today, "tasks": relevant, "count": len(relevant)}

        raise NotImplementedError(f"Outil inconnu: {tool_name}")
