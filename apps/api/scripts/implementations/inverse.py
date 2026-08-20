def accepts(m):
    return isinstance(m, MatrixBase) and m.is_square and m.det() != 0


def compute(m):
    return m.inv()
