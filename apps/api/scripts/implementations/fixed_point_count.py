def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    return sum(1 for i, image in enumerate(p.array_form) if i == image)
