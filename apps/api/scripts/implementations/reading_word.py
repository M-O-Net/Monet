def accepts(t):
    return isinstance(t, Tableau)


def compute(t):
    return Permutation([entry - 1 for row in reversed(t.rows) for entry in row])
