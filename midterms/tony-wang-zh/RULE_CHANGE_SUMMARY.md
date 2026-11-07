# Rule change and boundary review request

Please review the implemented bounded Oregon Trail rules and player boundary
independently. The original `oregon.py` was preserved as requested. The source
map is `rule-source-map.md`.

## Rules and evidence

- Purchase phases spend from the $700 budget and update visible resources
  immediately. `oregon.py:initial_purchases` is the local code reference;
  currency conversions and purchase-phase details are labeled `design` in the
  map.
- A ten-turn bounded episode uses seeded events and movement. The local
  reference formula is in `oregon.py:game_loop`; the fixed movement pace,
  event probabilities, 45-mile stop cost, and ten-turn termination are
  project adaptations labeled `design`.
- The player can continue, visit a fort, or hunt; choose a ration; type the
  displayed hunting word; and respond to rider encounters. The map identifies
  the relevant functions in `oregon.py` and the simplified `design` behavior.
- Rider encounters remain in the visible response phase until the player
  chooses a response. The engine starts and measures the shooting timer itself;
  a submitted action cannot claim a faster reaction time.
- Scores report trip progress from 0 to 1. Save/load captures validated,
  versioned game state and RNG state so a seeded episode can resume exactly.
- The text result shown to the player describes the latest turn only. During a
  CLI smoke play, prior-turn result text was observed to accumulate and print
  repeatedly. The state update was corrected and
  `test_result_message_does_not_accumulate_previous_turn_text` now checks the
  observed regression.

## Tests and interface

- Mileage acceptance test: `test_continue_advances_expected_miles_for_starting_oxen_quality`
  was run before the engine change and failed with 216 miles where the selected
  205-mile pace plus oxen bonus should give 211; it passes now.
- Partial-score test: `test_failure_score_preserves_partial_trip_progress` was
  run before the score change and failed with 0 where half-trip progress should
  give 0.5; it passes now.
- Hunting test: `test_shooting_typing_minigame_rewards_accuracy_and_speed` was
  run before the reaction-time change and failed because slow correct typing
  received the fast-shot reward; it passes now.
- The independent first review found that rider responses were skipped and
  that an action could claim a false reaction time. The new
  `test_riders_event_stays_visible_until_the_player_responds` and
  `test_shooter_cannot_claim_a_faster_reaction_time` both failed before their
  fixes and pass now.
- The deterministic tests cover purchase accounting, legal and refused
  actions, saves, seeded state, score, successful arrival, episode limits,
  player boundary, a replayed-model evaluation path, and the result-message
  regression. Command (from `midterms/tony-wang-zh/`):
  `uv run --frozen python -m unittest discover -s tests -v`.
- `observe` returns player-visible progress/resources and only a revealed
  event. `legal_actions` contains the currently visible choices and bounded
  purchase templates. The Vertex adapter receives only serialized observation
  and legal actions. It has no tools, filesystem reads, evaluator state, or
  answer key. Invalid actions leave the game observation unchanged, are
  counted, and two consecutive invalid actions terminate the episode.
- Human and machine shooting share exact-word validation and engine-measured
  response time. The model's request latency counts as its response time.
- The independent read-only review found the prior rider-phase and reaction
  timing issues, which were fixed and retested. Its follow-up found no new rule
  or player-boundary issue. The source citation and reuse terms have now been
  confirmed and recorded in `rule-source-map.md`: the Python reference is a
  direct translation of `original/oregon.bas` from clintmoyer/oregon-trail,
  whose `COPYING` file declares the Unlicense/public-domain dedication.

## Assumptions and unresolved evidence

- This implementation is a compact design adaptation, not a claim that the
  1978 source had these exact probabilities, costs, event sequence, or scoring
  rule. The relevant `design`/`code` labels and current local locators are in
  `rule-source-map.md`.
- The source repository identifies the BASIC game as shared in the May 1978
  issue of *Creative Computing*, attributes original programming to Bill
  Heinemann and research/materials to Don Rawitsch and MECC staff, and declares
  the transcription free and unencumbered under the Unlicense. The precise
  citation and license links are recorded in `rule-source-map.md` and
  `README.md`.
- The game is fully observable at each decision. The player is stateless and
  receives the current resource totals, progress, phase, current result, and
  revealed encounter; the hidden seeded future event sequence is not exposed.

## Follow-up from independent functional review

The reviewer reported three reproducible issues in `REVIEW_FINDINGS.md`:

- Save validation rejected completed purchase indices even when the game had
  advanced beyond that purchase phase. `test_save_load_after_completed_initial_and_fort_purchases`
  failed before the fix and now covers saves at both phase boundaries.
- The heuristic always chose ration level 2, which is unavailable with 13–17
  food. `test_heuristic_chooses_a_legal_ration_when_food_is_low` failed before
  the fix; the heuristic now selects level 2 when offered and otherwise picks
  an offered ration. The test verifies the action is accepted.
- Custom turn limits ended with the hard-coded reason `ten-turn limit`.
  `test_custom_turn_limit_is_named_in_terminal_reason` failed before the fix;
  terminal reasons now report the configured travel-turn limit.

The independent follow-up found two additional gaps: validation did not reject
unfinished initial purchases in an active post-purchase phase, and custom-turn
limit coverage did not exercise the rider-response termination path. The
loader now rejects those impossible active states while still allowing a
terminal save made during initial purchases. The turn-limit test covers both
ration and rider-response termination. A further review found that a forged
save could pair a terminal phase with ongoing status (or vice versa); the
loader now rejects either mismatch, with both cases covered by
`test_save_load_rejects_phase_status_mismatch`. The rule/source map was updated
for these cases. All 29 deterministic tests pass; final reviewer confirmation
is pending.

