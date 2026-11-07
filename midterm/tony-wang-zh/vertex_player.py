"""Text-only Vertex player. The provider receives no tools or file access."""

from __future__ import annotations

import json
from pathlib import Path
import re
import time
from typing import Any


SYSTEM_PROMPT = """You are the Oregon Trail gameplay agent. Try to reach Oregon City and keep the travelers alive. You receive only the visible game observation and legal-action list. Return exactly one JSON action. For a buy template with min and max, provide type, item, and a numeric amount within that inclusive range; omit min and max. For a shoot template with word, return type shoot and text equal to that word; omit word. For other actions, copy the action. Never invent a type, use hidden state, or use tools."""


class VertexPlayer:
    name = "vertex"

    def __init__(self, config_path: str | Path, prompt_path: str | Path,
                 timeout_seconds: float = 35.0):
        self.config_path = Path(config_path)
        self.prompt_path = Path(prompt_path)
        self.timeout_seconds = timeout_seconds
        self.client = None
        self.model = ""
        self.project = ""
        self.location = ""
        self.input_tokens = 0
        self.output_tokens = 0
        self.call_count = 0
        self.call_failures = 0
        self.call_seconds: list[float] = []
        self.system_prompt = SYSTEM_PROMPT

    def _connect(self) -> None:
        if self.client is not None:
            return
        try:
            info = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.project = info["project id"]
            self.location = info["location"]
            self.model = info["model"]
            self.system_prompt = self.prompt_path.read_text(encoding="utf-8")
        except (OSError, KeyError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Could not read Vertex settings from {self.config_path}: {exc}") from exc
        from google import genai
        self.client = genai.Client(vertexai=True, project=self.project, location=self.location)
        # Trigger ADC validation before an episode spends its call budget.
        try:
            import google.auth
            google.auth.default()
        except Exception as exc:
            self.client.close()
            self.client = None
            raise RuntimeError(
                "Google Cloud authentication is unavailable. Run `gcloud auth application-default login` "
                "in a terminal, then retry."
            ) from exc

    def choose(self, observation: dict[str, Any], legal_actions: list[dict[str, Any]],
               timeout_seconds: float | None = None) -> tuple[Any, dict[str, Any]]:
        self._connect()
        timeout = min(self.timeout_seconds, timeout_seconds or self.timeout_seconds)
        prompt = json.dumps({"observation": observation, "legal_actions": legal_actions},
                            ensure_ascii=False)
        start = time.monotonic()
        self.call_count += 1
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"system_instruction": self.system_prompt,
                        "response_mime_type": "application/json",
                        "max_output_tokens": 180,
                        "temperature": 0.1,
                        "http_options": {"timeout": int(timeout * 1000)}},
            )
            elapsed = time.monotonic() - start
            self.call_seconds.append(elapsed)
            raw = response.text or ""
            usage = getattr(response, "usage_metadata", None)
            self.input_tokens += int(getattr(usage, "prompt_token_count", 0) or 0)
            self.output_tokens += int(getattr(usage, "candidates_token_count", 0) or 0)
            try:
                action = json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
                action = json.loads(match.group(0)) if match else raw
            return action, {"elapsed_seconds": elapsed,
                            "input_tokens": int(getattr(usage, "prompt_token_count", 0) or 0),
                            "output_tokens": int(getattr(usage, "candidates_token_count", 0) or 0),
                            "model": self.model}
        except Exception:
            self.call_failures += 1
            self.call_seconds.append(time.monotonic() - start)
            raise

    def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None
