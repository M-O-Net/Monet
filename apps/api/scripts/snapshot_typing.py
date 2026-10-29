import pathlib
from typing import Any

import sympy
from seed_data.catalogue import TYPES

SANDBOX = pathlib.Path(__file__).resolve().parents[2] / "web" / "src" / "sandbox"


def load_prelude() -> dict[str, Any]:
    scope: dict[str, Any] = {"__name__": "prelude"}
    exec(compile((SANDBOX / "prelude.py").read_text(), "prelude.py", "exec"), scope)  # noqa: S102
    return scope


def _ancestors(type_key: str) -> set[str]:
    found: set[str] = set()
    for supertype in TYPES[type_key][3]:
        found |= {supertype} | _ancestors(supertype)
    return found


def most_specific(found: set[str]) -> list[str]:
    implied = set().union(*(_ancestors(t) for t in found))
    return sorted(found - implied)


def _is_jordan_form(m: sympy.Matrix) -> bool:
    size = m.rows
    for i in range(size):
        for j in range(size):
            if j not in (i, i + 1) and m[i, j] != 0:
                return False
    return all(
        m[i, i + 1] == 0 or (m[i, i + 1] == 1 and m[i, i] == m[i + 1, i + 1])
        for i in range(size - 1)
    )


def _is_companion(m: sympy.Matrix) -> bool:
    x = sympy.Symbol("x")
    return m.rows > 0 and m == sympy.Matrix.companion(sympy.Poly(m.charpoly(x).as_expr(), x))


def _is_diagonalizable(m: sympy.Matrix) -> bool:
    x = sympy.Symbol("x")
    characteristic = sympy.Poly(m.charpoly(x).as_expr(), x)
    squarefree = sympy.quo(characteristic, sympy.gcd(characteristic, characteristic.diff(x)))
    value = sympy.zeros(m.rows, m.rows)
    for c in squarefree.all_coeffs():
        value = value * m + c * sympy.eye(m.rows)
    return value.is_zero_matrix


def matrix_types(rows: list[list[int]]) -> list[str]:
    m = sympy.Matrix(rows)
    if m.rows != m.cols:
        return ["ColumnVectors"] if m.cols == 1 else ["Matrices"]
    found = {"SquareMatrices", "ColumnVectors"} if m.cols == 1 else {"SquareMatrices"}
    determinant = m.det()
    if m == m.T:
        found.add("SymmetricMatrices")
        if m.is_positive_definite:
            found.add("PositiveDefiniteMatrices")
    if m.is_diagonal():
        found.add("DiagonalMatrices")
    if _is_jordan_form(m):
        found.add("JordanNormalForms")
    if (m**m.rows).is_zero_matrix:
        found.add("NilpotentMatrices")
    if _is_diagonalizable(m):
        found.add("DiagonalizableMatrices")
    if _is_companion(m):
        found.add("CompanionMatrices")
    if determinant == 0:
        found.add("SingularMatrices")
    elif abs(determinant) == 1:
        found.add(
            "SpecialLinearIntegerMatrices" if determinant == 1 else "InvertibleIntegerMatrices"
        )
    else:
        found.add("InvertibleRationalMatrices")
    if determinant != 0 and m * m.T == sympy.eye(m.rows):
        found.add("RotationMatrices" if determinant == 1 else "OrthogonalMatrices")
        if all(sum(abs(c) for c in m.row(i)) == 1 and min(m.row(i)) >= 0 for i in range(m.rows)):
            found.add("PermutationMatrices")
    return most_specific(found)


def polynomial_types(expression: sympy.Expr, var: sympy.Symbol) -> list[str]:
    poly = sympy.Poly(expression, var)
    found = {"IntegerPolynomials"}
    if poly.LC() == 1:
        found.add("MonicIntegerPolynomials")
    if poly.degree() >= 1 and poly.is_irreducible:
        found.add("IrreduciblePolynomials")
    degree = poly.degree()
    if poly.LC() == 1 and any(
        poly == sympy.Poly(sympy.cyclotomic_poly(n, var), var)
        for n in range(1, 2 * degree * degree + 3)
    ):
        found.add("CyclotomicPolynomials")
    if poly in (
        sympy.Poly(sympy.chebyshevt(degree, var), var),
        sympy.Poly(sympy.chebyshevu(degree, var), var),
    ):
        found.add("ChebyshevPolynomials")
    return most_specific(found)
