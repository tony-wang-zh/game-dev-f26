# Oregon Trail Midterm Execution Plan

This plan turns the requested changes and the coursework brief into an implementation and submission checklist. It assumes Oregon Trail is the chosen reconstruction, the existing `oregon.py` is the starting point, and the final scope will be a small, complete episode that can be played by a person and by an automated player.

## Decisions to confirm (defaults are in bold)

1. **GitHub login: `tony-wang-zh`**, inferred from this folder name. Is that the exact lowercase login to use for the final submission folder and workflow filename?
A: Yes this is the github username to use

2. **Keep Oregon Trail and adapt the supplied Python starter.** Is Oregon Trail the final game choice, and may I refactor the existing code rather than preserve its current input/output structure?
A: oregon trail is the final choice. keep `oregon.py` as a base line reference and do not modify this file.

3. **Scope default: one bounded trip episode** with a finite number of travel turns, a clear arrival/loss ending, and a small set of recognizable Oregon Trail decisions (supplies, travel, hunting, food, and a few trail events). Is this acceptable, or do you want a particular part of the trip to be the episode?
A: Use a limited number of travel turns (e.g. 10) as a bounded episode. the episode should have a mix of events.

4. **Live model default: use the provider for which you already have credentials** (Vertex, Anthropic, or OpenAI), with the cheapest suitable model and a declared budget. Which provider can you configure in time? Do not put credentials in this repository.
A: I have a google cloud project already setup. use this project for the agent-player. the agent-player will use Vertex through it. project information are in google_cloud_info.json. 

1. **Video default: record a 3–5 minute local screen recording** showing human play and the player agent running without manual move selection. Where will it be hosted so course staff and assigned reviewers can view it?
A: I will do this manually and host on youtube myself

1. **Human test default: ask one friend/classmate/family member to play while you observe silently**, then anonymize notes. Who can do this, and when?
A: I will do this myself later 

These answers affect configuration and submission details, but the implementation can proceed with the bold defaults.

## Proposed scope and design record

- Reconstruct a compact, bounded slice of the 1978 Oregon Trail rather than porting every event and historical detail in the current script.
- Define the initial state, resource economy, legal actions, turn transitions, scoring/outcomes, and episode limit before implementing the wrapper.
- Use a seeded random source so a case can be replayed. Decide which events and choices fit the episode and document omissions/adaptations.
Note on randomness: add "seed" option at beginning to seed all randomness in game, so the same seed can be tested more easily
- Keep authoritative state in the game engine. The model player sees only the player observation and legal action vocabulary; it cannot inspect source files, state internals, or an answer key.
- about retaining or copying source code: do not worry about licensing: the originally basic code was open licensed, and the python code a directly translation that i made myself. 

## Work sequence

### 1. Resolve submission shape and scope

- the exact GitHub login and use the course-required final path is under `midterm/tony-wang-zh/`. Preserve this plan and useful starter material while preparing the final folder.
- Write the scope statement, episode boundaries, initial state, actions, transitions, outcomes, and episode limit.
- Draft the three evaluation situations before prompt tuning; select distinct starting situations/seeds and reserve at least one as held out.
- Create a rule/source map with locators and evidence labels (`code`, `manual`, `observed`, `assumed`, `design`). Credit the original game and all reused assets/material and state reuse terms.

### 2. Build the game engine and human CLI (for agent to complete)


