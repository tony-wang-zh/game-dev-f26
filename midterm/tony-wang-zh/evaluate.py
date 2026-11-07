"""Reproducible baseline and live Vertex evaluation runner."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time

from game import OregonTrailGame, PLAYER_ID, GAME_VERSION
from heuristic_player import HeuristicPlayer
from trace_log import TraceLog
from vertex_player import VertexPlayer

ROOT = Path(__file__).resolve().parent


def _episode(player, seed: int, limits: dict, live: bool,
             trace_directory: Path | None = None) -> dict:
    game = OregonTrailGame(seed=seed, max_turns=limits["step_limit_travel_turns"])
    trace = TraceLog(player.name, trace_directory or ROOT / "traces", GAME_VERSION)
    started = time.monotonic()
    deadline = started + limits["episode_time_limit_seconds"]
    failure = None
    while game.outcome()["status"] == "ongoing":
        observation = game.observe(PLAYER_ID)
        legal = game.legal_actions(PLAYER_ID)
        if time.monotonic() >= deadline:
            game.end_episode("episode time limit")
            break
        metadata = {}
        try:
            if player.name == "heuristic":
                action = player.choose(observation, legal)
            else:
                if player.call_count >= limits["model_call_limit_per_episode"]:
                    game.end_episode("model-call limit")
                    break
                action, metadata = player.choose(
                    observation, legal,
                    timeout_seconds=min(player.timeout_seconds, deadline - time.monotonic()),
                )
                game.record_model_call(success=True,
                                       input_tokens=metadata.get("input_tokens", 0),
                                       output_tokens=metadata.get("output_tokens", 0))
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
            if player.name == "vertex" and player.call_count > game.state.model_calls:
                game.record_model_call(success=False)
            trace.add({"observation": observation, "legal_actions": legal,
                       "action": None, "accepted": False, "error": failure,
                       "model_call_count": getattr(player, "call_count", 0)})
            game.end_episode("model call failed")
            break
        result = game.step(PLAYER_ID, action)
        trace.add({"observation": observation, "legal_actions": legal,
                   "action": action, "accepted": result["accepted"],
                   "result": result, "model": metadata})
    elapsed = time.monotonic() - started
    game.record_runtime(elapsed)
    outcome = game.outcome()
    seconds = getattr(player, "call_seconds", [])
    metrics = {
        "seed": seed,
        "elapsed_seconds": round(elapsed, 3),
        "model_calls": getattr(player, "call_count", 0),
        "failed_model_calls": getattr(player, "call_failures", 0),
        "input_tokens": getattr(player, "input_tokens", 0),
        "output_tokens": getattr(player, "output_tokens", 0),
        "mean_call_latency_seconds": round(statistics.fmean(seconds), 3) if seconds else None,
        "max_call_latency_seconds": round(max(seconds), 3) if seconds else None,
        "failure": failure,
    }
    trace.finish(outcome, metrics)
    try:
        trace_reference = trace.path.relative_to(ROOT).as_posix()
    except ValueError:
        trace_reference = str(trace.path)
    return {"outcome": outcome, "metrics": metrics, "trace": trace_reference}


def run_suite(live: bool, include_held_out: bool = False,
              held_out_only: bool = False) -> dict:
    suite = json.loads((ROOT / "evaluation_suite.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "agent_config.json").read_text(encoding="utf-8"))
    limits = {
        "step_limit_travel_turns": suite["step_limit_travel_turns"],
        "model_call_limit_per_episode": suite["model_call_limit_per_episode"],
        "episode_time_limit_seconds": suite["episode_time_limit_seconds"],
    }
    cases = list(suite["held_out"] if held_out_only else suite["situations"])
    if include_held_out and not held_out_only:
        cases.extend(suite["held_out"])
    runs = []
    player_names = ["heuristic"] + (["vertex"] if live else [])
    for case in cases:
        for trial in range(1, suite["trials_per_situation"] + 1):
            for player_name in player_names:
                if player_name == "heuristic":
                    player = HeuristicPlayer()
                else:
                    player = VertexPlayer(
                        ROOT / config["model_config_path"], ROOT / config["player_prompt"],
                        timeout_seconds=config["per_call_timeout_seconds"],
                    )
                    try:
                        player._connect()
                        player.call_count = 0
                    except Exception as exc:
                        row = {"case": case["id"], "trial": trial, "player": player_name,
                               "seed": case["seed"], "failure": f"{type(exc).__name__}: {exc}",
                               "outcome": {"status": "not_run", "reason": "provider unavailable"},
                               "metrics": {}, "trace": None}
                        runs.append(row)
                        print(f"{case['id']} trial {trial}: Vertex setup failed ({exc})")
                        continue
                result = _episode(player, case["seed"], limits, live and player_name == "vertex")
                runs.append({"case": case["id"], "trial": trial, "player": player_name,
                             "seed": case["seed"], **result})
                if hasattr(player, "close"):
                    player.close()
                print(f"{case['id']} trial {trial} {player_name}: "
                      f"{result['outcome']['status']} ({result['outcome']['reason']})")
    pricing = json.loads((ROOT / "pricing.json").read_text(encoding="utf-8"))
    for row in runs:
        m = row.get("metrics", {})
        m["estimated_cost_usd"] = round(
            m.get("input_tokens", 0) * pricing["input_usd_per_million_tokens"] / 1_000_000
            + m.get("output_tokens", 0) * pricing["output_usd_per_million_tokens"] / 1_000_000,
            8,
        )
    report = {"run_at": datetime.now(timezone.utc).isoformat(),
              "game_version": GAME_VERSION,
              "suite_declared_at": suite["declared_at"],
              "model": json.loads((ROOT / "google_cloud_info.json").read_text(encoding="utf-8"))["model"] if live else None,
              "pricing": pricing, "runs": runs}
    output_dir = ROOT / "evaluation_runs"
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"evaluation-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nEvaluation results: {path.relative_to(ROOT)}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the declared Oregon Trail suite")
    parser.add_argument("--live", action="store_true", help="make live Vertex calls and incur token charges")
    parser.add_argument("--include-held-out", action="store_true", help="run the reserved case after tuning")
    parser.add_argument("--held-out-only", action="store_true", help="run only the reserved case")
    args = parser.parse_args()
    if not args.live:
        print("Running heuristic baseline only. Pass --live for Vertex model trials.")
    if args.held_out_only and args.include_held_out:
        parser.error("use only one held-out option")
    run_suite(live=args.live, include_held_out=args.include_held_out,
              held_out_only=args.held_out_only)


if __name__ == "__main__":
    main()
