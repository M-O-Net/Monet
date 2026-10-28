def accepts(a):
    return (
        isinstance(a, Tuple)
        and len(a) % 2 == 1
        and all(isinstance(term, Expr) and term.is_number for term in a)
    )


def compute(a):
    size = (len(a) + 1) // 2
    return Matrix(size, size, lambda i, j: a[i + j])
