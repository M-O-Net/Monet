MAX_ORDER = 12


def _order(m):
    power = eye(m.rows)
    for k in range(1, MAX_ORDER + 1):
        power = power * m
        if power == eye(m.rows):
            return k
    return None


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_integer for entry in m)
        and abs(m.det()) == 1
        and _order(m) is not None
    )


def compute(m):
    return _order(m)
