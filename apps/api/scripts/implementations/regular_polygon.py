def accepts(n):
    return not isinstance(n, (bool, MatrixBase)) and n.is_Integer and n >= 3


def compute(n):
    return RegularPolygon(Point(0, 0), 1, n)
