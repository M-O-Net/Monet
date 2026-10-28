MAX_DEGREE = 8


def accepts(g):
    return isinstance(g, PermutationGroup) and g.degree <= MAX_DEGREE


def compute(g):
    return g.presentation()
