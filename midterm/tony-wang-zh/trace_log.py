"""Append-only, timestamped traces with no cloud credentials or hidden state."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import uuid


class TraceLog:
    def __init__(self, player: str, directory: str | Path = "traces",
                 game_version: str = "0.5.0"):
        self.player = player
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.path = self.directory / f"{stamp}-{player}-{uuid.uuid4().hex[:8]}.json"
        self.document = {"player": player, "started_at": datetime.now(timezone.utc).isoformat(),
                         "game_version": game_version, "events": []}
        self.flush()

    def add(self, event: dict[str, Any]) -> None:
        self.document["events"].append({"timestamp": datetime.now(timezone.utc).isoformat(), **event})
        self.flush()

    def finish(self, outcome: dict[str, Any], metrics: dict[str, Any] | None = None) -> None:
        self.document["finished_at"] = datetime.now(timezone.utc).isoformat()
        self.document["outcome"] = outcome
        self.document["metrics"] = metrics or {}
        self.flush()

    def flush(self) -> None:
        self.path.write_text(json.dumps(self.document, indent=2, ensure_ascii=False), encoding="utf-8")
