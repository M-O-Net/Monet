TERMS = 36


def _values(f):
    return [f.formula.subs(f.variables[0], k) for k in range(1, TERMS + 1)]


def _known():
    n = Symbol("n")
    return [
        Integer(1),
        n,
        n**2,
        KroneckerDelta(1, n),
        totient(n),
        mobius(n),
        divisor_sigma(n, 0),
        divisor_sigma(n),
        divisor_sigma(n, 2),
        2 ** primenu(n),
        Abs(mobius(n)),
    ]


def accepts(f):
    if not (isinstance(f, SeqFormula) and f.start == 1):
        return False
    return all(f.formula.subs(f.variables[0], k).is_integer for k in range(1, 7))


def compute(f, g):
    if not accepts(g):
        raise ValueError("both inputs must be arithmetic functions starting at n = 1")
    fv, gv = _values(f), _values(g)
    convolved = [sum(fv[d - 1] * gv[k // d - 1] for d in divisors(k)) for k in range(1, TERMS + 1)]
    n = Symbol("n")
    for formula in _known():
        if [formula.subs(n, k) for k in range(1, TERMS + 1)] == convolved:
            return SeqFormula(formula, (n, 1, oo))
    raise ValueError(f"no known arithmetic function starts {convolved[:8]}")
