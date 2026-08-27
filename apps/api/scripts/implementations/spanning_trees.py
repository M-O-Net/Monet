def _is_adjacency(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and m.rows > 0
        and m == m.T
        and all(entry in (0, 1) for entry in m)
        and all(m[i, i] == 0 for i in range(m.rows))
    )


def accepts(m):
    return _is_adjacency(m)


def compute(m):
    if m.rows == 1:
        return Integer(1)
    degrees = [sum(m.row(i)) for i in range(m.rows)]
    return (diag(*degrees) - m).minor_submatrix(0, 0).det()
