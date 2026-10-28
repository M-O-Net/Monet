def _invariants(curve):
    x, y = Symbol("x"), Symbol("y")
    if not isinstance(curve, Equality):
        return None
    poly = Poly(curve.lhs - curve.rhs, x, y)
    scale = poly.coeff_monomial(y**2)
    if scale == 0 or poly.coeff_monomial(x**3) != -scale:
        return None
    allowed = {(0, 2), (1, 1), (0, 1), (3, 0), (2, 0), (1, 0), (0, 0)}
    if any(monomial not in allowed for monomial in poly.monoms()):
        return None
    a = {
        1: poly.coeff_monomial(x * y) / scale,
        3: poly.coeff_monomial(y) / scale,
        2: -poly.coeff_monomial(x**2) / scale,
        4: -poly.coeff_monomial(x) / scale,
        6: -poly.coeff_monomial(1) / scale,
    }
    b2 = a[1] ** 2 + 4 * a[2]
    b4 = 2 * a[4] + a[1] * a[3]
    b6 = a[3] ** 2 + 4 * a[6]
    b8 = a[1] ** 2 * a[6] + 4 * a[2] * a[6] - a[1] * a[3] * a[4] + a[2] * a[3] ** 2 - a[4] ** 2
    return -(b2**2) * b8 - 8 * b4**3 - 27 * b6**2 + 9 * b2 * b4 * b6


def accepts(curve):
    discriminant = _invariants(curve)
    return discriminant is not None and discriminant != 0


def compute(curve):
    return _invariants(curve)
