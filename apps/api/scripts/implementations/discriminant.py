def _polynomial(p):
    x = Symbol("x")
    if not (isinstance(p, Expr) and p.free_symbols == {x} and p.is_polynomial(x)):
        return None
    poly = Poly(p, x)
    return poly if poly.degree() >= 1 and all(c.is_Rational for c in poly.all_coeffs()) else None


def accepts(p):
    return _polynomial(p) is not None


def compute(p):
    return discriminant(_polynomial(p))
