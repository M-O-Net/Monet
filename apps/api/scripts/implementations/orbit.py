def accepts(g):
    return isinstance(g, PermutationGroup)


def compute(g, point):
    if not (point.is_Integer and 0 <= point < g.degree):
        raise ValueError(f"{point} is not one of the {g.degree} points the group permutes")
    return Tuple(*sorted(g.orbit(int(point))))
