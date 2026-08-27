def accepts(n):
    return not isinstance(n, (bool, MatrixBase)) and n.is_Integer and n > 0


def compute(n):
    return cyclotomic_poly(n, Symbol("x"))
