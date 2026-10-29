from collections import Counter
from itertools import product

MAX_CROSSINGS = 12


def _find(parent, point):
    while parent[point] != point:
        parent[point] = parent[parent[point]]
        point = parent[point]
    return point


def _arcs(strands, word):
    levels = len(word)
    parent = list(range(levels * strands))
    smoothings = []
    for level, letter in enumerate(word):
        left = abs(letter) - 1
        here, below = level * strands, (level + 1) % levels * strands
        for position in range(strands):
            if position not in (left, left + 1):
                parent[_find(parent, here + position)] = _find(parent, below + position)
        vertical = ((here + left, below + left), (here + left + 1, below + left + 1))
        horizontal = ((here + left, here + left + 1), (below + left, below + left + 1))
        smoothings.append((vertical, horizontal) if letter > 0 else (horizontal, vertical))
    return [_find(parent, point) for point in range(levels * strands)], smoothings


def _loop_counts(strands, word):
    arcs, smoothings = _arcs(strands, word)
    ends = set(arcs)
    counts = Counter()
    for state in product((0, 1), repeat=len(word)):
        parent = arcs.copy()
        for options, choice in zip(smoothings, state, strict=True):
            for u, v in options[choice]:
                parent[_find(parent, u)] = _find(parent, v)
        counts[len(word) - 2 * sum(state), sum(1 for end in ends if parent[end] == end)] += 1
    return counts


def accepts(b):
    return isinstance(b, Braid) and 0 < len(b.word) <= MAX_CROSSINGS


def compute(b):
    a, t = Symbol("A"), Symbol("t")
    loop = -(a**2) - a**-2
    bracket = sum(
        count * a**power * loop ** (loops - 1)
        for (power, loops), count in _loop_counts(b.strands, b.word).items()
    )
    writhe = sum(1 if letter > 0 else -1 for letter in b.word)
    return expand(expand((-(a**3)) ** -writhe * bracket).subs(a, t ** Rational(-1, 4)))
