def accepts(n):
    return not isinstance(n, (bool, MatrixBase)) and n.is_Integer and n > 0


def compute(n):
    return Graph(n, [(u, v) for u in range(n) for v in range(u + 1, n)])
