import os
import json
from typing import Any
import anthropic

MODEL = "claude-sonnet-4-6"
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


class BaseAgent:
    name: str = "Agent"
    system_prompt: str = "Tu es un assistant utile."
    tools: list[dict] = []

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY non défini. Exécutez:\n"
                "  export ANTHROPIC_API_KEY=sk-ant-..."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.history: list[dict] = []

    def handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        raise NotImplementedError(f"Outil inconnu: {tool_name}")

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        while True:
            kwargs = {
                "model": MODEL,
                "max_tokens": 4096,
                "system": self.system_prompt,
                "messages": self.history,
            }
            if self.tools:
                kwargs["tools"] = self.tools

            response = self.client.messages.create(**kwargs)

            if response.stop_reason == "tool_use":
                assistant_content = response.content
                self.history.append({"role": "assistant", "content": assistant_content})

                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        try:
                            result = self.handle_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result, ensure_ascii=False),
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Erreur: {e}",
                                "is_error": True,
                            })

                self.history.append({"role": "user", "content": tool_results})
                continue

            text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            self.history.append({"role": "assistant", "content": text})
            return text

    def reset(self):
        self.history = []
