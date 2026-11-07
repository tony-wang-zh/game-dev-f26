"""Terminal game UI; rules and state transitions remain in game.py."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import questionary

from game import OregonTrailGame, PLAYER_ID, GAME_VERSION
from heuristic_player import HeuristicPlayer
from trace_log import TraceLog
from vertex_player import VertexPlayer

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "agent_config.json"


def _clear() -> None:
    print("\n" + "─" * 68)


def show_observation(observation: dict) -> None:
    _clear()
    print(f"Oregon Trail  |  Turn {observation['turn']} of {observation['turn_limit']}  |  {observation['miles']:.0f} miles")
    labels = {"cash": "Cash", "oxen": "Oxen", "food": "Food", "bullets": "Bullets",
              "clothing": "Clothing", "supplies": "Misc"}
    print("Stats: " + "  ".join(f"{labels[name]} {value:g}"
                               for name, value in observation["stats"].items()))
    if observation.get("result"):
        print(observation["result"])
    if observation.get("event"):
        print(f"\nTrail event: {observation['event']['description']}")


def _choose_action(observation: dict, legal_actions: list[dict]) -> dict | str:
    phase = observation["phase"]
    if phase in {"initial_purchase", "fort_purchase"}:
        action = legal_actions[0]
        controls = ["Continue purchase", "Ask heuristic for this move",
                    "Ask Vertex for this move", "Let heuristic play to the end",
                    "Let Vertex play to the end", "Save game", "Quit"]
        control = questionary.select("Purchase controls", choices=controls,
                                     use_arrow_keys=True).ask()
        if control == "Quit" or control is None:
            return "quit"
        if control == "Save game":
            save_path = questionary.text("Save file", default="game_saves/oregon-trail-save.json").ask()
            if not save_path:
                return "save_cancelled"
            return {"type": "__save__", "path": save_path}
        if control and control.startswith(("Ask ", "Let ")):
            who = "heuristic" if "heuristic" in control.lower() else "vertex"
            return {"type": "__delegate__", "player": who,
                    "persistent": control.startswith("Let ")}
        if len(legal_actions) > 1:
            labels = [f"Buy {action['item']}", "Finish fort stop"]
            selected = questionary.select("Choose an option", choices=labels, use_arrow_keys=True).ask()
            if selected is None:
                return "quit"
            if selected == labels[1]:
                return next(a for a in legal_actions if a["type"] == "finish_fort")
        item = action["item"]
        cap = observation["stats"]["cash"]
        minimum = action.get("min", 0)
        while True:
            answer = questionary.text(
                f"How much to spend on {item}? Available ${cap:.0f}; stats update after each purchase",
                default=str(minimum if minimum else 0),
            ).ask()
            if answer is None:
                return "quit"
            try:
                amount = float(answer)
            except ValueError:
                print("Enter a number.")
                continue
            return {"type": "buy", "item": item, "amount": amount}
    if phase == "shoot":
        word = legal_actions[0]["word"]
        print(f"Type the word quickly: {word} (or enter :save / :control)")
        answer = input("> ")
        if answer.strip().lower() == ":save":
            path = questionary.text("Save file", default="game_saves/oregon-trail-save.json").ask()
            return {"type": "__save__", "path": path} if path else "save_cancelled"
        if answer.strip().lower() == ":control":
            choices = ["Ask heuristic for this move", "Ask Vertex for this move",
                       "Let heuristic play to the end", "Let Vertex play to the end"]
            selected = questionary.select("Choose control", choices=choices,
                                          use_arrow_keys=True).ask()
            if not selected:
                return "save_cancelled"
            who = "heuristic" if "heuristic" in selected.lower() else "vertex"
            return {"type": "__delegate__", "player": who,
                    "persistent": selected.startswith("Let ")}
        return {"type": "shoot", "text": answer}
    labels = []
    for action in legal_actions:
        if action["type"] == "eat":
            labels.append(f"Eat {action['name']} ({action['level']})")
        elif action["type"] == "rider_response":
            labels.append(action["choice"].replace("_", " ").title())
        else:
            labels.append(action["type"].replace("_", " ").title())
    options = labels + ["Ask heuristic for this move", "Ask Vertex for this move",
                        "Let heuristic play to the end", "Let Vertex play to the end",
                        "Save game", "Quit"]
    selected = questionary.select("Choose your action", choices=options, use_arrow_keys=True).ask()
    if selected is None or selected == "Quit":
        return "quit"
    if selected == "Save game":
        save_path = questionary.text("Save file", default="game_saves/oregon-trail-save.json").ask()
        if not save_path:
            return "save_cancelled"
        return {"type": "__save__", "path": save_path}
    if selected.startswith(("Ask ", "Let ")):
        who = "heuristic" if "heuristic" in selected.lower() else "vertex"
        return {"type": "__delegate__", "player": who,
                "persistent": selected.startswith("Let ")}
    index = labels.index(selected)
    action = dict(legal_actions[index])
    if action["type"] == "shoot":
        print(f"Type the word quickly: {action['word']}")
        answer = input("> ")
        return {"type": "shoot", "text": answer}
    return action


def _make_trace_action(player, observation, legal, deadline, max_calls):
    if player.name == "heuristic":
        action = player.choose(observation, legal)
        metadata = {"kind": "heuristic", "elapsed_seconds": 0.0}
        return action, metadata
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("episode time limit")
    if player.call_count >= max_calls:
        raise RuntimeError("model-call limit")
    action, metadata = player.choose(observation, legal,
                                    timeout_seconds=min(player.timeout_seconds, remaining))
    return action, metadata


def run(args: argparse.Namespace) -> int:
    game = OregonTrailGame(seed=args.seed)
    if args.load:
        game = OregonTrailGame.load_state(args.load)
    mode = args.player
    if mode == "choose":
        mode = questionary.select("Who controls the game?", choices=["Human", "Heuristic player", "Vertex AI player"], use_arrow_keys=True).ask()
        mode = {"Human": "human", "Heuristic player": "heuristic", "Vertex AI player": "vertex"}.get(mode, "human")
    player = HeuristicPlayer() if mode == "heuristic" else None
    vertex = None

    def make_vertex():
        settings = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        client = VertexPlayer(ROOT / settings["model_config_path"],
                              ROOT / settings["player_prompt"],
                              timeout_seconds=settings["per_call_timeout_seconds"])
        client._connect()
        return client

    if mode == "vertex":
        try:
            vertex = make_vertex()
        except Exception as exc:
            print(f"Vertex setup failed: {exc}")
            print("Authenticate with `gcloud auth application-default login` and launch again.")
            return 2
        vertex.call_count = game.state.model_calls
        vertex.call_failures = game.state.failed_model_calls
        vertex.input_tokens = game.state.input_tokens
        vertex.output_tokens = game.state.output_tokens
        player = vertex
    trace = TraceLog(mode, ROOT / "traces", GAME_VERSION)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    episode_start = time.monotonic()
    time_limit = min(args.episode_seconds, config["max_episode_seconds"])
    saved_elapsed = game.state.elapsed_seconds
    deadline = episode_start + max(0, time_limit - saved_elapsed)
    autosave_path = ROOT / "game_saves" / "autosave.json"

    def autosave() -> None:
        autosave_path.parent.mkdir(parents=True, exist_ok=True)
        game.record_runtime(saved_elapsed + time.monotonic() - episode_start)
        game.save_state(autosave_path)

    autosave()
    while game.outcome()["status"] == "ongoing":
        observation = game.observe(PLAYER_ID)
        legal = game.legal_actions(PLAYER_ID)
        show_observation(observation)
        if time.monotonic() >= deadline:
            game.end_episode("episode time limit")
            trace.add({"player": mode, "observation": observation, "legal_actions": legal,
                       "action": None, "accepted": False, "error": "episode time limit"})
            break
        if mode == "human":
            action = _choose_action(observation, legal)
            metadata = {"kind": "human"}
            if action == "quit":
                break
            if action == "save_cancelled":
                continue
            if isinstance(action, dict) and action.get("type") == "__save__":
                path = ROOT / action["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                game.record_runtime(saved_elapsed + time.monotonic() - episode_start)
                game.save_state(path)
                print(f"Saved game to {path.relative_to(ROOT)}")
                continue
            if isinstance(action, dict) and action.get("type") == "__delegate__":
                delegated_mode = action["player"]
                delegated_player = HeuristicPlayer() if delegated_mode == "heuristic" else None
                if delegated_mode == "vertex":
                    try:
                        vertex = make_vertex()
                        delegated_player = vertex
                    except Exception as exc:
                        print(f"Vertex setup failed: {exc}")
                        print("Authenticate with `gcloud auth application-default login` and retry.")
                        continue
                    delegated_player.call_count = game.state.model_calls
                    delegated_player.call_failures = game.state.failed_model_calls
                    delegated_player.input_tokens = game.state.input_tokens
                    delegated_player.output_tokens = game.state.output_tokens
                if action.get("persistent"):
                    mode = delegated_mode
                    player = delegated_player
                    if mode == "vertex":
                        vertex = delegated_player
                    continue
                try:
                    calls_before = getattr(delegated_player, "call_count", 0)
                    action, metadata = _make_trace_action(
                        delegated_player, observation, legal, deadline,
                        config["max_calls_per_episode"],
                    )
                    if delegated_mode == "vertex" and delegated_player.call_count > calls_before:
                        game.record_model_call(success=True,
                                               input_tokens=metadata.get("input_tokens", 0),
                                               output_tokens=metadata.get("output_tokens", 0))
                    result = game.step(PLAYER_ID, action)
                    autosave()
                    trace.add({"player": delegated_mode, "observation": observation,
                               "legal_actions": legal, "action": action,
                               "accepted": result["accepted"], "result": result,
                               "model": metadata})
                    if not result["accepted"]:
                        print(f"Action refused: {result['message']}")
                except Exception as exc:
                    if (delegated_mode == "vertex" and delegated_player
                            and delegated_player.call_count > game.state.model_calls):
                        game.record_model_call(success=False)
                    trace.add({"player": delegated_mode, "observation": observation,
                               "legal_actions": legal, "action": None,
                               "accepted": False, "error": f"{type(exc).__name__}: {exc}"})
                    autosave()
                    print(f"Player call failed: {exc}")
                if delegated_mode == "vertex" and delegated_player:
                    delegated_player.close()
                continue
        else:
            calls_before = getattr(player, "call_count", 0)
            try:
                action, metadata = _make_trace_action(player, observation, legal, deadline,
                                                      config["max_calls_per_episode"])
                if mode == "vertex" and player.call_count > calls_before:
                    game.record_model_call(success=True,
                                           input_tokens=metadata.get("input_tokens", 0),
                                           output_tokens=metadata.get("output_tokens", 0))
            except Exception as exc:
                if mode == "vertex" and player.call_count > calls_before:
                    game.record_model_call(success=False)
                player_name = player.name
                if isinstance(exc, (TimeoutError,)) and str(exc) == "episode time limit":
                    game.end_episode("episode time limit")
                    break
                if str(exc) in {"model-call limit", "episode time limit"}:
                    game.end_episode(str(exc))
                    break
                trace.add({"player": player_name, "observation": observation,
                           "legal_actions": legal, "action": None, "accepted": False,
                           "error": f"{type(exc).__name__}: {exc}",
                           "model_call_count": getattr(player, "call_count", 0)})
                autosave()
                print(f"Player call failed: {exc}; failed calls still count toward its budget.")
                game.end_episode("model call failed")
                break
        result = game.step(PLAYER_ID, action)
        autosave()
        trace.add({"player": mode, "observation": observation, "legal_actions": legal,
                   "action": action, "accepted": result["accepted"],
                   "result": result, "model": metadata})
        if not result["accepted"]:
            print(f"Action refused: {result['message']}")
    outcome = game.outcome()
    total_elapsed = saved_elapsed + time.monotonic() - episode_start
    game.record_runtime(total_elapsed)
    game.save_state(autosave_path)
    metrics = {"elapsed_seconds": round(total_elapsed, 3),
               "seed": game.state.seed, "model_calls": game.state.model_calls,
               "failed_model_calls": game.state.failed_model_calls,
               "input_tokens": game.state.input_tokens,
               "output_tokens": game.state.output_tokens,
               "model": getattr(player, "model", None)}
    trace.finish(outcome, metrics)
    print(f"\nEpisode: {outcome['status']} — {outcome['reason'] or 'stopped by player'}; score {outcome['score']}")
    if game.state.last_result:
        print(game.state.last_result)
    print(f"Trace: {trace.path.relative_to(ROOT)}")
    if vertex:
        vertex.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Play the bounded Oregon Trail episode")
    parser.add_argument("--player", choices=("choose", "human", "heuristic", "vertex"), default="choose")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--load", help="load a human-readable game save")
    parser.add_argument("--episode-seconds", type=int, default=300)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
