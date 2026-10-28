def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    return p.order()
