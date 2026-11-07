# Oregon Trail: bounded midterm reconstruction

## Setup and commands

Run commands from the `midterms/tony-wang-zh/` directory in the course repository.

```sh
uv sync --frozen
uv run --frozen python cli.py --player human --seed 3
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python evaluate.py
```

`evaluate.py` runs the heuristic baseline on the predeclared suite. To run the
live Vertex model suite, use `uv run --frozen python evaluate.py --live`; to run
only the reserved held-out case, use
`uv run --frozen python evaluate.py --live --held-out-only`. Live runs use
Vertex AI and incur token charges. Each episode is capped at 80 model calls and
300 seconds. A failed Vertex call is not replaced with a heuristic action.

To resume a saved game, add `--load game_saves/autosave.json` to the `cli.py`
command. To start a player directly, use `--player vertex` or
`--player heuristic`. For Vertex authentication, run
`gcloud auth application-default login`. Project settings are read from
`google_cloud_info.json`; credentials are supplied through Google Application
Default Credentials and are not stored in this project.

## Scope and source map

This project reconstructs a bounded episode of the text-based Oregon Trail.
The player allocates a $700 starting budget, then makes supply, travel, fort,
hunting, ration, and encounter choices over at most 10 travel turns. Arrival
at Oregon City wins; resource failure, invalid-action limits, or the turn
limit can end the episode earlier. The score measures route progress from 0
to 1. The compact version omits the full calendar, detailed illness/injury
system, and most original events. See [`rule-source-map.md`](rule-source-map.md)
for rules, evidence labels, source locators, and acceptance evidence.

The reference game is *The Oregon Trail*, originally programmed by Bill
Heinemann, with research and materials from Don Rawitsch and MECC staff. The
The included `oregon.py` is a direct Python translation of the BASIC transcription at
[`clintmoyer/oregon-trail`](https://github.com/clintmoyer/oregon-trail/blob/master/original/oregon.bas).
That repository identifies the game as shared in the May 1978 issue of
[*Creative Computing*](https://archive.org/details/CreativeComputingbetterScan197805/page/n138/mode/1up).
Its [`COPYING` file](https://github.com/clintmoyer/oregon-trail/blob/master/COPYING)
declares the transcription free and unencumbered under the Unlicense and
dedicates it to the public domain. The bounded engine and adaptations are
newly implemented.

## Recording

[Game and agent recording](https://youtu.be/kg9pkfdCjP8)
