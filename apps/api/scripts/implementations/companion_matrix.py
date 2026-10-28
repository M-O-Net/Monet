def _is_polynomial_in_x(p):
    return isinstance(p, Expr) and Symbol("x") in p.free_symbols


def accepts(p):
    x = Symbol("x")
    return _is_polynomial_in_x(p) and Poly(p, x).is_monic and degree(p, x) >= 1


def compute(p):
    return Matrix.companion(Poly(p, Symbol("x")))
