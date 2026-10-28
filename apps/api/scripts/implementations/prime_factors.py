def accepts(n):
    return isinstance(n, Expr) and n.is_Integer and n > 1


def compute(n):
    return [p for p, e in sorted(factorint(n).items()) for _ in range(e)]
