def accepts(m):
    return isinstance(m, MatrixBase) and all(entry.is_number for entry in m)


def compute(m):
    return m.rank(simplify=True)
