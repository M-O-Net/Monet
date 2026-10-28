from itertools import pairwise


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_integer for entry in m)
        and abs((m - m.T).det()) == 1
    )


def _sign_changes(coefficients):
    signs = [c > 0 for c in coefficients if c != 0]
    return sum(1 for a, b in pairwise(signs) if a != b)


def compute(m):
    x = Symbol("x")
    characteristic = Poly((m + m.T).charpoly(x).as_expr(), x)
    positive = _sign_changes(characteristic.all_coeffs())
    negative = _sign_changes(Poly(characteristic.as_expr().subs(x, -x), x).all_coeffs())
    return positive - negative
