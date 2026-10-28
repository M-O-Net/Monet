def accepts(shape):
    return isinstance(shape, Polygon)


def compute(shape):
    return simplify(abs(shape.area))
