- Pre-declared evaluation suite (at least 3 situations/tasks x 2 live trials).
  The game parameter / game state for this game is relative simple, so the the evaluation suite are different seeds that results in different random events in the game. The three seeds represent three different random seeds that gave the player 1) mostly clear trail with few negative random effects 2) a moderate mix of random events 3) a more adversarial scenario with many negative events.

- Baseline vs. Model-Driven Player comparison table.

  This table summarizes evaluation runs using the suite described above. The raw file is[`evaluation-20261107T190346Z.json`](evaluation_runs/evaluation-20261107T190346Z.json). For each seed - player type, the result is averaged across 2 runs. The avg completion column shows how much of the game the player finished (which also double as a score)

  | Evaluation situation | Player | Avg. game completion | Arrived |
  |---|---|---:|---:|---:|
  | Mostly clear (seed 3) | Heuristic baseline | 100.0% | 2/2 (100%) |
  | Mostly clear (seed 3) | Vertex model-driven | 88.5% | 0/2 (0%) |
  | Mixed events (seed 2) | Heuristic baseline | 100.0% |  2/2 (100%) |
  | Mixed events (seed 2) | Vertex model-driven | 90.4% |  0/2 (0%) |
  | Rider-heavy (seed 5) | Heuristic baseline | 99.8% |  0/2 (0%) |
  | Rider-heavy (seed 5) | Vertex model-driven | 92.5% |  0/2 (0%) |



- Traces (or links to traces) and cost/latency metrics.

  (also from the same evaluation run as above) 
  - The six trials with agent based player made 177 model calls,  
  - (Cost) 79,876 input tokens plus 2,667 output tokens (82,543 total), or about 13,313 input and 445 output tokens per trial.
  -  average call latency is 0.722 seconds; 
  -  on average each episode took 21.33 seconds.

- CI test results evidence.

  The CI workflow is [`.github/workflows/midterm-tony-wang-zh.yml`](../../.github/workflows/midterm-tony-wang-zh.yml). It installs the locked dependencies with `uv sync --frozen` and runs `uv run --frozen python -m unittest discover -s tests -v` from `midterm/tony-wang-zh/`. 

- A Limitations paragraph.
