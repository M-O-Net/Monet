def accepts(m):
    return isinstance(m, MatrixBase) and m.is_square and all(entry.is_Rational for entry in m)


def compute(m):
    return m.trace()
