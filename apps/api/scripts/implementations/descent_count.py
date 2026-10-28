from itertools import pairwise


def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    images = p.array_form
    return sum(1 for a, b in pairwise(images) if a > b)
