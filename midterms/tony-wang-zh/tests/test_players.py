import json
from types import SimpleNamespace
import unittest

from game import OregonTrailGame, PLAYER_ID
from heuristic_player import HeuristicPlayer
from vertex_player import VertexPlayer


class FakeModels:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.kwargs = None

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


class PlayerTests(unittest.TestCase):
    def test_heuristic_uses_only_observation_and_legal_actions(self):
        game = OregonTrailGame(seed=2)
        player = HeuristicPlayer()
        action = player.choose(game.observe(PLAYER_ID), game.legal_actions(PLAYER_ID))
        self.assertEqual(action, {"type": "buy", "item": "oxen", "amount": 250})

    def test_heuristic_chooses_a_legal_ration_when_food_is_low(self):
        game = OregonTrailGame(seed=2)
        game.state.phase = "ration"
        game.state.food = 15
        observation = game.observe(PLAYER_ID)
        legal_actions = game.legal_actions(PLAYER_ID)
        action = HeuristicPlayer().choose(observation, legal_actions)
        self.assertIn(action, legal_actions)
        self.assertEqual(action["level"], 1)
        self.assertTrue(game.step(PLAYER_ID, action)["accepted"])

    def test_vertex_prompt_contains_only_observation_and_legal_action_boundary(self):
        response = SimpleNamespace(text='{"type":"buy","item":"oxen","amount":250}',
                                   usage_metadata=SimpleNamespace(prompt_token_count=12,
                                                                  candidates_token_count=8))
        player = VertexPlayer("unused", "unused")
        player.client = SimpleNamespace(models=FakeModels(response=response))
        player.model = "test-model"
        obs = {"phase": "initial_purchase", "stats": {"cash": 700}}
        legal = [{"type": "buy", "item": "oxen", "min": 200, "max": 300}]
        action, metrics = player.choose(obs, legal)
        request = player.client.models.kwargs
        self.assertEqual(action, {"type": "buy", "item": "oxen", "amount": 250})
        self.assertEqual(json.loads(request["contents"]),
                         {"observation": obs, "legal_actions": legal})
        self.assertEqual(metrics["input_tokens"], 12)
        self.assertEqual(player.call_count, 1)

    def test_vertex_failed_call_is_counted_and_not_fallback_action(self):
        player = VertexPlayer("unused", "unused")
        player.client = SimpleNamespace(models=FakeModels(error=TimeoutError("late")))
        player.model = "test-model"
        with self.assertRaises(TimeoutError):
            player.choose({"phase": "travel"}, [{"type": "continue"}])
        self.assertEqual(player.call_count, 1)
        self.assertEqual(player.call_failures, 1)


if __name__ == "__main__":
    unittest.main()
