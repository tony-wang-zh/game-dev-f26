"""Cheap policy using only the public observation and legal actions."""

from __future__ import annotations


class HeuristicPlayer:
    name = "heuristic"

    def choose(self, observation: dict, legal_actions: list[dict]) -> dict:
        action_types = {a.get("type") for a in legal_actions}
        stats = observation["stats"]
        phase = observation["phase"]
        if phase == "initial_purchase":
            item = legal_actions[0]["item"]
            allocations = {"oxen": 250, "food": 280, "ammunition": 40,
                           "clothing": 40, "supplies": 40}
            return {"type": "buy", "item": item,
                    "amount": min(allocations[item], legal_actions[0]["max"])}
        if phase == "fort_purchase":
            item = legal_actions[0]["item"]
            target = {"food": 80 if stats["food"] < observation["miles_remaining"] / 12 else 0,
                      "ammunition": 10 if stats["bullets"] < 100 else 0,
                      "clothing": 10 if stats["clothing"] < 15 else 0,
                      "supplies": 20 if stats["supplies"] < 10 else 0}[item]
            amount = min(target, max(0, stats["cash"] - 20))
            if amount == 0:
                return next(a for a in legal_actions if a["type"] == "finish_fort")
            return {"type": "buy", "item": item, "amount": amount}
        if phase == "travel":
            if "hunt" in action_types and stats["food"] < min(80, observation["miles_remaining"] / 10):
                return {"type": "hunt"}
            if "visit_fort" in action_types and stats["cash"] > 40 and (
                stats["bullets"] < 100 or stats["supplies"] < 8
            ):
                return {"type": "visit_fort"}
            return {"type": "continue"}
        if phase == "shoot":
            return {"type": "shoot", "text": legal_actions[0]["word"]}
        if phase == "ration":
            return {"type": "eat", "level": 2}
        if phase == "event_response":
            return {"type": "rider_response", "choice": "stand_ground"}
        raise ValueError(f"no policy for phase {phase!r}")
