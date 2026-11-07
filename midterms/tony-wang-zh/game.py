"""Seeded, bounded Oregon Trail episode and five-operation player interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import random
import time
from typing import Any

PLAYER_ID = "traveler"
GAME_VERSION = "0.5.0"
SAVE_VERSION = 1
PURCHASE_ITEMS = ("oxen", "food", "ammunition", "clothing", "supplies")
FORT_ITEMS = ("food", "ammunition", "clothing", "supplies")
ITEM_MULTIPLIERS = {"oxen": 1.0, "food": 1.0, "ammunition": 50.0,
                    "clothing": 1.0, "supplies": 1.0}
RATION_COSTS = {1: 13, 2: 18, 3: 23}


@dataclass
class GameState:
    seed: int
    cash: float = 700.0
    oxen: float = 0.0
    food: float = 0.0
    bullets: float = 0.0
    clothing: float = 0.0
    supplies: float = 0.0
    miles: float = 0.0
    turn: int = 0
    phase: str = "initial_purchase"
    purchase_index: int = 0
    fort_index: int = 0
    fort_available: bool = True
    active_event: str | None = None
    event_text: str | None = None
    shoot_started_at: float | None = None
    consecutive_invalid: int = 0
    invalid_actions: int = 0
    status: str = "ongoing"
    reason: str | None = None
    score: int = 0
    last_result: str = ""
    model_calls: int = 0
    failed_model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0


class OregonTrailGame:
    """The runner owns this object; agents receive only observations/actions."""

    def __init__(self, seed: int = 0, max_turns: int = 10):
        if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns <= 0:
            raise ValueError("max_turns must be a positive integer")
        self.max_turns = max_turns
        self.reset(seed)

    def reset(self, seed: int | None = None) -> dict[str, Any]:
        if seed is None:
            seed = 0
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed must be an integer")
        self.rng = random.Random(seed)
        self.state = GameState(seed=seed)
        self.trace: list[dict[str, Any]] = []
        self._step_number = 0
        return self.observe(PLAYER_ID)

    def _check_player(self, player_id: str) -> None:
        if player_id != PLAYER_ID:
            raise ValueError(f"unknown player: {player_id}")

    def observe(self, player_id: str) -> dict[str, Any]:
        self._check_player(player_id)
        s = self.state
        observation = {
            "player": "Oregon Trail traveler",
            "phase": s.phase,
            "turn": s.turn,
            "turn_limit": self.max_turns,
            "miles": round(s.miles, 1),
            "miles_remaining": round(max(0, 2040 - s.miles), 1),
            "stats": {"cash": round(s.cash, 2), "oxen": round(s.oxen, 1),
                      "food": round(s.food, 1), "bullets": round(s.bullets, 1),
                      "clothing": round(s.clothing, 1), "supplies": round(s.supplies, 1)},
            "fort_available": s.fort_available,
            "result": s.last_result,
        }
        if s.phase == "event_response":
            observation["event"] = {"name": s.active_event, "description": s.event_text}
        return observation

    def legal_actions(self, player_id: str) -> list[dict[str, Any]]:
        self._check_player(player_id)
        s = self.state
        if s.status == "terminal":
            return []
        if s.phase == "initial_purchase":
            item = PURCHASE_ITEMS[s.purchase_index]
            minimum = 200 if item == "oxen" else 0
            maximum = 300 if item == "oxen" else max(0, int(s.cash))
            return [{"type": "buy", "item": item, "min": minimum, "max": maximum}]
        if s.phase == "travel":
            actions = [{"type": "continue"}]
            if s.fort_available:
                actions.insert(0, {"type": "visit_fort"})
            if s.bullets >= 40:
                actions.append({"type": "hunt"})
            return actions
        if s.phase == "fort_purchase":
            item = FORT_ITEMS[s.fort_index]
            return [{"type": "buy", "item": item, "min": 0, "max": max(0, int(s.cash))},
                    {"type": "finish_fort"}]
        if s.phase == "shoot":
            return [{"type": "shoot", "word": s.active_event}]
        if s.phase == "ration":
            rations = [(1, "poorly"), (2, "moderately"), (3, "well")]
            if s.food < 13:
                rations = rations[:1]
            elif s.food < 18:
                rations = rations[:1]
            elif s.food < 23:
                rations = rations[:2]
            return [{"type": "eat", "level": level, "name": name}
                    for level, name in rations]
        if s.phase == "event_response":
            if s.active_event == "riders":
                return [{"type": "rider_response", "choice": choice}
                        for choice in ("run", "stand_ground", "circle_wagons")]
        return []

    def step(self, player_id: str, action: Any) -> dict[str, Any]:
        self._check_player(player_id)
        s = self.state
        if s.status == "terminal":
            return {"accepted": False, "message": "episode is terminal"}
        if not isinstance(action, dict) or not isinstance(action.get("type"), str):
            return self._reject(action, "action must be an object with a type")
        before = self._state_snapshot()
        handler = {
            "initial_purchase": self._step_initial_purchase,
            "travel": self._step_travel,
            "fort_purchase": self._step_fort_purchase,
            "shoot": self._step_shoot,
            "ration": self._step_ration,
            "event_response": self._step_event_response,
        }.get(s.phase)
        previous_result = s.last_result
        s.last_result = ""
        message = handler(action) if handler else "no action is available"
        if message is None:
            s.consecutive_invalid = 0
            self._step_number += 1
            record = {"step": self._step_number, "turn": s.turn,
                      "phase": before["phase"], "action": action, "accepted": True,
                      "message": s.last_result, "outcome": self.outcome()}
            self.trace.append(record)
            return {"accepted": True, "message": s.last_result}
        s.last_result = previous_result
        return self._reject(action, message)

    def _reject(self, action: Any, message: str) -> dict[str, Any]:
        self.state.invalid_actions += 1
        self.state.consecutive_invalid += 1
        self._step_number += 1
        if self.state.consecutive_invalid >= 2:
            self._terminal("two consecutive invalid actions")
        self.trace.append({"step": self._step_number, "turn": self.state.turn,
                           "phase": self.state.phase, "action": action,
                           "accepted": False, "message": message,
                           "outcome": self.outcome()})
        return {"accepted": False, "message": message,
                "terminal": self.state.status == "terminal"}

    def _state_snapshot(self) -> dict[str, Any]:
        return asdict(self.state)

    def _step_initial_purchase(self, action: dict[str, Any]) -> str | None:
        s = self.state
        item = PURCHASE_ITEMS[s.purchase_index]
        if action.get("type") != "buy" or action.get("item") != item:
            return f"buy {item} next"
        amount = action.get("amount")
        if not self._valid_amount(amount):
            return "purchase amount must be a nonnegative number"
        if item == "oxen" and not 200 <= amount <= 300:
            return "oxen spending must be between $200 and $300"
        if amount > s.cash:
            return "purchase exceeds available cash"
        self._purchase(item, float(amount))
        s.purchase_index += 1
        s.last_result = f"Purchased {item} for ${amount:.0f}. Remaining cash: ${s.cash:.0f}."
        if s.purchase_index == len(PURCHASE_ITEMS):
            s.phase = "travel"
            s.last_result += " The journey begins."
        return None

    def _step_travel(self, action: dict[str, Any]) -> str | None:
        s = self.state
        kind = action.get("type")
        if kind not in {"visit_fort", "hunt", "continue"}:
            return "action is not legal in the current travel state"
        if kind == "visit_fort" and not s.fort_available:
            return "no fort is available this turn"
        if kind == "hunt" and s.bullets < 40:
            return "you need at least 40 bullets to hunt"
        s.turn += 1
        s.miles += 205 + (s.oxen - 220) / 5
        if kind == "visit_fort" and s.fort_available:
            s.phase = "fort_purchase"
            s.fort_index = 0
            s.miles = max(0, s.miles - 45)
            s.fort_available = False
            s.last_result = "You reached a fort. Time on the trail was lost; choose supplies to buy."
            return None
        if kind == "hunt" and s.bullets >= 40:
            s.phase = "shoot"
            s.fort_available = not s.fort_available
            s.miles = max(0, s.miles - 45)
            s.active_event = self.rng.choice(("BANG", "BLAM", "POW", "WHAM"))
            s.shoot_started_at = time.time()
            s.last_result = f"Hunting costs time. Type {s.active_event} to take your shot."
            return None
        if kind == "continue":
            s.fort_available = not s.fort_available
            s.phase = "ration"
            s.last_result = "You continued along the trail. Choose today's ration."
            return None
        return "action is not legal in the current travel state"

    def _step_fort_purchase(self, action: dict[str, Any]) -> str | None:
        s = self.state
        if action.get("type") == "finish_fort":
            s.phase = "ration"
            s.last_result = "You leave the fort and choose today's ration."
            return None
        item = FORT_ITEMS[s.fort_index]
        if action.get("type") != "buy" or action.get("item") != item:
            return f"buy {item} or finish the fort stop"
        amount = action.get("amount")
        if not self._valid_amount(amount):
            return "purchase amount must be a nonnegative number"
        if amount > s.cash:
            return "purchase exceeds available cash"
        self._purchase(item, float(amount), discount=2 / 3)
        s.fort_index += 1
        s.last_result = f"Purchased {item}; remaining cash: ${s.cash:.0f}."
        if s.fort_index == len(FORT_ITEMS):
            s.phase = "ration"
            s.last_result += " You leave the fort and choose today's ration."
        return None

    @staticmethod
    def _valid_amount(amount: Any) -> bool:
        return isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount >= 0

    def _purchase(self, item: str, cost: float, discount: float = 1.0) -> None:
        field = "bullets" if item == "ammunition" else item
        setattr(self.state, field, getattr(self.state, field) + cost * ITEM_MULTIPLIERS[item] * discount)
        self.state.cash = round(self.state.cash - cost, 2)

    def _step_shoot(self, action: dict[str, Any]) -> str | None:
        s = self.state
        if action.get("type") != "shoot" or not isinstance(action.get("text"), str):
            return "type the displayed word to shoot"
        if s.shoot_started_at is None:
            return "shooting timer was not started"
        reaction = max(0.0, time.time() - s.shoot_started_at)
        target = s.active_event
        if action["text"].strip().upper() == target:
            food = 52 if reaction <= 1.0 else 48
            s.food += food
            s.bullets = max(0, s.bullets - 12)
            s.last_result = f"A clean shot! You added {food} food and used 12 bullets."
        else:
            s.bullets = max(0, s.bullets - 10)
            s.last_result = "The shot missed. You used 10 bullets and gained no food."
        s.active_event = None
        s.shoot_started_at = None
        s.phase = "ration"
        return None

    def _step_ration(self, action: dict[str, Any]) -> str | None:
        s = self.state
        level = action.get("level")
        if (action.get("type") != "eat" or isinstance(level, bool)
                or not isinstance(level, int) or level not in RATION_COSTS):
            return "choose a ration level from 1 to 3"
        cost = RATION_COSTS[level]
        if s.food < 13:
            if level != 1 or s.food <= 0:
                return "choose a poor ration to use the remaining food"
            cost = s.food
        elif s.food < cost:
            return "not enough food for that ration"
        s.food -= cost
        ration_message = f"You ate {cost:g} food. "
        s.last_result = ration_message
        self._resolve_event()
        if s.status != "terminal":
            if s.food <= 0:
                self._terminal("lost on the trail")
            elif s.phase == "event_response":
                pass
            elif s.miles >= 2040:
                s.miles = 2040
                self._terminal("arrived at Oregon City")
            elif s.turn >= self.max_turns:
                self._terminal(self._turn_limit_reason())
            else:
                s.phase = "travel"
        return None

    def _resolve_event(self) -> None:
        s = self.state
        event = self.rng.choices(("clear", "helpful", "rain", "breakdown", "riders"),
                                 weights=(30, 15, 20, 20, 15), k=1)[0]
        if event == "clear":
            s.last_result += "The weather stayed clear."
        elif event == "helpful":
            s.food += 14
            s.last_result += "A guide showed you a hunting ground; you found 14 food."
        elif event == "rain":
            s.food = max(0, s.food - 10)
            s.supplies = max(0, s.supplies - 2)
            s.miles = max(0, s.miles - 10)
            s.last_result += "Heavy rain damaged food and supplies and delayed the wagon."
        elif event == "breakdown":
            s.supplies = max(0, s.supplies - 5)
            s.miles = max(0, s.miles - 15)
            s.last_result += "A wagon part broke; repairs used 5 supplies and cost time."
        else:
            s.active_event = "riders"
            s.event_text = "Riders approach. Choose how to respond."
            s.phase = "event_response"

    def _step_event_response(self, action: dict[str, Any]) -> str | None:
        s = self.state
        if action.get("type") != "rider_response" or action.get("choice") not in {
            "run", "stand_ground", "circle_wagons"
        }:
            return "choose run, stand_ground, or circle_wagons"
        choice = action["choice"]
        if choice == "run":
            s.miles = max(0, s.miles - 15)
            s.oxen = max(0, s.oxen - 10)
            s.last_result = "You ran from the riders, losing time and some oxen."
        elif choice == "stand_ground":
            s.bullets = max(0, s.bullets - 25)
            s.last_result = "You stood your ground and spent 25 bullets."
        else:
            s.supplies = max(0, s.supplies - 3)
            s.miles = max(0, s.miles - 10)
            s.last_result = "You circled the wagons, using supplies and time."
        s.active_event = None
        s.event_text = None
        if s.miles >= 2040:
            self._terminal("arrived at Oregon City")
        elif s.turn >= self.max_turns:
            self._terminal(self._turn_limit_reason())
        else:
            s.phase = "travel"
        return None

    def _terminal(self, reason: str) -> None:
        s = self.state
        s.status = "terminal"
        s.reason = reason
        s.score = round(max(0, min(1, s.miles / 2040)), 3)
        s.phase = "terminal"

    def _turn_limit_reason(self) -> str:
        return f"travel-turn limit ({self.max_turns} turns)"

    def end_episode(self, reason: str) -> None:
        """Runner-enforced budget termination, recorded as an explicit outcome."""
        if self.state.status != "terminal":
            self._terminal(reason)

    def record_model_call(self, *, success: bool, input_tokens: int = 0,
                          output_tokens: int = 0) -> None:
        self.state.model_calls += 1
        if not success:
            self.state.failed_model_calls += 1
        self.state.input_tokens += max(0, int(input_tokens))
        self.state.output_tokens += max(0, int(output_tokens))

    def record_runtime(self, seconds: float) -> None:
        self.state.elapsed_seconds = max(self.state.elapsed_seconds, float(seconds))

    def outcome(self) -> dict[str, Any]:
        return {"status": self.state.status, "reason": self.state.reason,
                "score": self.state.score, "turn": self.state.turn,
                "miles": round(self.state.miles, 1),
                "steps": self._step_number, "invalid_actions": self.state.invalid_actions,
                "model_calls": self.state.model_calls,
                "failed_model_calls": self.state.failed_model_calls}

    def save_state(self, path: str | Path) -> None:
        payload = {"version": SAVE_VERSION, "max_turns": self.max_turns,
                   "state": asdict(self.state), "rng_state": self.rng.getstate(),
                   "trace": self.trace, "step_number": self._step_number}
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load_state(cls, path: str | Path) -> "OregonTrailGame":
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            if payload.get("version") != SAVE_VERSION:
                raise ValueError("unsupported save version")
            state_data = payload["state"]
            state = GameState(**state_data)
            max_turns = int(payload["max_turns"])
            if state.phase not in {"initial_purchase", "travel", "fort_purchase", "shoot",
                                   "ration", "event_response", "terminal"}:
                raise ValueError("invalid saved phase")
            if max_turns <= 0 or state.turn < 0 or state.turn > max_turns:
                raise ValueError("invalid saved turn limit")
            if (min(state.cash, state.oxen, state.food, state.bullets, state.clothing,
                    state.supplies, state.miles, state.elapsed_seconds) < 0):
                raise ValueError("invalid saved resource or turn value")
            if not 0 <= state.purchase_index <= len(PURCHASE_ITEMS):
                raise ValueError("invalid saved purchase index")
            if (state.phase == "initial_purchase"
                    and state.purchase_index >= len(PURCHASE_ITEMS)):
                raise ValueError("invalid saved purchase index for purchase phase")
            if (state.phase not in {"initial_purchase", "terminal"}
                    and state.purchase_index != len(PURCHASE_ITEMS)):
                raise ValueError("incomplete saved purchases after purchase phase")
            if not 0 <= state.fort_index <= len(FORT_ITEMS):
                raise ValueError("invalid saved fort index")
            if (state.phase == "fort_purchase"
                    and state.fort_index >= len(FORT_ITEMS)):
                raise ValueError("invalid saved fort index for fort purchase phase")
            if state.status not in {"ongoing", "terminal"}:
                raise ValueError("invalid saved outcome status")
            if (state.phase == "terminal") != (state.status == "terminal"):
                raise ValueError("saved phase and status are inconsistent")
            if (state.shoot_started_at is not None
                    and not isinstance(state.shoot_started_at, (int, float))):
                raise ValueError("invalid saved shooting timer")
            if min(state.invalid_actions, state.model_calls, state.failed_model_calls,
                   state.input_tokens, state.output_tokens) < 0:
                raise ValueError("invalid saved counter")
            game = cls(seed=state.seed, max_turns=max_turns)
            game.state = state
            if state.phase == "shoot":
                game.state.shoot_started_at = time.time()
            game.rng.setstate(_tuplify(payload["rng_state"]))
            game.trace = payload.get("trace", [])
            game._step_number = int(payload.get("step_number", len(game.trace)))
            return game
        except (KeyError, TypeError, json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"invalid save file: {exc}") from exc


def _tuplify(value: Any) -> Any:
    return tuple(_tuplify(item) for item in value) if isinstance(value, list) else value
