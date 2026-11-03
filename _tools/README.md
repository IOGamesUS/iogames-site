# IO Games site tools

Not published: GitHub Pages skips folders that start with an underscore.

- `build_game.py wordtangle|pemdash|meld`: rebuilds `<game>/index.html` from `_tools/<game>/template.html` and `puzzles.enc`.
- `codec.py`: decode a puzzles.enc to JSON for editing, and encode it back. Answers are lightly obfuscated, not secret.
- `wordtangle/gen.py`: finds word rectangles (needs `pip install wordfreq`). Clues are written by hand.
- `meld/gen.py`: generates Rummy Run hands (code name meld) with exactly one way to split them into sets and runs; aces high or low, no wrapping.
- `pemdash/gen.py`: generates order-of-operations puzzles with exactly one solution.
- `home/build.py`: builds the home page (`python3 _tools/home/build.py index.html`).
- `counter/Code.gs`: the Apps Script play counter (copy of what is deployed). When a game's queue grows, raise its number in GAMES there and redeploy a new version. It also serves each puzzle's results for the percentile panel.
- `after.js`: the panel under every finished puzzle (percentile and links to the other games), added by build_game.py.
- `crazypath/`: built but not yet published; publish with `python3 _tools/build_game.py crazypath` once the counter lists it.
- `pokerrows/`: built but not yet published. `gen.py` makes 3x3 and 4x4 grids with exactly one answer. Preview without the counter: `python3 _tools/build_game.py pokerrows /path/preview.html`.

Puzzle ids are play order. The counter serves today's puzzle number per game and moves on overnight only if the current puzzle was played.
