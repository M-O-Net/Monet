from itertools import product

MAX_CROSSINGS = 12


def _loops(strands, word, state):
    parent = {}

    def find(point):
        while parent.setdefault(point, point) != point:
            point = parent[point]
        return point

    def join(a, b):
        parent[find(a)] = find(b)

    levels = len(word)
    for level, (letter, a_smoothing) in enumerate(zip(word, state, strict=True)):
        left = abs(letter) - 1
        below = (level + 1) % levels
        for position in range(strands):
            if position not in (left, left + 1):
                join((level, position), (below, position))
        if a_smoothing == (letter > 0):
            join((level, left), (below, left))
            join((level, left + 1), (below, left + 1))
        else:
            join((level, left), (level, left + 1))
            join((below, left), (below, left + 1))
    return len({find((level, position)) for level in range(levels) for position in range(strands)})


def accepts(b):
    return isinstance(b, Braid) and 0 < len(b.word) <= MAX_CROSSINGS


def compute(b):
    a, t = Symbol("A"), Symbol("t")
    loop = -(a**2) - a**-2
    bracket = sum(
        a ** sum(1 if smoothing else -1 for smoothing in state)
        * loop ** (_loops(b.strands, b.word, state) - 1)
        for state in product((True, False), repeat=len(b.word))
    )
    writhe = sum(1 if letter > 0 else -1 for letter in b.word)
    return expand(expand((-(a**3)) ** -writhe * bracket).subs(a, t ** Rational(-1, 4)))
