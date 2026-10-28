def accepts(a):
    return isinstance(a, Expr) and a.is_number and bool(a.is_algebraic) and not a.is_Rational


def compute(a):
    x = Symbol("x")
    minimal = Poly(minimal_polynomial(a, x), x)
    return (-1) ** minimal.degree() * minimal.TC() / minimal.LC()
