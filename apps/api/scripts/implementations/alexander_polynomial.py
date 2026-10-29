def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_integer for entry in m)
        and abs((m - m.T).det()) == 1
    )


def compute(m):
    values = [(k, (m - k * m.T).det()) for k in range(m.rows + 1)]
    return expand(interpolate(values, Symbol("x")))
