def accepts(p):
    return not isinstance(p, (bool, MatrixBase)) and p.is_Integer and isprime(p)


def compute(p, k):
    if not (k.is_Integer and k > 0):
        raise ValueError(f"{k} is not a positive integer")
    return FiniteField(p, k)
