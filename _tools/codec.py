"""Encode/decode puzzle files. Same light XOR obfuscation the game pages use, so answers are not plain text in the repo."""
import base64, json, sys
KEYS = {"wordtangle": b"iogames-wt", "pemdash": b"iogames-pz"}
def enc(game, data):
    raw = json.dumps(data, separators=(",", ":")).encode()
    k = KEYS[game]
    return base64.b64encode(bytes(b ^ k[i % len(k)] for i, b in enumerate(raw))).decode()
def dec(game, s):
    raw = base64.b64decode(s); k = KEYS[game]
    return json.loads(bytes(b ^ k[i % len(k)] for i, b in enumerate(raw)).decode())
if __name__ == "__main__":
    # python3 codec.py decode wordtangle puzzles.enc > plain.json   |   python3 codec.py encode wordtangle plain.json > puzzles.enc
    mode, game, path = sys.argv[1:4]
    txt = open(path).read()
    print(json.dumps(dec(game, txt.strip()), indent=1) if mode == "decode" else enc(game, json.loads(txt)))
