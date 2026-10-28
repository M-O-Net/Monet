def accepts(m):
    return isinstance(m, MatrixBase)


def compute(a, b):
    if not isinstance(b, MatrixBase) or a.cols != b.rows:
        raise ValueError("the first matrix needs as many columns as the second has rows")
    return a * b
