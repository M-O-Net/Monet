def accepts(a):
    return isinstance(a, Expr) and a.is_number and bool(a.is_algebraic) and not a.is_Rational


def compute(a):
    return minimal_polynomial(a, Symbol("x"))
