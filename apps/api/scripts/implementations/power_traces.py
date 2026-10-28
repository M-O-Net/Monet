def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_Rational for entry in m)
        and m.det() != 0
    )


def compute(m):
    n, term = Symbol("n"), Function("a")
    coefficients = m.charpoly(Symbol("x")).all_coeffs()[1:]
    rule = sum(-c * term(n - k) for k, c in enumerate(coefficients, start=1))
    traces = [(m**k).trace() for k in range(m.rows)]
    return RecursiveSeq(rule, term(n), n, traces)
