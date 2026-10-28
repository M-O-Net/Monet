def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    return Permutation(p.array_form[::-1])
