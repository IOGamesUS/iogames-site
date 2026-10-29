# IO Games site tools

Not published: GitHub Pages skips folders that start with an underscore.

- `build_game.py wordtangle|pemdash`: rebuilds `<game>/index.html` from `_tools/<game>/template.html` and `puzzles.enc`.
- `codec.py`: decode a puzzles.enc to JSON for editing, and encode it back. Answers are lightly obfuscated, not secret.
- `wordtangle/gen.py`: finds word rectangles (needs `pip install wordfreq`). Clues are written by hand.
- `pemdash/gen.py`: generates order-of-operations puzzles with exactly one solution.
- `home/build.py`: builds the home page (`python3 _tools/home/build.py index.html`).
- `counter/Code.gs`: the Apps Script play counter. When a game's queue grows, raise its number in GAMES there and redeploy a new version.

Puzzle ids are play order. The counter serves today's puzzle number per game and moves on overnight only if the current puzzle was played.
