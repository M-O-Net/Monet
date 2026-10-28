def _position(z):
    point = complex(N(z, 30))
    return round(point.real, 12), round(point.imag, 12)


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_number and bool(entry.is_algebraic) for entry in m)
    )


def compute(m):
    if all(entry.is_Rational for entry in m):
        values = Poly(m.charpoly(Symbol("x")).as_expr(), Symbol("x")).all_roots()
    else:
        values = [value for value, count in m.eigenvals().items() for _ in range(count)]
    return sorted(values, key=_position)
