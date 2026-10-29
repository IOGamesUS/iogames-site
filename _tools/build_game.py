"""Build a live game page.  python3 _tools/build_game.py wordtangle|pemdash
Reads _tools/<game>/template.html and puzzles.enc, writes <game>/index.html (the published page)."""
import os, sys, json, re
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
sys.path.insert(0, here); import codec
game = sys.argv[1]
API = "https://script.google.com/macros/s/AKfycbzxlJIAAwQbGZ2rSdf8uBiRgskIYVQDvIWddeXoB1oAFMRCLFsgr0P7StOB6naYKIwz/exec"
ns = {"__name__": "x", "sys": sys}
src = open(os.path.join(here, "home", "build.py")).read().split("wordmark = ")[0].replace("OUT = sys.argv[1]", "OUT=None")
exec(src, ns)
title = ns["word_svg"]({"wordtangle": "WORDTANGLE", "pemdash": "PEMDASH"}[game], "title", "#f2c14e", "#7a4a1c", {"wordtangle": "WordTangle", "pemdash": "Pemdash"}[game])
data = codec.dec(game, open(os.path.join(here, game, "puzzles.enc")).read().strip())
html = open(os.path.join(here, game, "template.html")).read()
html = (html.replace("{{TITLE_SVG}}", title).replace("{{FAVICON}}", ns["favicon"]()).replace("{{DATA}}", codec.enc(game, data))
        .replace("{{LIVE}}", "true").replace("{{API}}", API).replace("{{ROBOTS}}", "")
        .replace(" prototype by IO Games", " by IO Games")
        .replace("Your progress stays on this device.", "Your progress stays on this device. Finished puzzles are counted anonymously (puzzle number, result and score only)."))
assert "—" not in html
os.makedirs(os.path.join(root, game), exist_ok=True)
open(os.path.join(root, game, "index.html"), "w").write(html)
print("built", game, len(data), "puzzles")
