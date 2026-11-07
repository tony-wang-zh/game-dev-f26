import tempfile
import unittest
from pathlib import Path

from evaluate import _episode
from game import GAME_VERSION
from heuristic_player import HeuristicPlayer


class ReplayedVertexPlayer:
    """Deterministic response replay that exercises the real episode runner."""

    name = "vertex"

    def __init__(self):
        self.policy = HeuristicPlayer()
        self.call_count = 0
        self.call_failures = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.call_seconds = []
        self.timeout_seconds = 35.0

    def choose(self, observation, legal_actions, timeout_seconds=None):
        self.call_count += 1
        self.call_seconds.append(0.001)
        return self.policy.choose(observation, legal_actions), {
            "elapsed_seconds": 0.001, "input_tokens": 10,
            "output_tokens": 3, "model": "replayed-response",
        }


class EvaluationIntegrationTests(unittest.TestCase):
    def test_replayed_model_actions_reach_engine_terminal_outcome(self):
        player = ReplayedVertexPlayer()
        limits = {"step_limit_travel_turns": 10,
                  "model_call_limit_per_episode": 80,
                  "episode_time_limit_seconds": 300}
        with tempfile.TemporaryDirectory() as tmp:
            result = _episode(player, seed=1, limits=limits, live=True,
                              trace_directory=Path(tmp))
            self.assertEqual(result["outcome"]["reason"], "arrived at Oregon City")
            self.assertEqual(result["outcome"]["model_calls"], player.call_count)
            self.assertEqual(result["outcome"]["invalid_actions"], 0)
            self.assertTrue(Path(tmp, Path(result["trace"]).name).exists())
            self.assertEqual(player.call_count, 25)

    def test_model_call_limit_ends_the_episode_without_fallback(self):
        player = ReplayedVertexPlayer()
        limits = {"step_limit_travel_turns": 10,
                  "model_call_limit_per_episode": 1,
                  "episode_time_limit_seconds": 300}
        with tempfile.TemporaryDirectory() as tmp:
            result = _episode(player, seed=1, limits=limits, live=True,
                              trace_directory=Path(tmp))
        self.assertEqual(result["outcome"]["reason"], "model-call limit")
        self.assertEqual(result["outcome"]["model_calls"], 1)
        self.assertEqual(player.call_count, 1)

    def test_episode_time_limit_is_enforced_before_a_player_call(self):
        player = ReplayedVertexPlayer()
        limits = {"step_limit_travel_turns": 10,
                  "model_call_limit_per_episode": 80,
                  "episode_time_limit_seconds": 0}
        with tempfile.TemporaryDirectory() as tmp:
            result = _episode(player, seed=1, limits=limits, live=True,
                              trace_directory=Path(tmp))
        self.assertEqual(result["outcome"]["reason"], "episode time limit")
        self.assertEqual(result["outcome"]["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
