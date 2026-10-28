def _polynomial(value):
    if isinstance(value, NumberField):
        value = value.polynomial
    x = Symbol("x")
    if not (isinstance(value, Expr) and value.free_symbols == {x} and value.is_polynomial(x)):
        return None
    poly = Poly(value, x)
    rational = all(c.is_Rational for c in poly.all_coeffs())
    return poly if rational and 2 <= poly.degree() <= 6 and poly.is_irreducible else None


def accepts(value):
    return _polynomial(value) is not None


def compute(value):
    name, _ = galois_group(_polynomial(value), by_name=True)
    return name.get_perm_group()
