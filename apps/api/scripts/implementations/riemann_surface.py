def _homogeneous(curve):
    x, y, z = Symbol("x"), Symbol("y"), Symbol("z")
    poly = Poly(curve.lhs - curve.rhs, x, y)
    degree = poly.total_degree()
    form = sum(c * x**i * y**j * z ** (degree - i - j) for (i, j), c in poly.terms())
    return degree, [form.diff(v) for v in (x, y, z)]


def _smooth(curve):
    x, y, z = Symbol("x"), Symbol("y"), Symbol("z")
    _, partials = _homogeneous(curve)
    affine = groebner([p.subs(z, 1) for p in partials], x, y)
    at_infinity = groebner([p.subs({z: 0, y: 1}) for p in partials], x)
    corner = [p.subs({x: 1, y: 0, z: 0}) for p in partials]
    return list(affine) == [1] and list(at_infinity) == [1] and any(c != 0 for c in corner)


def accepts(curve):
    return isinstance(curve, Equality) and len(curve.free_symbols) == 2 and _smooth(curve)


def compute(curve):
    degree, _ = _homogeneous(curve)
    return Surface(True, (degree - 1) * (degree - 2) // 2)
