def accepts(m):
    return isinstance(m, MatrixBase) and all(entry.is_number and entry.is_real for entry in m)


def compute(m):
    return (m.T * m).applyfunc(simplify)
