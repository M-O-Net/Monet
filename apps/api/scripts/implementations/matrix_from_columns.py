def accepts(v):
    return isinstance(v, MatrixBase) and v.cols == 1


def compute(*columns):
    if not all(accepts(c) and c.rows == columns[0].rows for c in columns):
        raise ValueError("every input must be a column vector of the same height")
    return Matrix.hstack(*columns)
