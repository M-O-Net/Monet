def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_integer for entry in m)
        and abs((m - m.T).det()) == 1
    )


def compute(m):
    return expand((m - Symbol("x") * m.T).det())
