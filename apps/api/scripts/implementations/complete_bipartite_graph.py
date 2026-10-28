def accepts(m):
    return not isinstance(m, (bool, MatrixBase)) and m.is_Integer and m > 0


def compute(m, n):
    if not (n.is_Integer and n > 0):
        raise ValueError(f"{n} is not a positive integer")
    return Graph(m + n, [(u, v) for u in range(m) for v in range(m, m + n)])
