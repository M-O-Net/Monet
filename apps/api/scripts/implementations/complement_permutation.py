def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    return Permutation([p.size - 1 - image for image in p.array_form])
