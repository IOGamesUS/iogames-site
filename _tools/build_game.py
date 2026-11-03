"""Build a live game page.  python3 _tools/build_game.py wordtangle|pemdash|meld|crazypath|pokerrows
Reads _tools/<game>/template.html and puzzles.enc, writes <game>/index.html (the published page)."""
import os, sys, json, re
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
sys.path.insert(0, here); import codec
game = sys.argv[1]
PREVIEW = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] else None  # build_game.py <game> <out.html>: playable preview with a puzzle picker, not connected to the counter
API = "https://script.google.com/macros/s/AKfycbzxlJIAAwQbGZ2rSdf8uBiRgskIYVQDvIWddeXoB1oAFMRCLFsgr0P7StOB6naYKIwz/exec"
ns = {"__name__": "x", "sys": sys}
src = open(os.path.join(here, "home", "build.py")).read().split("wordmark = ")[0].replace("OUT = sys.argv[1]", "OUT=None")
exec(src, ns)
title = ns["word_svg"]({"wordtangle": "WORDTANGLE", "pemdash": "PEMDASH", "meld": "RUMMY RUN", "crazypath": "CRAZY PATH", "pokerrows": "POKER ROWS"}[game], "title", "#f2c14e", "#7a4a1c", {"wordtangle": "WordTangle", "pemdash": "Pemdash", "meld": "Rummy Run", "crazypath": "Crazy Path", "pokerrows": "Poker Rows"}[game])
data = codec.dec(game, open(os.path.join(here, game, "puzzles.enc")).read().strip())
html = open(os.path.join(here, game, "template.html")).read()
if PREVIEW:
    html = (html.replace("{{TITLE_SVG}}", title).replace("{{FAVICON}}", ns["favicon"]()).replace("{{DATA}}", codec.enc(game, data))
            .replace("{{LIVE}}", "false").replace("{{API}}", "").replace("{{ROBOTS}}", '<meta name="robots" content="noindex">')
            .replace('<a class="home" href="/">IO Games</a>', '<a class="home" href="https://iogames.us">IO Games</a>'))
    assert "\u2014" not in html
    open(PREVIEW, "w").write(html); print("preview", game, len(data), "puzzles"); sys.exit(0)
html = (html.replace("{{TITLE_SVG}}", title).replace("{{FAVICON}}", ns["favicon"]()).replace("{{DATA}}", codec.enc(game, data))
        .replace("{{LIVE}}", "true").replace("{{API}}", API).replace("{{ROBOTS}}", "")
        .replace(" prototype by IO Games", " by IO Games")
        .replace("Your progress stays on this device.", "Your progress stays on this device. Finished puzzles are counted anonymously (puzzle number, result and score only)."))
# games that are live on the site, in home-page order (used for the "More daily puzzles" links)
LIVE_GAMES = [g for g in [
    {"id": "wordtangle", "name": "WordTangle", "key": "iogames-wt"},
    {"id": "pemdash", "name": "Pemdash", "key": "iogames-pz"},
    {"id": "meld", "name": "Rummy Run", "key": "iogames-md"},
    {"id": "crazypath", "name": "Crazy Path", "key": "iogames-cp"},
    {"id": "pokerrows", "name": "Poker Rows", "key": "iogames-pr"},
] if os.path.exists(os.path.join(root, g["id"], "index.html")) or g["id"] == game]
# report finish time with each result, so players can be ranked by score, then time
html = html.replace("result: st, score:", "result: st, secs: Math.round(S.elapsed / 1000), score:")
# header link goes back to the puzzle list on the home page
html = html.replace('<a class="home" href="/">IO Games</a>', '<a class="home" href="/#daily">&lsaquo; All puzzles</a>')
after = open(os.path.join(here, "after.js")).read().replace("{{API}}", API).replace("{{GAME}}", game).replace("{{GAMES}}", json.dumps(LIVE_GAMES)).replace("{{KEY}}", {"wordtangle": "iogames-wt", "pemdash": "iogames-pz", "meld": "iogames-md", "crazypath": "iogames-cp", "pokerrows": "iogames-pr"}[game])
html = html.replace("</body>", "<script>\n" + after + "</script>\n</body>", 1)
# live pages: no "Reset puzzle", so a finished puzzle is counted once
html = html.replace("</style>", "#again { display: none !important; }\n</style>", 1)
assert "\u2014" not in html
os.makedirs(os.path.join(root, game), exist_ok=True)
open(os.path.join(root, game, "index.html"), "w").write(html)
print("built", game, len(data), "puzzles")
