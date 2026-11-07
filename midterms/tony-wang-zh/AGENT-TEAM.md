# agent team log

## implementation
- This agent is the main code-writing agent. It has full read and write access to the files in this repo (mostly under `midterms/tony-wang-zh` but also other directory because of need for CIs). This agent is running GPT-6-Luna with high effort. It is run from CLI and the main developing interface for this project.

## gameplay 
- This agent is the game's play test agent. It only lives within the context of a game's episode / playthrough, and only has access to the information as exposed to it through the game play interface, and only choose its actions through the same interface. The agent is running gemini-3.5-flash-lite and is invoked either from evaluation run calls or within the game for a single step

## review 
- This agent is the review agent. It has read and execution access to the repo's code and conducts code reviews. It reads and runs code as write down its findings as reference for future work. This agent run GPT-6-Luna too and is manually run through CLI.
