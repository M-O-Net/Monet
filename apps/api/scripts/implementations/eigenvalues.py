def _rational_eigenvalues(m):
    values = m.eigenvals(multiple=True)
    if not values or not all(value.is_Rational for value in values):
        return None
    return sorted(values)


def accepts(m):
    if not (isinstance(m, MatrixBase) and m.is_square):
        return False
    return _rational_eigenvalues(m) is not None


def compute(m):
    return _rational_eigenvalues(m)