- Refactor game state into an explicit serializable structure (for example, a dataclass) with validation and a versioned, human-readable JSON save format.
- Implement load-at-launch and save-at-any-point commands, validating loaded states and refusing malformed or incompatible saves safely.
- Separate game rules/state transitions from rendering, terminal input, and output. Implement the five-operation player boundary: `reset(seed)`, `observe(player_id)`, `legal_actions(player_id)`, `step(player_id, action)`, and `outcome()`.
- Keep observations and legal actions free of hidden information. Enforce legal actions, turn/episode limits, and explicit terminal reasons in the engine.
- Convert displayed text to normal capitalization. Add a lightweight terminal UI library with arrow-key selection for choice menus; preserve the timed typing action for shooting. Put save/load, help, and automated-agent controls on non-conflicting CLI commands or reserved controls outside game menus and typing rounds.
- Specifically, the UI should show all the player-visible stats (FOOD  BULLETS CLOTHING  MISC  CASH)
- Update item buying interface (both in initial purchase phase or while visiting any fort). after buying each item, the stats should be updated right away (currently player don't see the updated stats until end of the buying menu)

- Use `uv` and keep dependency/configuration files inside the final project folder. Document fresh-clone setup and exact working directories.
 
### 3. Implement and constrain both players (for agent to complete)

- Implement a cheap, meaningful scripted/heuristic baseline that uses only the same observations and actions as the model player. See human-written high-level idea for this player in `heuristic_player.md`
  
- Implement an executable model-driven player that chooses and submits actions through the five-operation interface. Keep the model API adapter separate from the engine and CLI. 
  - implement this agent such that it is strictly a text-in, action out agent. it's observation space is only what it is visible through the gameplay interface, and its action only chosen from legal actions. this agent does not have access to project files.
  - write a skill for this agent, roughly "you are a gameplay agent for the oregon trail game. Your goal is to finish the game, or make as good a progress as possible. the current game state is given to your through the interface, and you need to choose an action from the list of legal actions"   
  - This player will use Vertex AI through the provided google cloud project. when started during a play through, it should try to connect to the cloud project, and if needed, prompt the human to authenticate for google cloud client.
 
- build both players so that either can be started in the overall game-play CLI at any point in play through. the game cli should update as the machine-players play. the player's observations and action should be saved in a trace file (such as a json), timestamped and distinguished based on which player it was. save this in a separate folder 

- Enforce a per-episode step limit, model-call limit, timeout policy, invalid-action handling, and terminal reason. Count failed calls against the budget; never label a fallback as a successful model action.
    - each episode should be 10 in game travel turns. the model is expected to make 1 call per each step (aka each time a human player would have to choose something). each episode last up to 5 minutes. if model return invalid action, prompt action is invalid and try again; two consecutive invalid action results in the episode ending. 
  
- Record action traces and metrics for both players. If the game is fully observable, compare with/without bounded history or explain why memory is unnecessary.

### 4. Build evidence and review (for agent to complete)

- Add deterministic checks for rule invariants, legal and illegal actions, a successful terminal path, a genuine observed regression, and episode limits. Use mocked/replayed model outputs for deterministic integration checks; do not substitute them for live trials.
  
- Run the declared suite with at least three situations and two live trials per situation, plus the baseline on the same cases. Include held-out cases and report every failure.
  
- Capture outcomes, illegal actions, step/call limits, latency, token use, dated estimated cost, seeds, model/config identifiers, and game version in `EVALUATION.md`.
  
- Have another person play while you observe without helping. Record anonymous notes on actions, hesitations/guesses, and what you changed or would change. If this cannot happen, state why and what a playtest would have checked in the limitations paragraph.
  
- Provide the implementation assistant's instructions/session evidence, a reusable skill or prompt invoked in two sessions, and an independent read-only review with findings. Write `AGENT-TEAM.md` in your own voice, identifying each agent's access, recommendations, your decisions, and evidence locations. Do not present an agent as approving your own work.
  
- Record a 3–5 minute video showing the game and the agent making moves without manual selection; state relevant limits and link the recording from both README and PR.

### 5. Package and submit (agent, do not do these yet. some are for human to complete)

- Complete `README.md`, `EVALUATION.md`, `AGENT-TEAM.md`, playtest notes, traces (or durable links), code, tests, player, baseline, configuration, rule/source map, and source/reuse credits inside `midterms/<login>/`.
- Add exactly the project workflow `.github/workflows/midterm-<login>.yml`; it should run deterministic checks on relevant pull requests, touch no other project folders, and install no secrets.
- Open one PR targeting the course repository's `main`, with only the project folder plus that workflow. Link README, evaluation, team log, playtest notes, and recording in the PR description.


## Submission artifact checklist (for human reference only)

- `README.md`: scope; setup, play, test, evaluation commands with exact working directory for each; rule/source map; source credits and reuse terms; video link.
- Game source and UI; state save/load; player-facing CLI; five-operation engine interface.
- Executable model player and cheap baseline; non-secret agent/model configuration; traces or durable trace links.
- Deterministic tests and the login-specific workflow.
- `EVALUATION.md`: predeclared suite; baseline/model comparison table; trials, seeds, failures, outcome counts, invalid actions, limits, latency, tokens, dated cost, traces, CI evidence, limitations.
- `AGENT-TEAM.md`: one-page, student-authored log with implementation agent, reusable skill, and independent review evidence.
- Anonymous human playtest notes (or the specified omission explanation in limitations).
- 3–5 minute recording linked from README and PR description.
- PR URL submitted through CourseWorks by the deadline.

## Time-sensitive order (for human reference only)

Prioritize a complete, inspectable narrow game and all required artifacts over polishing every requested convenience. Work in this order: (1) confirm scope/login/provider, (2) implement engine plus five operations and deterministic checks, (3) baseline and one live model path, (4) run the required suite and fill evaluation metrics, (5) human playtest and notes, (6) README/team/review/video, (7) project workflow and PR. If the six live trials or other evidence cannot be completed by the deadline, report exactly what was run and why in limitations; do not fabricate results or imply mocked trials were live.
