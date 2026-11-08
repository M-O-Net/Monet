MAX_CROSSINGS = 60


def _generator(strands, letter, t):
    size = strands - 1
    i = abs(letter) - 1
    m = eye(size)
    m[i, i] = -t
    if i > 0:
        m[i, i - 1] = t
    if i < size - 1:
        m[i, i + 1] = 1
    return m if letter > 0 else m.inv()


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
    product = eye(b.strands - 1)
    for letter in b.word:
        product = (product * _generator(b.strands, letter, t)).applyfunc(cancel)
    numerator = cancel((eye(b.strands - 1) - product).det(method="berkowitz"))
    top, _ = fraction(cancel(numerator * (1 - t) / (1 - t**b.strands)))
    quotient = Poly(top, t)
    coeffs = quotient.all_coeffs()
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    if coeffs[0] < 0:
        coeffs = [-c for c in coeffs]
    x = Symbol("x")
    return sum(c * x ** (len(coeffs) - 1 - i) for i, c in enumerate(coeffs))
