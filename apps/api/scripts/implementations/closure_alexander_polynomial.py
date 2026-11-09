from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix

MAX_CROSSINGS = 60


def _closes_to_a_knot(b):
    position = list(range(b.strands))
    for letter in b.word:
        left = abs(letter) - 1
        position[left], position[left + 1] = position[left + 1], position[left]
    seen, start = {0}, position[0]
    while start not in seen:
        seen.add(start)
        start = position[start]
    return len(seen) == b.strands


def accepts(b):
    return (
        isinstance(b, Braid)
        and b.strands > 1
        and len(b.word) <= MAX_CROSSINGS
        and _closes_to_a_knot(b)
    )


def compute(b):
    t = Symbol("t")
    ring = ZZ[t]
    size = b.strands - 1
    one, zero, tt = ring.one, ring.zero, ring.gens[0]
    product = DomainMatrix.eye(size, ring)
    inverses = 0
    for letter in b.word:
        i = abs(letter) - 1
        rows = [[one if r == c else zero for c in range(size)] for r in range(size)]
        if letter > 0:
            rows[i][i] = -tt
            if i > 0:
                rows[i][i - 1] = tt
            if i < size - 1:
                rows[i][i + 1] = one
        else:
            inverses += 1
            rows = [[tt if r == c else zero for c in range(size)] for r in range(size)]
            rows[i][i] = -one
            if i > 0:
                rows[i][i - 1] = tt
            if i < size - 1:
                rows[i][i + 1] = one
        product = product * DomainMatrix(rows, (size, size), ring)
    scaled = DomainMatrix.eye(size, ring) * (tt**inverses) - product
    numerator = ring.to_sympy(scaled.det())
    top, _ = fraction(cancel(numerator * (1 - t) / (1 - t**b.strands)))
    coeffs = Poly(top, t).all_coeffs()
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    if coeffs[0] < 0:
        coeffs = [-c for c in coeffs]
    x = Symbol("x")
    return sum(c * x ** (len(coeffs) - 1 - i) for i, c in enumerate(coeffs))
