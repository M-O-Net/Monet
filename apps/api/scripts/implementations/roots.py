def _position(z):
    point = complex(N(z, 30))
    return round(point.real, 12), round(point.imag, 12)


def _polynomial(p):
    x = Symbol("x")
    if not (isinstance(p, Expr) and p.free_symbols == {x} and p.is_polynomial(x)):
        return None
    poly = Poly(p, x)
    return poly if poly.degree() >= 1 and all(c.is_Rational for c in poly.all_coeffs()) else None


def accepts(p):
    return _polynomial(p) is not None


def compute(p):
    return sorted(_polynomial(p).all_roots(), key=_position)
