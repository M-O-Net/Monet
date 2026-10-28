def _quadratic_minpoly(value):
    if isinstance(value, (bool, MatrixBase)) or not isinstance(value, Expr):
        return None
    if not value.is_number or value.is_Rational or value.is_algebraic is not True:
        return None
    poly = Poly(minimal_polynomial(value, Symbol("x")), Symbol("x"))
    return poly if poly.degree() == 2 else None


def accepts(value):
    return _quadratic_minpoly(value) is not None


def compute(value):
    a, b, c = _quadratic_minpoly(value).all_coeffs()
    discriminant = int(b**2 - 4 * a * c)
    squarefree = sign(discriminant) * prod(
        p for p, e in factorint(abs(discriminant)).items() if e % 2
    )
    x = Symbol("x")
    if squarefree % 4 == 1:
        return NumberField(x**2 - x + (1 - squarefree) // 4)
    return NumberField(x**2 - squarefree)
