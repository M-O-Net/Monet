def _position(z):
    point = complex(N(z, 30))
    return round(point.real, 12), round(point.imag, 12)


def _diagonalizable(m):
    if not all(entry.is_Rational for entry in m):
        return m.is_diagonalizable()
    x = Symbol("x")
    squarefree = Poly(m.charpoly(x).as_expr(), x).sqf_part()
    value = zeros(m.rows, m.rows)
    for coefficient in squarefree.all_coeffs():
        value = value * m + coefficient * eye(m.rows)
    return value.is_zero_matrix


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_number and bool(entry.is_algebraic) for entry in m)
        and _diagonalizable(m)
    )


def compute(m):
    values = sorted(m.eigenvals(), key=_position)
    diagonal, columns = [], []
    for value in values:
        basis = (m - value * eye(m.rows)).nullspace(simplify=True)
        diagonal.extend([value] * len(basis))
        columns.extend(basis)
    if len(columns) < m.rows:
        raise ValueError("the eigenvectors do not span: the matrix is not diagonalizable")
    return diag(*diagonal), Matrix.hstack(*columns)
