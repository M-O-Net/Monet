def accepts(n):
    return isinstance(n, Expr) and n.is_Integer and n > 0


def compute(n):
    return divisor_count(n)
