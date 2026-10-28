def accepts(p):
    return isinstance(p, Permutation)


def compute(p, point):
    if not (point.is_Integer and 0 <= point < p.size):
        raise ValueError(f"{point} is not one of the {p.size} points p permutes")
    return p(int(point))
