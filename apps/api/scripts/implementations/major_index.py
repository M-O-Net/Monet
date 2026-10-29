from itertools import pairwise


def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    images = p.array_form
    return sum(i for i, (a, b) in enumerate(pairwise(images), start=1) if a > b)
