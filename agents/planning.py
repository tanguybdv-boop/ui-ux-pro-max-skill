import uuid
from datetime import datetime, date
from .base import BaseAgent, load_data, save_data

FILE = "events.json"

SYSTEM = """Tu es un assistant de planification expert. Tu gères un calendrier personnel.

Tes responsabilités :
- Ajouter, modifier, supprimer des événements
- Afficher le planning du jour, de la semaine ou d'une période
- Détecter les conflits d'horaires
- Proposer des créneaux libres
- Envoyer des rappels intelligents

Réponds toujours en français, de façon concise et structurée.
La date actuelle est : """ + datetime.now().strftime("%A %d %B %Y")


class PlanningAgent(BaseAgent):
    name = "Planning"
    system_prompt = SYSTEM
    tools = [
        {
            "name": "add_event",
            "description": "Ajouter un événement au calendrier",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titre de l'événement"},
                    "date": {"type": "string", "description": "Date au format YYYY-MM-DD"},
                    "time": {"type": "string", "description": "Heure au format HH:MM"},
                    "duration": {"type": "integer", "description": "Durée en minutes"},
                    "location": {"type": "string", "description": "Lieu (optionnel)"},
                    "notes": {"type": "string", "description": "Notes (optionnel)"},
                },
                "required": ["title", "date", "time"],
            },
        },
        {
            "name": "list_events",
            "description": "Lister les événements d'une période",
            "input_schema": {
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "description": "Date début YYYY-MM-DD"},
                    "to_date": {"type": "string", "description": "Date fin YYYY-MM-DD"},
                },
            },
        },
        {
            "name": "delete_event",
            "description": "Supprimer un événement par son ID",
            "input_schema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID de l'événement"},
                },
                "required": ["event_id"],
            },
        },
        {
            "name": "update_event",
            "description": "Modifier un événement existant",
            "input_schema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID de l'événement"},
                    "title": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "duration": {"type": "integer"},
                    "location": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["event_id"],
            },
        },
        {
            "name": "get_today",
            "description": "Récupérer le planning d'aujourd'hui",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "find_free_slots",
            "description": "Trouver des créneaux libres sur une journée",
            "input_schema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date YYYY-MM-DD"},
                    "duration": {"type": "integer", "description": "Durée souhaitée en minutes"},
                },
                "required": ["date", "duration"],
            },
        },
    ]

    def handle_tool(self, tool_name: str, tool_input: dict):
        events = load_data(FILE)

        if tool_name == "add_event":
            event = {
                "id": str(uuid.uuid4())[:8],
                "title": tool_input["title"],
                "date": tool_input["date"],
                "time": tool_input.get("time", "09:00"),
                "duration": tool_input.get("duration", 60),
                "location": tool_input.get("location", ""),
                "notes": tool_input.get("notes", ""),
                "created_at": datetime.now().isoformat(),
            }
            events.append(event)
            save_data(FILE, events)
            return {"success": True, "event": event}

        elif tool_name == "list_events":
            from_date = tool_input.get("from_date", "")
            to_date = tool_input.get("to_date", "")
            filtered = [
                e for e in events
                if (not from_date or e["date"] >= from_date)
                and (not to_date or e["date"] <= to_date)
            ]
            filtered.sort(key=lambda e: (e["date"], e["time"]))
            return {"events": filtered, "count": len(filtered)}

        elif tool_name == "delete_event":
            event_id = tool_input["event_id"]
            original = len(events)
            events = [e for e in events if e["id"] != event_id]
            if len(events) == original:
                return {"success": False, "error": "Événement introuvable"}
            save_data(FILE, events)
            return {"success": True}

        elif tool_name == "update_event":
            event_id = tool_input["event_id"]
            for event in events:
                if event["id"] == event_id:
                    for key in ["title", "date", "time", "duration", "location", "notes"]:
                        if key in tool_input:
                            event[key] = tool_input[key]
                    save_data(FILE, events)
                    return {"success": True, "event": event}
            return {"success": False, "error": "Événement introuvable"}

        elif tool_name == "get_today":
            today = date.today().isoformat()
            today_events = [e for e in events if e["date"] == today]
            today_events.sort(key=lambda e: e["time"])
            return {"date": today, "events": today_events, "count": len(today_events)}

        elif tool_name == "find_free_slots":
            target_date = tool_input["date"]
            duration = tool_input.get("duration", 60)
            day_events = sorted(
                [e for e in events if e["date"] == target_date],
                key=lambda e: e["time"],
            )
            slots = []
            work_start, work_end = 8 * 60, 19 * 60
            current = work_start
            for event in day_events:
                h, m = map(int, event["time"].split(":"))
                start = h * 60 + m
                end = start + event.get("duration", 60)
                if start - current >= duration:
                    slots.append({
                        "from": f"{current // 60:02d}:{current % 60:02d}",
                        "to": f"{start // 60:02d}:{start % 60:02d}",
                    })
                current = max(current, end)
            if work_end - current >= duration:
                slots.append({
                    "from": f"{current // 60:02d}:{current % 60:02d}",
                    "to": f"{work_end // 60:02d}:{work_end % 60:02d}",
                })
            return {"date": target_date, "free_slots": slots}

        raise NotImplementedError(f"Outil inconnu: {tool_name}")
