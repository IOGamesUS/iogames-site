#!/usr/bin/env python3
"""Poker Rows puzzle generator.
A 3x3 or 4x4 grid of cards. Every row and every column is labeled with the poker hand its cards make.
Some cards are given; the rest sit in a tray and the player places them. A puzzle is kept only if the
tray cards fit the empty squares in exactly one way.
Aces count high or low in straights (A 2 3 or Q K A) but never wrap (K A 2)."""
import random, json, sys
from collections import Counter

SUITS = "SHDC"

def is_straight(ranks):
    rs = sorted(ranks)
    if len(set(rs)) != len(rs):
        return False
    if all(rs[i] + 1 == rs[i + 1] for i in range(len(rs) - 1)):
        return True
    hi = sorted(14 if r == 1 else r for r in rs)
    return all(hi[i] + 1 == hi[i + 1] for i in range(len(hi) - 1))

def hand(cards):
    """Name of the poker hand a 3 or 4 card line makes."""
    ranks = [c // 10 for c in cards]
    suits = [c % 10 for c in cards]
    flush = len(set(suits)) == 1
    straight = is_straight(ranks)
    counts = sorted(Counter(ranks).values(), reverse=True)
    if flush and straight:
        return "Straight flush"
    if counts[0] == 4:
        return "Four of a kind"
    if counts[0] == 3:
        return "Three of a kind"
    if straight:
        return "Straight"
    if flush:
        return "Flush"
    if counts[:2] == [2, 2]:
        return "Two pair"
    if counts[0] == 2:
        return "Pair"
    return "High card"

def lines(n):
    rows = [[r * n + c for c in range(n)] for r in range(n)]
    cols = [[r * n + c for r in range(n)] for c in range(n)]
    return rows + cols

def labels(n, grid):
    return [hand([grid[i] for i in L]) for L in lines(n)]

def count_solutions(n, grid, given, limit=2):
    """Ways to place the non-given cards into the non-given squares so every line keeps its label."""
    want = labels(n, grid)
    L = lines(n)
    empty = [i for i in range(n * n) if not given[i]]
    tray = [grid[i] for i in empty]
    cur = [grid[i] if given[i] else None for i in range(n * n)]
    by_cell = {i: [k for k, l in enumerate(L) if i in l] for i in range(n * n)}
    used = [False] * len(tray)
    found = [0]
    def ok(cell):
        for k in by_cell[cell]:
            cs = [cur[j] for j in L[k]]
            if None not in cs and hand(cs) != want[k]:
                return False
        return True
    def go(pos):
        if found[0] >= limit:
            return
        if pos == len(empty):
            found[0] += 1
            return
        cell = empty[pos]
        for t in range(len(tray)):
            if used[t]:
                continue
            used[t] = True; cur[cell] = tray[t]
            if ok(cell):
                go(pos + 1)
            cur[cell] = None; used[t] = False
    go(0)
    return found[0]

def deal(rng, n):
    """A grid built from a narrow slice of the deck so lines tend to make real hands."""
    lo = rng.randint(1, 13 - (n + 3))
    ranks = list(range(lo, lo + n + 3))
    suits = rng.sample(range(4), 3 if n == 3 else 4)
    pool = [r * 10 + s for r in ranks for s in suits]
    return rng.sample(pool, n * n)

def make(rng, n, max_given):
    for _ in range(4000):
        grid = deal(rng, n)
        lab = labels(n, grid)
        kinds = Counter(lab)
        if len(kinds) < (3 if n == 3 else 4) or kinds["High card"] > (1 if n == 3 else 2):
            continue
        order = list(range(n * n)); rng.shuffle(order)
        given = [False] * (n * n)
        for k in range(max_given + 1):
            if count_solutions(n, grid, given) == 1:
                return {"n": n, "grid": grid, "given": [i for i in range(n * n) if given[i]], "labels": lab}
            if k < max_given:
                given[order[k]] = True
    return None

if __name__ == "__main__":
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    for n, g in [(3, 3), (3, 2), (4, 7)]:
        print(json.dumps(make(rng, n, g)), flush=True)
