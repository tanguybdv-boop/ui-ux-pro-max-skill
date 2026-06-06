import os
import json
import urllib.request
import urllib.error
from typing import Any

OLLAMA_URL   = os.environ.get("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "agents")


def load_data(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(filename: str, data: list) -> None:
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _ollama_request(endpoint: str, payload: dict) -> dict:
    url  = f"{OLLAMA_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Impossible de joindre Ollama sur {OLLAMA_URL}.\n"
            f"Installez Ollama : https://ollama.com\n"
            f"Puis lancez : ollama pull {OLLAMA_MODEL}\n"
            f"Détail : {e}"
        )


def ollama_available() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except Exception:
        return False


def list_local_models() -> list[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


class BaseAgent:
    name: str = "Agent"
    system_prompt: str = "Tu es un assistant utile."
    tools: list[dict] = []

    def __init__(self):
        self.history: list[dict] = []
        self.model = OLLAMA_MODEL

    def handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        raise NotImplementedError(f"Outil inconnu: {tool_name}")

    def _build_messages(self, user_message: str) -> list[dict]:
        msgs = [{"role": "system", "content": self.system_prompt}]
        msgs.extend(self.history)
        msgs.append({"role": "user", "content": user_message})
        return msgs

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        while True:
            payload: dict = {"model": self.model, "messages": messages, "stream": False}
            if self.tools:
                # Convert Anthropic-style tool schema to Ollama/OpenAI format
                payload["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t.get("description", ""),
                            "parameters": t.get("input_schema", {}),
                        },
                    }
                    for t in self.tools
                ]

            resp = _ollama_request("/api/chat", payload)
            msg  = resp.get("message", {})

            tool_calls = msg.get("tool_calls", [])
            if tool_calls:
                messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
                self.history.append({"role": "assistant", "content": "", "tool_calls": tool_calls})

                for call in tool_calls:
                    fn   = call.get("function", {})
                    name = fn.get("name", "")
                    args = fn.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    try:
                        result = self.handle_tool(name, args)
                        content = json.dumps(result, ensure_ascii=False)
                    except Exception as e:
                        content = f"Erreur: {e}"

                    tool_msg = {"role": "tool", "content": content}
                    messages.append(tool_msg)
                    self.history.append(tool_msg)

                continue

            text = msg.get("content", "")
            self.history.append({"role": "assistant", "content": text})
            return text

    def reset(self):
        self.history = []
