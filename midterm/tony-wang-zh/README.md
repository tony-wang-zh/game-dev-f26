- **Setup, play, tests, and evaluation commands**

  - To run the game, run the following commands from the `midterm/tony-wang-zh/` working directory

  - first sync project packages with `uv sync --frozen`
  
  - To start a regular play through: `uv run --frozen python cli.py --player human --seed 3`

  - use arrow keys to select options, and keyboard for text inputs

  - To run unit tests: `uv run --frozen python -m unittest discover -s tests -v`

  - To run the game with the heuristic player: `uv run --frozen python evaluate.py` (this uses the seeds from evaluation.json)

  - To run the game with the vertex agent player: `uv run --frozen python evaluate.py --live` (this uses the seeds from evaluation.json)

  - add `--held-out-only` to run the held out case 

- **Scope statement and rule/source map**

  This is a compact version of the original text-only oregon trail. Each play through constitute a self-contained episode that can be finished in 5 minutes by human players. see rule-resource-map.md for rules and resources

- **Source credit and reuse terms**

  The reference game is *The Oregon Trail*, originally programmed by Bill
  Heinemann, with research and materials from Don Rawitsch and MECC staff. The base game logic used to start the reconstruction is 
  [`original/oregon.bas` in clintmoyer/oregon-trail](https://github.com/clintmoyer/oregon-trail/blob/master/original/oregon.bas).
  The repository identifies the game source as shared in the May 1978 issue
  of *Creative Computing* ([issue scan](https://archive.org/details/CreativeComputingbetterScan197805/page/n138/mode/1up)).

- Link to your video recording.
https://youtu.be/kg9pkfdCjP8