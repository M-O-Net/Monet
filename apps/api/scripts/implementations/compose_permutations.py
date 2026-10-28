def accepts(p):
    return isinstance(p, Permutation)


def compute(p, q):
    if p.size != q.size:
        raise ValueError(f"sizes differ: {p.size} and {q.size}")
    return p * q
