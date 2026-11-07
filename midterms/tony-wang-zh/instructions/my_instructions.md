Implementation goals:

- Text: currently all displayed text are in all caps. Change display texts to normal capitalization for easier reading. 

- Use UV for package management 

- Encapsulate the game state (e.g. could be a data class) 
  - Make it so that game can be saved at any point into a human-readable game state file
  - make launch option to load game state and start from there

- UI: currently the game prints its text to stdout. Use a simple lightweight python CLI library and convert the game interface from typing to a CLI interface. 
  - For option-selecting parges in-game, instead of typing in the selection, the player can use up and down to choose and return to select.
  - Typing minigames should still be the same.
  - Implementation: this should be as encapsulated from the core game logic as possible. 

- functions including saving, loading, and let agent play the game should be executable all from this CLI interface with special key binds (aka these controls should not overlap the selections and typing minigames in-game)

- Note on randomness: add "seed" option at beginning to seed all randomness in game, so the same seed can be tested more easily
