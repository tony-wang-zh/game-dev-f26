# Evaluation report

## Predeclared evaluation suite

The suite was declared on 2026-11-07 in [`evaluation_suite.json`](evaluation_suite.json): two trials for each of three seeded situations, with seed 4 reserved as a held-out case. The main comparison uses the same seeds and game rules for the heuristic baseline and Vertex model-driven player. Each episode has a 10 travel-turn limit, an 80-call model budget, and a 300-second time limit.

## Baseline and model-driven player

The table summarizes the six trials per player in
[`evaluation-20261107T190346Z.json`](evaluation_runs/evaluation-20261107T190346Z.json).
Average game completion is average miles traveled divided by 2,040; score is
the mean score from 0 to 1. `Arrived` counts trials that reached Oregon City.

| Situation | Player | Avg. game completion | Avg. score | Arrived |
|---|---|---:|---:|---:|
| Mostly clear (seed 3) | Heuristic baseline | 100.0% | 1.000 | 2/2 (100%) |
| Mostly clear (seed 3) | Vertex model-driven | 88.5% | 0.885 | 0/2 (0%) |
| Mixed events (seed 2) | Heuristic baseline | 100.0% | 1.000 | 2/2 (100%) |
| Mixed events (seed 2) | Vertex model-driven | 90.4% | 0.904 | 0/2 (0%) |
| Rider-heavy (seed 5) | Heuristic baseline | 99.8% | 0.998 | 0/2 (0%) |
| Rider-heavy (seed 5) | Vertex model-driven | 92.5% | 0.925 | 0/2 (0%) |

Across all six trials, the heuristic averaged 99.9% route completion and a
0.999 score; Vertex averaged 90.4% completion and a 0.904 score. The heuristic
reached Oregon City in 4/6 trials; Vertex reached it in 0/6. Neither player
submitted an invalid action in these runs, and all six Vertex trials completed
without a failed model call. The Vertex episodes ended at the turn limit.

The reserved held-out case was run separately on 2026-11-07; results are in
[`evaluation-20261107T180332Z.json`](evaluation_runs/evaluation-20261107T180332Z.json).
The heuristic arrived in 2/2 trials (mean completion 100%, score 1.000).
Vertex arrived in 0/2 trials (mean completion 94.1%, score 0.941); it made 55
calls with no failed calls or invalid actions.

## Traces, cost, and latency

The six main-suite Vertex trials used model `gemini-3.5-flash-lite` and made
177 calls: 79,876 input tokens and 2,667 output tokens (82,543 total), or about
13,313 input and 445 output tokens per episode. Call latency averaged 0.722
seconds when weighted by calls; the maximum was 1.271 seconds. Mean episode
wall time was 21.33 seconds.

Using the global Vertex token prices recorded in [`pricing.json`](pricing.json)
($0.15 per million input tokens and $1.25 per million output tokens, checked
2026-11-07), the estimated total cost was **$0.01531515 USD**. The heuristic
used no model tokens and incurred no model cost. This estimate excludes credits,
taxes, and non-token charges.

The main-run action traces are in
[`evaluation_runs_traces/`](evaluation_runs_traces/). The JSON evaluation
report records trial outcomes and trace filenames. The held-out report records
the results and token/latency metrics for its four trials.

## CI test evidence

The login-specific workflow is
[`.github/workflows/midterm-tony-wang-zh.yml`](../../.github/workflows/midterm-tony-wang-zh.yml).
On pull requests that change this project, it installs locked dependencies
and runs `uv run --frozen python -m unittest discover -s tests -v` from
`midterms/tony-wang-zh/`. The workflow uses no secrets and makes no live model
calls. The same deterministic command passed locally with **29 tests** on
2026-11-07. Hosted Actions evidence will be linked here after the PR workflow
has run.

## Limitations

This is a small seeded evaluation with two trials per situation, so the results
are descriptive and do not establish statistical certainty. The Vertex player
made progress but did not arrive in the six main-suite trials; the heuristic
arrived in four. The held-out sample contains only two trials per player. No
independent human playtest notes are included in this snapshot: the available
human trace is not a substitute for someone else playing while the student
observes. The execution plan deferred the playtest for the student to arrange,
so this draft does not claim that requirement is met. Such a playtest should
check whether the menus, resource updates, encounter choices, and 10-turn pace
are clear. Add anonymous notes after that session before treating the
submission as complete.
