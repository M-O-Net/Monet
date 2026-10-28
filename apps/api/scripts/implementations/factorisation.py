def _polynomial(p):
    x = Symbol("x")
    if not (isinstance(p, Expr) and p.free_symbols == {x} and p.is_polynomial(x)):
        return None
    poly = Poly(p, x)
    return poly if poly.degree() >= 1 and all(c.is_Rational for c in poly.all_coeffs()) else None


def accepts(p):
    return _polynomial(p) is not None


def compute(p):
    x = Symbol("x")
    _, factors = factor_list(_polynomial(p).as_expr(), x)
    found = []
    for factor, multiplicity in factors:
        poly = Poly(factor, x)
        if poly.LC() < 0:
            poly = -poly
        found.extend([poly] * multiplicity)
    found.sort(key=lambda poly: (poly.degree(), poly.all_coeffs()))
    return [poly.as_expr() for poly in found]
