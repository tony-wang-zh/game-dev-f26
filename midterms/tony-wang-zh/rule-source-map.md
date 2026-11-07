# Rule and source map

The bounded game is a reconstruction of the 1978 BASIC
Oregon Trail. The original source used (but not included in the repo) was
`original/oregon.bas` in [clintmoyer/oregon-trail](https://github.com/clintmoyer/oregon-trail/blob/master/original/oregon.bas). 
That repository identifies the program as the original Oregon Trail and says
it was shared in the May 1978 issue of *Creative Computing*. The repository
attributes original programming to Bill Heinemann and research/materials to
Don Rawitsch and MECC staff. Its [`COPYING` file](https://github.com/clintmoyer/oregon-trail/blob/master/COPYING)
declares the transcription to be free and unencumbered software under the
Unlicense, dedicating it to the public domain. This project credits that
transcription and license; its scoped engine, adaptations, and additional
rules are newly implemented and labeled `design` below.

note that instead of using the original BASIC code as reference, the project first uses a python translation of the BASIC code for the ease of running locally and readability for humans` and ai agents.

| Rule | Evidence label and locator | Implementation target | Acceptance evidence |
|---|---|---|---|
| Oregon Trail's source rules and terminology are reconstructed from the 1978 BASIC transcription. | `code`: [clintmoyer/oregon-trail `original/oregon.bas`](https://github.com/clintmoyer/oregon-trail/blob/master/original/oregon.bas), originally published in *Creative Computing*, May 1978; the repository's [`COPYING`](https://github.com/clintmoyer/oregon-trail/blob/master/COPYING) declares the Unlicense. | `oregon.py` is the student's direct Python translation; `game.py` contains the bounded reconstruction. | Local rule rows below identify the reference functions and label bounded changes `design`. |
| Starting budget is $700 after the wagon purchase; the player allocates it across oxen, food, ammunition, clothing, and supplies. | `code`: `oregon.py`, `initial_purchases`; bounded prices and validation are `design`. | `game.py`: purchase phase | Purchase tests check immediate cash/inventory updates, available cash, and oxen minimum. |
| Ten travel turns form the default bounded episode; configurable travel-turn limits also terminate with a reason that reports the active limit. Arrival at 2,040 miles wins. | `design`: `EXECUTION_PLAN.md`, scope decisions. | `game.py`: `max_turns`, `_turn_limit_reason`, and terminal checks | Deterministic tests check the ten-turn limit and a custom two-turn limit reached after ration and rider-response phases. |
| The score is trip progress from 0 to 1, capped at 1 at Oregon City, including partial progress on a loss or turn limit. | `design`: midterm outcome should compare bounded single-player progress. | `game.py`: `_terminal` | Test checks partial score on a forced early ending and full score on arrival. |
| A travel choice advances 205 miles plus one mile for each oxen-quality dollar above 220 divided by five; fort/hunt stops then cost 45 miles. | `code`: `oregon.py`, `game_loop` mileage formula; `design`: fixed seeded movement and 205-mile bounded pace. | `game.py`: `_step_travel` | Exact movement test with 250 oxen checks 211 miles before stop costs. |
| Each turn lets the player stop at an available fort, hunt when ammunition permits, or continue; a fort visit costs time and fort availability alternates. | `code`: `oregon.py`, `take_turn_action`, `visit_fort`, `hunt`; simplifications and exact effects are `design`. | `game.py`: travel action rules | Legal-action and transition tests, including refusing unavailable hunting/fort actions. |
| The player chooses a ration level; food is consumed and exhaustion is terminal. | `code`: `oregon.py`, `eat`; bounded consumption/termination are `design`. | `game.py`: ration phase | Tests verify food deltas and starvation. |
| Hunting requires typing the displayed word; the engine measures elapsed time from revealing the target. A correct shot within one second gives 52 food and costs 12 bullets, a slower correct shot gives 48 food, and a wrong word misses. | `code`: `oregon.py`, `hunt` and `shoot`; simplified rewards and one-second threshold are `design`. | `game.py`: hunt/shoot phase; `cli.py`: timed text input | Tests verify fast, slow, and incorrect shots, including that an action cannot claim a faster time. |
| Trail events are selected from a seeded event set and may consume resources, slow travel, or present a response choice. | `code`: `oregon.py`, `random_events`, `check_riders`, `check_mountains`; reduced event set and outcomes are `design`. | `game.py`: event phase | Seeded event tests verify visible events and legal responses. |
| Observation includes only player-visible resources, progress, phase, visible event, and description; legal actions contain no hidden event information. | `design`: coursework five-operation interface and this project specification. | `game.py`: `observe`, `legal_actions` | Tests compare observation/actions before and after an event is revealed. |
| Refused actions do not mutate game state, are counted, and two consecutive invalid actions end an agent-controlled episode. The heuristic's ration choice uses the levels currently offered by the engine. | `design`: `EXECUTION_PLAN.md`. | `game.py`: `step` validation and ration legal actions; `heuristic_player.py`: ration selection | Tests verify immutable rejection, invalid count, consecutive-invalid termination, and that the heuristic selects an available ration at low food. |
| Each result message describes the latest action/event without accumulating prior turn text. | `observed`: duplicate prior-turn messages during the CLI smoke play; corrected behavior is specified here. | `game.py`: `step`, `_step_ration` | Regression test checks that a new result does not retain the previous message. |
| Randomness is reproducible from a seed. | `design`: `EXECUTION_PLAN.md`. | `game.py`: seeded RNG | Repeated seeds produce matching event sequences. |
| Save files are versioned, human-readable JSON and validated on load; completed purchase indices remain valid after the game advances to its next phase, while incomplete purchases cannot appear in later active phases. Terminal phase and outcome status must agree. | `design`: `EXECUTION_PLAN.md`. | `game.py`: save/load validation | Round-trip tests cover saves after initial purchases, a completed fort purchase, and a terminal during initial purchases; malformed incomplete-purchase and phase/status-mismatch saves are rejected. |

## Acceptance trace

The primary trace will buy supplies within budget, then choose travel/rations
that reach Oregon City by turn ten. Random events are deterministic under the
trace seed. Individual tests also cover event responses and refusal of illegal
actions. Exact trace actions and resulting values are maintained in the tests.

