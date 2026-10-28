def accepts(a):
    return (
        isinstance(a, Tuple) and len(a) > 0 and all(isinstance(t, Expr) and t.is_number for t in a)
    )


def compute(a):
    sizes = range(1, (len(a) + 1) // 2 + 1)
    return Tuple(*(Matrix(k, k, lambda i, j: a[i + j]).det() for k in sizes))
