def accepts(f):
    return isinstance(f, Expr) and f.free_symbols == {Symbol("x")}


def compute(f, n):
    if not (isinstance(n, Expr) and n.is_Integer and n > 0):
        raise ValueError("the degree must be a positive integer")
    x = Symbol("x")
    return expand(series(f, x, 0, int(n) + 1).removeO())
