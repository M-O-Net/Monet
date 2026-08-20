def accepts(m):
    return isinstance(m, MatrixBase) and m.is_square


def compute(m):
    return m.charpoly(Symbol("x")).as_expr()
