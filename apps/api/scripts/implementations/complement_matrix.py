def _is_adjacency(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and m.rows > 1
        and m == m.T
        and all(entry in (0, 1) for entry in m)
        and all(m[i, i] == 0 for i in range(m.rows))
    )


def accepts(m):
    return _is_adjacency(m)


def compute(m):
    return ones(m.rows, m.rows) - eye(m.rows) - m
