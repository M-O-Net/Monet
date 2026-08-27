def _is_seifert_matrix(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_integer for entry in m)
        and abs((m - m.T).det()) == 1
    )


def _is_alexander_polynomial(p):
    x = Symbol("x")
    if isinstance(p, (bool, MatrixBase)) or getattr(p, "free_symbols", set()) != {x}:
        return False
    return Poly(p, x).is_univariate and abs(p.subs(x, 1)) == 1


def accepts(v):
    return _is_seifert_matrix(v) if isinstance(v, MatrixBase) else _is_alexander_polynomial(v)


def compute(v):
    if isinstance(v, MatrixBase):
        return abs((v + v.T).det())
    return abs(v.subs(Symbol("x"), -1))
