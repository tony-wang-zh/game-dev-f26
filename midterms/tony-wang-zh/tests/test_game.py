import json
import tempfile
import time
import unittest
from pathlib import Path

from game import FORT_ITEMS, OregonTrailGame, PLAYER_ID


def start_game(game):
    # Deliberately economical starting allocations, all inside the $700 budget.
    for item, amount in (
        ("oxen", 250), ("food", 250), ("ammunition", 60),
        ("clothing", 60), ("supplies", 60),
    ):
        result = game.step(PLAYER_ID, {"type": "buy", "item": item, "amount": amount})
        assert result["accepted"], result


class OregonTrailGameTests(unittest.TestCase):
    def test_purchases_update_visible_stats_immediately(self):
        game = OregonTrailGame(seed=12)
        before = game.observe(PLAYER_ID)
        result = game.step(PLAYER_ID, {"type": "buy", "item": "oxen", "amount": 250})
        after = game.observe(PLAYER_ID)
        self.assertTrue(result["accepted"])
        self.assertEqual(before["stats"]["cash"] - after["stats"]["cash"], 250)
        self.assertEqual(after["stats"]["oxen"], 250)
        self.assertEqual(after["phase"], "initial_purchase")

    def test_fort_purchase_is_charged_once_and_visible_at_once(self):
        game = OregonTrailGame(seed=12)
        start_game(game)
        game.state.cash = 100
        game.step(PLAYER_ID, {"type": "visit_fort"})
        before = game.observe(PLAYER_ID)
        result = game.step(PLAYER_ID, {"type": "buy", "item": "food", "amount": 10})
        after = game.observe(PLAYER_ID)
        self.assertTrue(result["accepted"])
        self.assertEqual(after["stats"]["cash"], before["stats"]["cash"] - 10)
        self.assertAlmostEqual(after["stats"]["food"] - before["stats"]["food"], 10 * 2 / 3, delta=0.05)

    def test_purchase_cannot_exceed_cash_and_rejection_is_immutable(self):
        game = OregonTrailGame(seed=12)
        before = game.observe(PLAYER_ID)
        result = game.step(PLAYER_ID, {"type": "buy", "item": "oxen", "amount": 701})
        self.assertFalse(result["accepted"])
        self.assertEqual(game.observe(PLAYER_ID), before)
        self.assertEqual(game.outcome()["invalid_actions"], 1)

    def test_initial_purchase_minimum_and_budget_are_enforced(self):
        game = OregonTrailGame(seed=12)
        self.assertFalse(game.step(PLAYER_ID, {"type": "buy", "item": "oxen", "amount": 199})["accepted"])
        start_game(game)
        self.assertEqual(game.observe(PLAYER_ID)["phase"], "travel")
        self.assertLessEqual(game.state.cash, 700)

    def test_episode_has_ten_travel_turns_and_terminal_reason(self):
        game = OregonTrailGame(seed=1)
        start_game(game)
        for _ in range(10):
            if game.outcome()["status"] == "terminal":
                break
            if game.observe(PLAYER_ID)["phase"] == "travel":
                game.step(PLAYER_ID, {"type": "continue"})
            if game.observe(PLAYER_ID)["phase"] == "ration":
                game.step(PLAYER_ID, {"type": "eat", "level": 2})
            if game.observe(PLAYER_ID)["phase"] == "event_response":
                legal = game.legal_actions(PLAYER_ID)
                game.step(PLAYER_ID, legal[0])
        self.assertLessEqual(game.outcome()["turn"], 10)
        self.assertEqual(game.outcome()["status"], "terminal")
        self.assertIn(game.outcome()["reason"], {
            "arrived at Oregon City", "lost on the trail", "travel-turn limit (10 turns)"
        })

    def test_custom_turn_limit_is_named_in_terminal_reason(self):
        game = OregonTrailGame(seed=1, max_turns=2)
        start_game(game)
        for _ in range(2):
            game.step(PLAYER_ID, {"type": "continue"})
            game.step(PLAYER_ID, {"type": "eat", "level": 2})
        self.assertEqual(game.outcome()["reason"], "travel-turn limit (2 turns)")

        rider_game = OregonTrailGame(seed=1, max_turns=2)
        rider_game.state.phase = "event_response"
        rider_game.state.turn = 2
        rider_game.state.miles = 400
        rider_game.state.active_event = "riders"
        self.assertTrue(rider_game.step(PLAYER_ID, {
            "type": "rider_response", "choice": "stand_ground"
        })["accepted"])
        self.assertEqual(rider_game.outcome()["reason"], "travel-turn limit (2 turns)")

    def test_heuristic_acceptance_trace_reaches_oregon_city(self):
        from heuristic_player import HeuristicPlayer

        game = OregonTrailGame(seed=1)
        player = HeuristicPlayer()
        while game.outcome()["status"] == "ongoing":
            observation = game.observe(PLAYER_ID)
            action = player.choose(observation, game.legal_actions(PLAYER_ID))
            self.assertIn(action.get("type"), {a["type"] for a in game.legal_actions(PLAYER_ID)})
            game.step(PLAYER_ID, action)
        self.assertEqual(game.outcome()["reason"], "arrived at Oregon City")
        self.assertEqual(game.outcome()["score"], 1)

    def test_reset_seed_replays_same_initial_observation(self):
        game = OregonTrailGame(seed=1)
        first = game.observe(PLAYER_ID)
        game.reset(seed=91)
        game.reset(seed=1)
        self.assertEqual(game.observe(PLAYER_ID), first)
        self.assertEqual(game.state.seed, 1)

    def test_unknown_and_unavailable_actions_do_not_change_state(self):
        game = OregonTrailGame(seed=4)
        start_game(game)
        game.state.bullets = 0
        before = game.observe(PLAYER_ID)
        result = game.step(PLAYER_ID, {"type": "hunt"})
        self.assertFalse(result["accepted"])
        self.assertEqual(game.observe(PLAYER_ID), before)
        self.assertNotIn({"type": "hunt"}, game.legal_actions(PLAYER_ID))

    def test_continue_advances_expected_miles_for_starting_oxen_quality(self):
        game = OregonTrailGame(seed=4)
        start_game(game)
        result = game.step(PLAYER_ID, {"type": "continue"})
        self.assertTrue(result["accepted"])
        self.assertEqual(game.observe(PLAYER_ID)["miles"], 211)

    def test_two_consecutive_invalid_actions_end_agent_episode(self):
        game = OregonTrailGame(seed=4)
        game.step(PLAYER_ID, {"type": "bogus"})
        game.step(PLAYER_ID, {"type": "bogus"})
        self.assertEqual(game.outcome()["status"], "terminal")
        self.assertEqual(game.outcome()["reason"], "two consecutive invalid actions")
        self.assertEqual(game.outcome()["invalid_actions"], 2)

    def test_failure_score_preserves_partial_trip_progress(self):
        game = OregonTrailGame(seed=4)
        game.state.miles = 1020
        game.end_episode("test limit")
        self.assertEqual(game.outcome()["score"], 0.5)

    def test_shooting_typing_minigame_rewards_accuracy_and_speed(self):
        game = OregonTrailGame(seed=4)
        game.state.phase = "shoot"
        game.state.active_event = "BANG"
        game.state.shoot_started_at = time.time() - 0.5
        game.state.bullets = 100
        self.assertTrue(game.step(PLAYER_ID, {"type": "shoot", "text": "BANG",
                                              "reaction_seconds": 999})["accepted"])
        self.assertEqual(game.state.food, 52)
        self.assertEqual(game.state.bullets, 88)
        game.state.phase = "shoot"
        game.state.active_event = "POW"
        game.state.shoot_started_at = time.time() - 2.0
        self.assertTrue(game.step(PLAYER_ID, {"type": "shoot", "text": "POW",
                                              "reaction_seconds": 0.0})["accepted"])
        self.assertEqual(game.state.food, 100)
        game.state.phase = "shoot"
        game.state.active_event = "WHAM"
        game.state.shoot_started_at = time.time() - 0.1
        self.assertTrue(game.step(PLAYER_ID, {"type": "shoot", "text": "BANG",
                                              "reaction_seconds": 0.0})["accepted"])
        self.assertEqual(game.state.food, 100)

    def test_result_message_does_not_accumulate_previous_turn_text(self):
        game = OregonTrailGame(seed=7)
        game.state.phase = "ration"
        game.state.food = 100
        game.state.last_result = "OLD TURN MESSAGE"
        self.assertTrue(game.step(PLAYER_ID, {"type": "eat", "level": 2})["accepted"])
        self.assertNotIn("OLD TURN MESSAGE", game.state.last_result)
        self.assertTrue(game.state.last_result.startswith("You ate 18 food."))

    def test_save_load_round_trip_and_reject_malformed_state(self):
        game = OregonTrailGame(seed=12)
        game.step(PLAYER_ID, {"type": "buy", "item": "oxen", "amount": 250})
        game.record_model_call(success=False)
        game.record_runtime(17.5)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            game.save_state(path)
            loaded = OregonTrailGame.load_state(path)
            self.assertEqual(loaded.observe(PLAYER_ID), game.observe(PLAYER_ID))
            self.assertEqual(loaded.state.model_calls, 1)
            self.assertEqual(loaded.state.failed_model_calls, 1)
            self.assertEqual(loaded.state.elapsed_seconds, 17.5)
            path.write_text('{"version": 999, "state": {}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                OregonTrailGame.load_state(path)

    def test_save_load_after_completed_initial_and_fort_purchases(self):
        game = OregonTrailGame(seed=12)
        start_game(game)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            game.save_state(path)
            loaded = OregonTrailGame.load_state(path)
            self.assertEqual(loaded.observe(PLAYER_ID), game.observe(PLAYER_ID))

            game.step(PLAYER_ID, {"type": "visit_fort"})
            while game.observe(PLAYER_ID)["phase"] == "fort_purchase":
                item = game.legal_actions(PLAYER_ID)[0]["item"]
                game.step(PLAYER_ID, {"type": "buy", "item": item, "amount": 0})
            game.save_state(path)
            loaded = OregonTrailGame.load_state(path)
            self.assertEqual(loaded.observe(PLAYER_ID), game.observe(PLAYER_ID))
            self.assertEqual(loaded.state.fort_index, len(FORT_ITEMS))

    def test_save_load_rejects_incomplete_purchases_in_travel_phase(self):
        game = OregonTrailGame(seed=12)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            game.save_state(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["state"]["phase"] = "travel"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "purchase"):
                OregonTrailGame.load_state(path)

            ended_during_purchase = OregonTrailGame(seed=12)
            ended_during_purchase.step(PLAYER_ID, {"type": "invalid"})
            ended_during_purchase.step(PLAYER_ID, {"type": "invalid"})
            ended_during_purchase.save_state(path)
            loaded = OregonTrailGame.load_state(path)
            self.assertEqual(loaded.outcome()["status"], "terminal")
            self.assertEqual(loaded.state.purchase_index, 0)

    def test_save_load_rejects_phase_status_mismatch(self):
        game = OregonTrailGame(seed=12)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            game.save_state(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["state"]["phase"] = "terminal"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "phase and status"):
                OregonTrailGame.load_state(path)

            payload["state"]["phase"] = "initial_purchase"
            payload["state"]["status"] = "terminal"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "phase and status"):
                OregonTrailGame.load_state(path)

    def test_all_legal_actions_are_structured_and_episode_is_bounded(self):
        game = OregonTrailGame(seed=5, max_turns=2)
        self.assertTrue(all(isinstance(a, dict) for a in game.legal_actions(PLAYER_ID)))
        start_game(game)
        for _ in range(2):
            if game.outcome()["status"] == "terminal":
                break
            if game.observe(PLAYER_ID)["phase"] == "travel":
                game.step(PLAYER_ID, {"type": "continue"})
            if game.observe(PLAYER_ID)["phase"] == "ration":
                game.step(PLAYER_ID, {"type": "eat", "level": 2})
            if game.observe(PLAYER_ID)["phase"] == "event_response":
                game.step(PLAYER_ID, game.legal_actions(PLAYER_ID)[0])
        self.assertEqual(game.outcome()["status"], "terminal")
        self.assertLessEqual(game.outcome()["turn"], 2)

    def test_event_information_is_hidden_until_the_event_occurs(self):
        game = OregonTrailGame(seed=23)
        start_game(game)
        observation = game.observe(PLAYER_ID)
        self.assertNotIn("event_name", observation)
        self.assertNotIn("riders", str(game.legal_actions(PLAYER_ID)).lower())

    def test_riders_event_stays_visible_until_the_player_responds(self):
        class RidersOnly:
            def choices(self, *args, **kwargs):
                return ["riders"]

        game = OregonTrailGame(seed=23)
        game.state.phase = "ration"
        game.state.turn = 1
        game.state.food = 100
        game.rng = RidersOnly()
        self.assertTrue(game.step(PLAYER_ID, {"type": "eat", "level": 2})["accepted"])
        self.assertEqual(game.observe(PLAYER_ID)["phase"], "event_response")
        self.assertEqual(game.observe(PLAYER_ID)["event"]["name"], "riders")
        self.assertEqual({a["choice"] for a in game.legal_actions(PLAYER_ID)},
                         {"run", "stand_ground", "circle_wagons"})
        self.assertTrue(game.step(PLAYER_ID, {"type": "rider_response",
                                              "choice": "stand_ground"})["accepted"])
        self.assertEqual(game.observe(PLAYER_ID)["phase"], "travel")

    def test_shooter_cannot_claim_a_faster_reaction_time(self):
        game = OregonTrailGame(seed=23)
        game.state.phase = "shoot"
        game.state.active_event = "BANG"
        game.state.shoot_started_at = time.time() - 2.0
        game.state.bullets = 100
        result = game.step(PLAYER_ID, {"type": "shoot", "text": "BANG",
                                       "reaction_seconds": 0.0})
        self.assertTrue(result["accepted"])
        self.assertEqual(game.state.food, 48)


if __name__ == "__main__":
    unittest.main()
