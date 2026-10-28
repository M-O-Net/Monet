def _quadratic(p):
    x = Symbol("x")
    if not (isinstance(p, Expr) and p.free_symbols == {x} and p.is_polynomial(x)):
        return None
    poly = Poly(p, x)
    rational = all(c.is_Rational for c in poly.all_coeffs())
    return poly if rational and poly.degree() == 2 and poly.is_irreducible else None


def accepts(p):
    return _quadratic(p) is not None


def compute(p):
    x = Symbol("x")
    a, b, c = _quadratic(p).all_coeffs()
    disc = Rational(b**2 - 4 * a * c)
    whole = disc.p * disc.q
    d = sign(whole) * prod(prime ** (e % 2) for prime, e in factorint(abs(whole)).items())
    if d % 4 == 1:
        return NumberField(x**2 - x + (1 - d) / 4)
    return NumberField(x**2 - d)
