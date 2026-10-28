def _position(z):
    point = complex(N(z, 30))
    return round(point.real, 12), round(point.imag, 12)


def _denominator(f):
    x = Symbol("x")
    if not (isinstance(f, Expr) and f.free_symbols == {x} and f.is_rational_function(x)):
        return None
    denominator = Poly(denom(cancel(f)), x)
    return denominator if denominator.degree() >= 1 else None


def accepts(f):
    return _denominator(f) is not None


def compute(f):
    return sorted(_denominator(f).all_roots(), key=_position)
