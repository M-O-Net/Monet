def accepts(m):
    return isinstance(m, MatrixBase)


def compute(a, b):
    if a.shape != b.shape:
        raise ValueError(f"shapes differ: {a.shape} and {b.shape}")
    return a + b
