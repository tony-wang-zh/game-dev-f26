# Functional Code Review Findings

Review scope: executable Python gameplay, player, CLI, and evaluation paths. This review focused on behavior and state transitions. It did not modify implementation code or run tests.

## Findings

### 1. [P1] Valid saves after initial purchases cannot be loaded

**Location:** [game.py](game.py#L427)

After the fifth initial purchase, `purchase_index` advances to `len(PURCHASE_ITEMS)` (5) and the game moves to `travel`. `save_state()` serializes that state, but `load_state()` rejects every index greater than or equal to the item count, without considering the phase. The CLI autosaves after each accepted action, so the ordinary save created when the player completes setup cannot be resumed. A completed fort purchase similarly leaves `fort_index == len(FORT_ITEMS)` (4) in the ration phase, which is also rejected.

**Reproduction:** Complete all five initial purchases, save, then load that file. Loading raises `ValueError("invalid saved purchase index")`. Complete all four fort purchases and save to reproduce the corresponding fort-index failure.

**Suggested fix:** Validate purchase and fort indices against the active phase: allow the completed count in phases entered after that sequence, while keeping the index within the sequence bounds for its active purchase phase.

### 2. [P2] Heuristic player chooses an unavailable ration with 13–17 food

**Location:** [heuristic_player.py](heuristic_player.py#L40)

The heuristic always submits ration level 2. The engine only offers level 1 when food is below 18, so at 13–17 food the heuristic submits an illegal action. Since the state does not change after rejection, the same heuristic submits the same invalid action again; the engine then terminates the episode for two consecutive invalid actions. This can turn a recoverable low-food situation into an automatic loss for the baseline.

**Reproduction:** Set the game to the `ration` phase with 15 food and ask `HeuristicPlayer.choose()` to choose from `game.legal_actions(PLAYER_ID)`. It returns level 2, which the engine rejects; calling it again produces the second rejection and terminal state.

**Suggested fix:** Choose among the supplied legal ration actions, preferring level 2 only when it is present.

### 3. [P2] Configurable turn limits report a hard-coded ten-turn reason

**Location:** [game.py](game.py#L313) and [game.py](game.py#L364)

`OregonTrailGame` accepts a configurable `max_turns`, and both terminal checks use that value, but the reported reason is always `ten-turn limit`. For any configured limit other than ten, the game ends at the right turn while exposing a false terminal explanation in `outcome()` and traces.

**Reproduction:** Construct `OregonTrailGame(max_turns=2)`, complete two travel turns without arriving, and inspect `outcome()["reason"]`; it reports `ten-turn limit`.

**Suggested fix:** Build the reason from `self.max_turns` (or use a limit-neutral reason such as `travel-turn limit`).

## Review limits

Findings are based on static inspection of the Python paths and existing tests. No tests or live model calls were run for this review.
