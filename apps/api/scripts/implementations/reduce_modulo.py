def accepts(a):
    return isinstance(a, Expr) and a.is_Integer


def compute(a, n):
    if not (isinstance(n, Expr) and n.is_Integer and n > 0):
        raise ValueError("the modulus must be a positive integer")
    return residue(int(a) % int(n), int(n))
