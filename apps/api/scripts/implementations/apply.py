def accepts(m):
    return isinstance(m, MatrixBase)


def compute(m, v):
    if not isinstance(v, MatrixBase) or v.cols != 1 or v.rows != m.cols:
        raise ValueError(f"the second input must be a column vector with {m.cols} entries")
    return m * v
