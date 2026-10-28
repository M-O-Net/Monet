def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    images = p.array_form
    return Matrix(p.size, p.size, lambda i, j: 1 if images[j] == i else 0)
