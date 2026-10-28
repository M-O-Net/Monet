def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_number for entry in m)
        and (m**m.rows).applyfunc(simplify).is_zero_matrix
    )


def compute(m):
    power = m
    for k in range(1, m.rows + 1):
        if power.applyfunc(simplify).is_zero_matrix:
            return k
        power = power * m
    raise ValueError("the matrix is not nilpotent")
