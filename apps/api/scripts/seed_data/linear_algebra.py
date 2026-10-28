from fractions import Fraction

from seed_data.build import (
    HALF_SQRT2_CELL,
    HALF_SQRT3_CELL,
    I_CELL,
    MINUS_HALF_SQRT2_CELL,
    MINUS_HALF_SQRT3_CELL,
    SQRT2_CELL,
    SQRT3_CELL,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    algebraic,
    fraction,
    matrix_instance,
    seifert,
)

MINUS_I_CELL = ("- i", algebraic([1, 0, 1], 0))
PSI_CELL = (r"\frac{1}{2} - \frac{\sqrt{5}}{2}", algebraic([-1, -1, 1], 0))
PHI_CELL = (r"\frac{1}{2} + \frac{\sqrt{5}}{2}", algebraic([-1, -1, 1], 1))

INSTANCES: dict[str, Instance] = {
    "A": matrix_instance(
        [[2, 1], [1, 2]], ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"]
    ),
    "B": matrix_instance(
        [[1, 0], [0, 1]],
        [
            "DiagonalMatrices",
            "PositiveDefiniteMatrices",
            "PermutationMatrices",
            "RotationMatrices",
            "SpecialLinearIntegerMatrices",
        ],
        "The identity.",
    ),
    "D": matrix_instance(
        [[0, 1], [1, 0]],
        ["SymmetricMatrices", "PermutationMatrices", "CompanionMatrices"],
    ),
    "E": matrix_instance(
        [[3, 1], [1, 3]], ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"]
    ),
    "C": matrix_instance(
        [[0, -3], [1, 4]],
        ["CompanionMatrices", "InvertibleRationalMatrices", "DiagonalizableMatrices"],
        "The companion matrix of "
        r"$x^{2} - 4 x + 3$ — its own characteristic polynomial closes the loop.",
    ),
    "V3": matrix_instance(
        seifert(2),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        "The Seifert matrix of the trefoil.",
    ),
    "V5": matrix_instance(
        seifert(4),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        r"The Seifert matrix of $5_1$.",
    ),
    "V7": matrix_instance(
        seifert(6),
        ["JordanNormalForms", "SpecialLinearIntegerMatrices"],
        r"The Seifert matrix of $7_1$.",
    ),
    "S": matrix_instance(
        [[1, 2], [2, 4]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
        "Singular: its rows are proportional, so it collapses the plane onto a line.",
    ),
    "CompPhi6": matrix_instance(
        [[0, -1], [1, 1]],
        ["CompanionMatrices", "SpecialLinearIntegerMatrices", "DiagonalizableMatrices"],
        r"The companion matrix of $x^{2} - x + 1$ — the trefoil's polynomial, "
        "back in linear algebra.",
    ),
    "wide": matrix_instance([[1, 2, 3], [4, 5, 6]], ["Matrices"]),
    "tall": matrix_instance([[1, 0], [0, 1], [1, 1]], ["Matrices"]),
    "row": matrix_instance([[1, 2]], ["Matrices"], "A row vector."),
    "e1": matrix_instance([[1], [0]], ["ColumnVectors"]),
    "e2": matrix_instance([[0], [1]], ["ColumnVectors"]),
    "v123": matrix_instance([[1], [2], [3]], ["ColumnVectors"]),
    "cartan_a2": matrix_instance(
        [[2, -1], [-1, 2]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
        r"The Cartan matrix of $\mathfrak{sl}_{3}$.",
    ),
    "cat_map": matrix_instance(
        [[2, 1], [1, 1]],
        ["PositiveDefiniteMatrices", "SpecialLinearIntegerMatrices"],
        "Arnold's cat map on the torus.",
    ),
    "cat_map_inverse": matrix_instance(
        [[1, -1], [-1, 2]], ["PositiveDefiniteMatrices", "SpecialLinearIntegerMatrices"]
    ),
    "diag12": matrix_instance(
        [[1, 0], [0, 2]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "zero2": matrix_instance(
        [[0, 0], [0, 0]], ["DiagonalMatrices", "NilpotentMatrices"], "The zero matrix."
    ),
    "reflection": matrix_instance(
        [[1, 0], [0, -1]],
        ["DiagonalMatrices", "OrthogonalMatrices", "InvertibleIntegerMatrices"],
        "Reflection in the horizontal axis.",
    ),
    "shear": matrix_instance(
        [[1, 1], [0, 1]], ["JordanNormalForms", "SpecialLinearIntegerMatrices"]
    ),
    "nilpotent_block": matrix_instance(
        [[0, 1], [0, 0]], ["JordanNormalForms", "NilpotentMatrices"]
    ),
    "jordan3": matrix_instance(
        [[2, 1, 0], [0, 2, 0], [0, 0, 3]], ["JordanNormalForms", "InvertibleRationalMatrices"]
    ),
    "nilpotent_block3": matrix_instance(
        [[0, 1, 0], [0, 0, 1], [0, 0, 0]], ["JordanNormalForms", "NilpotentMatrices"]
    ),
    "nilpotent_dense": matrix_instance(
        [[2, -4], [1, -2]], ["NilpotentMatrices"], "Squares to zero, with no zero entry."
    ),
    "nilpotent_symmetric": matrix_instance(
        [[1, I_CELL], [I_CELL, -1]],
        ["SymmetricMatrices", "NilpotentMatrices"],
        "Symmetric yet not diagonalizable — possible only with complex entries.",
    ),
    "upper_triangular": matrix_instance(
        [[1, 1], [0, 2]], ["DiagonalizableMatrices", "InvertibleRationalMatrices"]
    ),
    "real_upper_triangular": matrix_instance(
        [[2, SQRT3_CELL], [0, 1]], ["DiagonalizableMatrices", "InvertibleRealMatrices"]
    ),
    "singular3": matrix_instance(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]], ["SingularMatrices", "DiagonalizableMatrices"]
    ),
    "ones2": matrix_instance(
        [[1, 1], [1, 1]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
    ),
    "complex_shear": matrix_instance([[1, I_CELL], [0, 1]], ["InvertibleMatrices"]),
    "complex_symmetric": matrix_instance(
        [[0, I_CELL], [I_CELL, 0]],
        ["SymmetricMatrices", "DiagonalizableMatrices", "InvertibleMatrices"],
    ),
    "complex_jordan": matrix_instance(
        [[I_CELL, 1], [0, I_CELL]], ["JordanNormalForms", "InvertibleMatrices"]
    ),
    "real_shear": matrix_instance([[1, SQRT2_CELL], [0, 1]], ["InvertibleRealMatrices"]),
    "real_positive_definite": matrix_instance(
        [[SQRT2_CELL, 1], [1, SQRT2_CELL]], ["PositiveDefiniteMatrices"]
    ),
    "fibonacci_matrix": matrix_instance(
        [[1, 1], [1, 0]],
        ["SymmetricMatrices", "InvertibleIntegerMatrices", "DiagonalizableMatrices"],
        r"Its $n$th power holds the Fibonacci numbers $F_{n+1}, F_{n}, F_{n-1}$.",
    ),
    "rational_reflection": matrix_instance(
        [[fraction(3, 5), fraction(4, 5)], [fraction(4, 5), fraction(-3, 5)]],
        ["SymmetricMatrices", "OrthogonalMatrices", "InvertibleRationalMatrices"],
    ),
    "rotation90": matrix_instance(
        [[0, -1], [1, 0]],
        ["RotationMatrices", "SpecialLinearIntegerMatrices", "CompanionMatrices"],
        "A quarter turn.",
    ),
    "rational_rotation": matrix_instance(
        [[fraction(3, 5), fraction(-4, 5)], [fraction(4, 5), fraction(3, 5)]],
        ["RotationMatrices", "InvertibleRationalMatrices"],
        "Rotation through the angle of a 3-4-5 triangle.",
    ),
    "rotation45": matrix_instance(
        [[HALF_SQRT2_CELL, MINUS_HALF_SQRT2_CELL], [HALF_SQRT2_CELL, HALF_SQRT2_CELL]],
        ["RotationMatrices"],
        "An eighth of a turn.",
    ),
    "cycle3": matrix_instance(
        [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
        [
            "PermutationMatrices",
            "RotationMatrices",
            "SpecialLinearIntegerMatrices",
            "CompanionMatrices",
        ],
        r"Cycles the coordinate axes: a third of a turn about $(1, 1, 1)$.",
    ),
    "swap3": matrix_instance(
        [[0, 1, 0], [1, 0, 0], [0, 0, 1]], ["SymmetricMatrices", "PermutationMatrices"]
    ),
    "hankel_catalan": matrix_instance(
        [[1, 1, 2, 5], [1, 2, 5, 14], [2, 5, 14, 42], [5, 14, 42, 132]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
        "The Hankel matrix of the Catalan numbers: every leading minor is 1.",
    ),
    "hankel_central_binomials": matrix_instance(
        [[1, 2, 6], [2, 6, 20], [6, 20, 70]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "hankel_fibonacci": matrix_instance(
        [[1, 1, 2], [1, 2, 3], [2, 3, 5]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
        "Singular: each row past the second is the sum of the two above it.",
    ),
    "hankel_factorials": matrix_instance(
        [[1, 2, 6], [2, 6, 24], [6, 24, 120]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "hankel_primes": matrix_instance(
        [[2, 3, 5], [3, 5, 7], [5, 7, 11]],
        ["SymmetricMatrices", "DiagonalizableMatrices", "InvertibleRationalMatrices"],
    ),
    "inverse_A": matrix_instance(
        [[fraction(2, 3), fraction(-1, 3)], [fraction(-1, 3), fraction(2, 3)]],
        ["PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "rotation_minus90": matrix_instance(
        [[0, 1], [-1, 0]],
        ["RotationMatrices", "SpecialLinearIntegerMatrices"],
        "A quarter turn clockwise.",
    ),
    "rational_rotation_inverse": matrix_instance(
        [[fraction(3, 5), fraction(4, 5)], [fraction(-4, 5), fraction(3, 5)]],
        ["RotationMatrices", "InvertibleRationalMatrices"],
    ),
    "fibonacci_inverse": matrix_instance(
        [[0, 1], [1, -1]],
        ["SymmetricMatrices", "InvertibleIntegerMatrices", "DiagonalizableMatrices"],
    ),
    "jordan3_inverse": matrix_instance(
        [[fraction(1, 2), fraction(-1, 4), 0], [0, fraction(1, 2), 0], [0, 0, fraction(1, 3)]],
        ["InvertibleRationalMatrices"],
    ),
    "complex_shear_inverse": matrix_instance([[1, MINUS_I_CELL], [0, 1]], ["InvertibleMatrices"]),
    "rotation45_inverse": matrix_instance(
        [[HALF_SQRT2_CELL, HALF_SQRT2_CELL], [MINUS_HALF_SQRT2_CELL, HALF_SQRT2_CELL]],
        ["RotationMatrices"],
    ),
    "half_third": matrix_instance(
        [[1, fraction(1, 2)], [fraction(1, 3), 1]],
        ["InvertibleRationalMatrices", "DiagonalizableMatrices"],
    ),
    "sqrt2_diagonal": matrix_instance(
        [[SQRT2_CELL, 0], [0, 1]], ["DiagonalMatrices", "PositiveDefiniteMatrices"]
    ),
    "wide_doubled": matrix_instance([[2, 4, 6], [8, 10, 12]], ["Matrices"]),
    "ones_column": matrix_instance([[1], [1]], ["ColumnVectors"]),
    "order3_companion": matrix_instance(
        [[0, -1], [1, -1]],
        ["CompanionMatrices", "SpecialLinearIntegerMatrices", "DiagonalizableMatrices"],
        r"The companion matrix of $x^{2} + x + 1$: a rotation of order 3 in disguise.",
    ),
    "golden_companion": matrix_instance(
        [[0, 1], [1, 1]],
        [
            "SymmetricMatrices",
            "InvertibleIntegerMatrices",
            "DiagonalizableMatrices",
            "CompanionMatrices",
        ],
        r"The companion matrix of $x^{2} - x - 1$, conjugate to the Fibonacci matrix by the "
        "swap.",
    ),
    "fibonacci_cubed": matrix_instance(
        [[3, 2], [2, 1]],
        ["SymmetricMatrices", "InvertibleIntegerMatrices", "DiagonalizableMatrices"],
        r"$F_{4}, F_{3}, F_{2}$.",
    ),
    "wide_times_tall": matrix_instance(
        [[4, 5], [10, 11]], ["InvertibleRationalMatrices", "DiagonalizableMatrices"]
    ),
    "tall_times_wide": matrix_instance(
        [[1, 2, 3], [4, 5, 6], [5, 7, 9]], ["SingularMatrices", "DiagonalizableMatrices"]
    ),
    "minus_identity": matrix_instance(
        [[-1, 0], [0, -1]],
        ["DiagonalMatrices", "RotationMatrices", "SpecialLinearIntegerMatrices"],
        "A half turn.",
    ),
    "cycle3_inverse": matrix_instance(
        [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
        ["PermutationMatrices", "RotationMatrices", "SpecialLinearIntegerMatrices"],
    ),
    "wide_transpose": matrix_instance([[1, 4], [2, 5], [3, 6]], ["Matrices"]),
    "column12": matrix_instance([[1], [2]], ["ColumnVectors"]),
    "shear_transpose": matrix_instance([[1, 0], [1, 1]], ["SpecialLinearIntegerMatrices"]),
    "gram_wide": matrix_instance(
        [[17, 22, 27], [22, 29, 36], [27, 36, 45]],
        ["SymmetricMatrices", "SingularMatrices", "DiagonalizableMatrices"],
    ),
    "shear_gram": matrix_instance(
        [[1, 1], [1, 2]], ["PositiveDefiniteMatrices", "SpecialLinearIntegerMatrices"]
    ),
    "rotation60": matrix_instance(
        [[fraction(1, 2), MINUS_HALF_SQRT3_CELL], [HALF_SQRT3_CELL, fraction(1, 2)]],
        ["RotationMatrices"],
        "A sixth of a turn.",
    ),
    "jordan_mixed": matrix_instance(
        [[2, 0, 0], [0, 2, 0], [0, 0, 3]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
        "The same characteristic polynomial as the Jordan block beside it, but not similar to it.",
    ),
    "jordan3_reordered": matrix_instance(
        [[3, 0, 0], [0, 2, 1], [0, 0, 2]], ["JordanNormalForms", "InvertibleRationalMatrices"]
    ),
    "diag13": matrix_instance(
        [[1, 0], [0, 3]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "diag23": matrix_instance(
        [[2, 0], [0, 3]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "diag24": matrix_instance(
        [[2, 0], [0, 4]],
        ["DiagonalMatrices", "PositiveDefiniteMatrices", "InvertibleRationalMatrices"],
    ),
    "diag05": matrix_instance([[0, 0], [0, 5]], ["DiagonalMatrices", "SingularMatrices"]),
    "fibonacci_eigenvalues_diagonal": matrix_instance(
        [[PSI_CELL, 0], [0, PHI_CELL]], ["DiagonalMatrices", "InvertibleRealMatrices"]
    ),
    "rotation90_diagonal": matrix_instance(
        [[MINUS_I_CELL, 0], [0, I_CELL]], ["DiagonalMatrices", "InvertibleMatrices"]
    ),
    "eigenbasis_A": matrix_instance(
        [[-1, 1], [1, 1]],
        ["SymmetricMatrices", "InvertibleRationalMatrices", "DiagonalizableMatrices"],
    ),
    "eigenbasis_C": matrix_instance(
        [[-3, -1], [1, 1]], ["InvertibleRationalMatrices", "DiagonalizableMatrices"]
    ),
    "eigenbasis_S": matrix_instance(
        [[-2, fraction(1, 2)], [1, 1]], ["InvertibleRationalMatrices", "DiagonalizableMatrices"]
    ),
    "fibonacci_eigenbasis": matrix_instance(
        [[PSI_CELL, PHI_CELL], [1, 1]], ["InvertibleRealMatrices", "DiagonalizableMatrices"]
    ),
    "rotation90_eigenbasis": matrix_instance(
        [[MINUS_I_CELL, I_CELL], [1, 1]], ["InvertibleMatrices", "DiagonalizableMatrices"]
    ),
    "kernel_S": matrix_instance([[-2], [1]], ["ColumnVectors"]),
    "kernel_123": matrix_instance([[1], [-2], [1]], ["ColumnVectors"]),
    "kernel_ones": matrix_instance([[-1], [1]], ["ColumnVectors"]),
    "kernel_hankel_fibonacci": matrix_instance([[-1], [-1], [1]], ["ColumnVectors"]),
    "column21": matrix_instance([[2], [1]], ["ColumnVectors"]),
    "minus_e1": matrix_instance([[-1], [0]], ["ColumnVectors"]),
    "column312": matrix_instance([[3], [1], [2]], ["ColumnVectors"]),
    "column_14_32": matrix_instance([[14], [32]], ["ColumnVectors"]),
    "zero_column": matrix_instance([[0], [0]], ["ColumnVectors"]),
    "v123_twice": matrix_instance([[1, 1], [2, 2], [3, 3]], ["Matrices"]),
}

SECTIONS: dict[str, Specimen] = {
    "MatrixOperations": (
        r"\text{Matrix Operations}",
        "Operations taking matrices as "
        "their input: characteristic polynomials, inverses, "
        "determinants, sums.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "CharacteristicPolynomial": (
        r"\text{Characteristic Polynomial}",
        "For a matrix A, the polynomial det(xI - A).",
    ),
    "Inverse": (
        r"\text{Inverse}",
        "The multiplicative inverse of a matrix, when one exists.",
    ),
    "Determinant": (r"\text{Determinant}", "The scalar determinant of a matrix."),
    "Add": (r"\text{Add}", "The entrywise sum of two matrices of the same shape."),
    "MatrixOrder": (
        r"\text{Matrix Order}",
        "How many times a matrix must be multiplied by itself to reach the identity. "
        "Only some matrices ever get there.",
    ),
    "Eigenvalues": (
        r"\text{Eigenvalues}",
        "The values a matrix merely scales its eigenvectors by, one output each.",
    ),
    "IsSingular": (r"\text{Is Singular}", "Whether a matrix's determinant is zero."),
    "Trace": (r"\text{Trace}", "The sum of a square matrix's diagonal entries."),
    "Rank": (r"\text{Rank}", "The dimension of the space a matrix's columns span."),
    "Transpose": (r"\text{Transpose}", "The matrix reflected in its diagonal."),
    "Multiply": (
        r"\text{Multiply}",
        "The matrix product, first input on the left. Order matters.",
    ),
    "JordanNormalForm": (
        r"\text{Jordan Normal Form}",
        "The Jordan matrix a square matrix is similar to, its blocks ordered by eigenvalue "
        "(real part, then imaginary part) and largest first. Two matrices are similar exactly "
        "when they share it. The conjugating matrix is not unique, so it is left out.",
    ),
    "Diagonalise": (
        r"\text{Diagonalise}",
        r"For a diagonalizable $A$, the diagonal $D$ and the invertible $P$ with "
        r"$A = P D P^{-1}$: eigenvalues ordered by real part, then imaginary part, and each "
        "eigenspace spanned by its reduced-row-echelon basis.",
    ),
    "NilpotencyIndex": (
        r"\text{Nilpotency Index}",
        r"The least $k$ with $N^{k} = 0$: the size of the largest Jordan block.",
    ),
    "NullSpace": (
        r"\text{Null Space}",
        "A basis of the vectors a matrix sends to zero, one output each, read off the "
        "reduced row echelon form.",
    ),
    "GramMatrix": (r"\text{Gram Matrix}", r"$A^{T} A$, the inner products of the columns."),
    "RotationByAngle": (
        r"\text{Rotation by Angle}",
        r"The rotation of the plane through the angle $\theta$.",
    ),
    "MatrixMinimalPolynomial": (
        r"\text{Minimal Polynomial of a Matrix}",
        "The monic polynomial of least degree the matrix satisfies. It divides the "
        "characteristic polynomial.",
    ),
    "Cokernel": (
        r"\text{Cokernel}",
        r"For an integer $m \times n$ matrix $A$, the abelian group "
        r"$\mathbb{Z}^{m} / A \mathbb{Z}^{n}$, "
        "read from the Smith normal form.",
    ),
    "PowerTraces": (
        r"\text{Power Traces}",
        r"The sequence $\operatorname{tr}(A^{n})$. By Cayley-Hamilton it satisfies the "
        "recurrence the characteristic polynomial spells out.",
    ),
    "Apply": (
        r"\text{Apply}",
        r"A matrix acting on a column vector: $(A, v) \mapsto A v$.",
    ),
    "MatrixFromColumns": (
        r"\text{Matrix from Columns}",
        "The matrix whose columns are the given vectors: the inverse of Apply on a basis, "
        "since a linear map is fixed by where it sends each basis vector.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("CharacteristicPolynomial", "Matrices", "Polynomials"),
    ("CharacteristicPolynomial", "SquareMatrices", "Polynomials"),
    ("Inverse", "Matrices", "Matrices"),
    ("Inverse", "SymmetricMatrices", "SymmetricMatrices"),
    ("Inverse", "InvertibleRationalMatrices", "InvertibleRationalMatrices"),
    ("Inverse", "InvertibleIntegerMatrices", "InvertibleIntegerMatrices"),
    ("Inverse", "OrthogonalMatrices", "OrthogonalMatrices"),
    ("Determinant", "Matrices", "Integers"),
    ("Determinant", "SquareMatrices", "RationalNumbers"),
    ("Determinant", "SquareMatrices", "AlgebraicNumbers"),
    ("Determinant", "SquareMatrices", "Expressions"),
    ("Add", "Matrices", "Matrices"),
    ("IsSingular", "Matrices", "Booleans"),
    ("MatrixOrder", "Matrices", "Integers"),
    ("MatrixOrder", "InvertibleIntegerMatrices", "PositiveIntegers"),
    ("MatrixOrder", "SpecialLinearIntegerMatrices", "PositiveIntegers"),
    ("Eigenvalues", "SquareMatrices", "RationalNumbers"),
    ("Eigenvalues", "SquareMatrices", "AlgebraicNumbers"),
    ("Trace", "SquareMatrices", "Integers"),
    ("Trace", "SquareMatrices", "RationalNumbers"),
    ("Rank", "Matrices", "Integers"),
    ("Transpose", "Matrices", "Matrices"),
    ("Transpose", "OrthogonalMatrices", "OrthogonalMatrices"),
    ("Transpose", "PermutationMatrices", "PermutationMatrices"),
    ("Multiply", "Matrices", "Matrices"),
    ("Multiply", "InvertibleMatrices", "InvertibleMatrices"),
    ("Multiply", "OrthogonalMatrices", "OrthogonalMatrices"),
    ("Multiply", "PermutationMatrices", "PermutationMatrices"),
    ("JordanNormalForm", "SquareMatrices", "JordanNormalForms"),
    ("Diagonalise", "DiagonalizableMatrices", "DiagonalMatrices"),
    ("Diagonalise", "DiagonalizableMatrices", "InvertibleMatrices"),
    ("NilpotencyIndex", "NilpotentMatrices", "PositiveIntegers"),
    ("NullSpace", "Matrices", "ColumnVectors"),
    ("GramMatrix", "Matrices", "SymmetricMatrices"),
    ("GramMatrix", "InvertibleRealMatrices", "PositiveDefiniteMatrices"),
    ("RotationByAngle", "Expressions", "RotationMatrices"),
    ("MatrixMinimalPolynomial", "SquareMatrices", "Polynomials"),
    ("Cokernel", "Matrices", "FinitelyGeneratedAbelianGroups"),
    ("PowerTraces", "SquareMatrices", "LinearRecurrences"),
    ("Apply", "Matrices", "ColumnVectors"),
    ("MatrixFromColumns", "ColumnVectors", "Matrices"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "CharacteristicPolynomial": "characteristic_polynomial",
    "Inverse": "inverse",
    "Determinant": "determinant",
    "Add": "add",
    "IsSingular": "is_singular",
    "MatrixOrder": "matrix_order",
    "Eigenvalues": "eigenvalues",
    "Trace": "trace",
    "Rank": "rank",
    "Transpose": "transpose",
    "Multiply": "multiply",
    "JordanNormalForm": "jordan_normal_form",
    "Diagonalise": "diagonalise",
    "NilpotencyIndex": "nilpotency_index",
    "NullSpace": "null_space",
    "GramMatrix": "gram_matrix",
    "RotationByAngle": "rotation_by_angle",
    "MatrixMinimalPolynomial": "matrix_minimal_polynomial",
    "Cokernel": "cokernel",
    "PowerTraces": "power_traces",
    "Apply": "apply",
    "MatrixFromColumns": "matrix_from_columns",
}

RELATIONS: list[RelationSpec] = [
    ("CharacteristicPolynomial", ["A"], ["P"]),
    ("CharacteristicPolynomial", ["C"], ["P"]),
    ("Inverse", ["B"], ["B"]),
    ("Inverse", ["D"], ["D"]),
    ("CharacteristicPolynomial", ["B"], ["Q"]),
    ("CharacteristicPolynomial", ["D"], ["R"]),
    ("Add", ["A", "B"], ["E"]),
    ("Determinant", ["A"], ["three"]),
    ("IsSingular", ["A"], ["false"]),
    ("CharacteristicPolynomial", ["CompPhi6"], ["Phi6"]),
    ("MatrixOrder", ["CompPhi6"], ["six"]),
    ("MatrixOrder", ["B"], ["one"]),
    ("MatrixOrder", ["D"], ["two"]),
    ("Eigenvalues", ["A"], ["one", "three"]),
    ("Determinant", ["B"], ["one"]),
    ("Determinant", ["D"], ["neg_one"]),
    ("Determinant", ["C"], ["three"]),
    ("Determinant", ["S"], ["zero"]),
    ("IsSingular", ["S"], ["true"]),
    ("CharacteristicPolynomial", ["rotation90"], ["Phi4"]),
    ("MatrixOrder", ["rotation90"], ["four"]),
    ("Determinant", ["rotation90"], ["one"]),
    ("CharacteristicPolynomial", ["fibonacci_matrix"], ["golden_polynomial"]),
    ("Determinant", ["fibonacci_matrix"], ["neg_one"]),
    ("CharacteristicPolynomial", ["cycle3"], ["cube_minus_one"]),
    ("MatrixOrder", ["cycle3"], ["three"]),
    ("CharacteristicPolynomial", ["cartan_a2"], ["P"]),
    ("Eigenvalues", ["cartan_a2"], ["one", "three"]),
    ("Determinant", ["cartan_a2"], ["three"]),
    ("Inverse", ["cat_map"], ["cat_map_inverse"]),
    ("Inverse", ["cat_map_inverse"], ["cat_map"]),
    ("Eigenvalues", ["diag12"], ["one", "two"]),
    ("Determinant", ["nilpotent_block"], ["zero"]),
    ("IsSingular", ["nilpotent_block"], ["true"]),
    ("CharacteristicPolynomial", ["shear"], ["Q"]),
    ("CharacteristicPolynomial", ["nilpotent_block3"], ["x_cubed"]),
    ("CharacteristicPolynomial", ["complex_symmetric"], ["Phi4"]),
    ("CharacteristicPolynomial", ["jordan3"], ["jordan3_charpoly"]),
    ("CharacteristicPolynomial", ["jordan_mixed"], ["jordan3_charpoly"]),
    ("Inverse", ["A"], ["inverse_A"]),
    ("Inverse", ["rotation90"], ["rotation_minus90"]),
    ("Inverse", ["rotation_minus90"], ["rotation90"]),
    ("Inverse", ["rational_rotation"], ["rational_rotation_inverse"]),
    ("Inverse", ["fibonacci_matrix"], ["fibonacci_inverse"]),
    ("Inverse", ["jordan3"], ["jordan3_inverse"]),
    ("Inverse", ["complex_shear"], ["complex_shear_inverse"]),
    ("Inverse", ["rotation45"], ["rotation45_inverse"]),
    ("Determinant", ["rational_rotation"], [1]),
    ("Determinant", ["diag12"], [2]),
    ("Determinant", ["jordan3"], [12]),
    ("Determinant", ["singular3"], [0]),
    ("Determinant", ["rational_reflection"], [-1]),
    ("Determinant", ["real_upper_triangular"], [2]),
    ("Determinant", ["half_third"], [Fraction(5, 6)]),
    ("Determinant", ["sqrt2_diagonal"], ["sqrt2"]),
    ("Determinant", ["complex_symmetric"], [1]),
    ("Determinant", ["inverse_A"], [Fraction(1, 3)]),
    ("Add", ["D", "B"], ["ones2"]),
    ("Add", ["wide", "wide"], ["wide_doubled"]),
    ("Add", ["e1", "e2"], ["ones_column"]),
    ("Add", ["rotation90", "rotation_minus90"], ["zero2"]),
    ("IsSingular", ["singular3"], ["true"]),
    ("IsSingular", ["ones2"], ["true"]),
    ("IsSingular", ["cat_map"], ["false"]),
    ("IsSingular", ["nilpotent_symmetric"], ["true"]),
    ("IsSingular", ["hankel_fibonacci"], ["true"]),
    ("MatrixOrder", ["swap3"], [2]),
    ("MatrixOrder", ["reflection"], [2]),
    ("MatrixOrder", ["order3_companion"], [3]),
    ("MatrixOrder", ["rotation_minus90"], [4]),
    ("MatrixOrder", ["minus_identity"], [2]),
    ("Eigenvalues", ["fibonacci_matrix"], ["golden_conjugate", "golden_ratio"]),
    ("Eigenvalues", ["rotation90"], ["minus_i", "i"]),
    ("Eigenvalues", ["shear"], [1, 1]),
    ("Eigenvalues", ["nilpotent_block3"], [0, 0, 0]),
    ("Eigenvalues", ["cycle3"], ["omega_bar", "omega", 1]),
    ("Eigenvalues", ["real_positive_definite"], ["sqrt2_minus_1", "sqrt2_plus_1"]),
    ("Trace", ["A"], [4]),
    ("Trace", ["cartan_a2"], [4]),
    ("Trace", ["fibonacci_matrix"], [1]),
    ("Trace", ["nilpotent_block3"], [0]),
    ("Trace", ["jordan3"], [7]),
    ("Trace", ["rational_rotation"], [Fraction(6, 5)]),
    ("Trace", ["cycle3"], [0]),
    ("Trace", ["hankel_catalan"], [149]),
    ("Rank", ["S"], [1]),
    ("Rank", ["singular3"], [2]),
    ("Rank", ["wide"], [2]),
    ("Rank", ["tall"], [2]),
    ("Rank", ["zero2"], [0]),
    ("Rank", ["A"], [2]),
    ("Rank", ["row"], [1]),
    ("Rank", ["nilpotent_block3"], [2]),
    ("Rank", ["hankel_fibonacci"], [2]),
    ("Transpose", ["wide"], ["wide_transpose"]),
    ("Transpose", ["row"], ["column12"]),
    ("Transpose", ["cycle3"], ["cycle3_inverse"]),
    ("Transpose", ["shear"], ["shear_transpose"]),
    ("Transpose", ["A"], ["A"]),
    ("Transpose", ["rational_rotation"], ["rational_rotation_inverse"]),
    ("Transpose", ["rotation90"], ["rotation_minus90"]),
    ("Multiply", ["fibonacci_matrix", "fibonacci_matrix"], ["cat_map"]),
    ("Multiply", ["cat_map", "fibonacci_matrix"], ["fibonacci_cubed"]),
    ("Multiply", ["wide", "tall"], ["wide_times_tall"]),
    ("Multiply", ["tall", "wide"], ["tall_times_wide"]),
    ("Multiply", ["rotation90", "rotation90"], ["minus_identity"]),
    ("Multiply", ["cycle3", "cycle3"], ["cycle3_inverse"]),
    ("Multiply", ["shear", "D"], ["fibonacci_matrix"]),
    ("Multiply", ["D", "shear"], ["golden_companion"]),
    ("Multiply", ["rotation90", "rotation_minus90"], ["B"]),
    ("JordanNormalForm", ["jordan3"], ["jordan3"]),
    ("JordanNormalForm", ["jordan3_reordered"], ["jordan3"]),
    ("JordanNormalForm", ["shear"], ["shear"]),
    ("JordanNormalForm", ["nilpotent_dense"], ["nilpotent_block"]),
    ("JordanNormalForm", ["nilpotent_symmetric"], ["nilpotent_block"]),
    ("JordanNormalForm", ["A"], ["diag13"]),
    ("JordanNormalForm", ["C"], ["diag13"]),
    ("JordanNormalForm", ["upper_triangular"], ["diag12"]),
    ("JordanNormalForm", ["fibonacci_matrix"], ["fibonacci_eigenvalues_diagonal"]),
    ("JordanNormalForm", ["rotation90"], ["rotation90_diagonal"]),
    ("Diagonalise", ["A"], ["diag13", "eigenbasis_A"]),
    ("Diagonalise", ["C"], ["diag13", "eigenbasis_C"]),
    ("Diagonalise", ["S"], ["diag05", "eigenbasis_S"]),
    ("Diagonalise", ["upper_triangular"], ["diag12", "shear"]),
    ("Diagonalise", ["B"], ["B", "B"]),
    (
        "Diagonalise",
        ["fibonacci_matrix"],
        ["fibonacci_eigenvalues_diagonal", "fibonacci_eigenbasis"],
    ),
    ("Diagonalise", ["rotation90"], ["rotation90_diagonal", "rotation90_eigenbasis"]),
    ("NilpotencyIndex", ["zero2"], [1]),
    ("NilpotencyIndex", ["nilpotent_block"], [2]),
    ("NilpotencyIndex", ["nilpotent_block3"], [3]),
    ("NilpotencyIndex", ["nilpotent_dense"], [2]),
    ("NilpotencyIndex", ["nilpotent_symmetric"], [2]),
    ("NullSpace", ["S"], ["kernel_S"]),
    ("NullSpace", ["row"], ["kernel_S"]),
    ("NullSpace", ["singular3"], ["kernel_123"]),
    ("NullSpace", ["wide"], ["kernel_123"]),
    ("NullSpace", ["zero2"], ["e1", "e2"]),
    ("NullSpace", ["nilpotent_block"], ["e1"]),
    ("NullSpace", ["ones2"], ["kernel_ones"]),
    ("NullSpace", ["hankel_fibonacci"], ["kernel_hankel_fibonacci"]),
    ("GramMatrix", ["wide"], ["gram_wide"]),
    ("GramMatrix", ["tall"], ["A"]),
    ("GramMatrix", ["shear"], ["shear_gram"]),
    ("GramMatrix", ["rotation90"], ["B"]),
    ("GramMatrix", ["fibonacci_matrix"], ["cat_map"]),
    ("GramMatrix", ["row"], ["S"]),
    ("RotationByAngle", ["pi"], ["minus_identity"]),
    ("RotationByAngle", ["half_pi"], ["rotation90"]),
    ("RotationByAngle", ["third_pi"], ["rotation60"]),
    ("RotationByAngle", ["quarter_pi"], ["rotation45"]),
    ("MatrixMinimalPolynomial", ["B"], ["Phi1"]),
    ("MatrixMinimalPolynomial", ["zero2"], ["x_polynomial"]),
    ("MatrixMinimalPolynomial", ["A"], ["P"]),
    ("MatrixMinimalPolynomial", ["jordan3"], ["jordan3_charpoly"]),
    ("MatrixMinimalPolynomial", ["jordan_mixed"], ["jordan_mixed_minimal_polynomial"]),
    ("MatrixMinimalPolynomial", ["cycle3"], ["cube_minus_one"]),
    ("MatrixMinimalPolynomial", ["shear"], ["Q"]),
    ("MatrixMinimalPolynomial", ["diag12"], ["diag12_polynomial"]),
    ("MatrixMinimalPolynomial", ["nilpotent_block3"], ["x_cubed"]),
    ("Cokernel", ["diag23"], ["c6"]),
    ("Cokernel", ["A"], ["c3"]),
    ("Cokernel", ["wide"], ["c3"]),
    ("Cokernel", ["S"], ["integers_group"]),
    ("Cokernel", ["tall"], ["integers_group"]),
    ("Cokernel", ["zero2"], ["z2"]),
    ("Cokernel", ["diag24"], ["z2_plus_z4"]),
    ("Cokernel", ["B"], ["trivial_group"]),
    ("PowerTraces", ["fibonacci_matrix"], ["lucas"]),
    ("PowerTraces", ["B"], ["constant_two"]),
    ("PowerTraces", ["A"], ["one_plus_powers_of_three"]),
    ("PowerTraces", ["rotation90"], ["rotation90_traces"]),
    ("PowerTraces", ["cycle3"], ["cycle3_traces"]),
    ("Apply", ["A", "e1"], ["column21"]),
    ("Apply", ["rotation90", "e1"], ["e2"]),
    ("Apply", ["rotation90", "e2"], ["minus_e1"]),
    ("Apply", ["cycle3", "v123"], ["column312"]),
    ("Apply", ["wide", "v123"], ["column_14_32"]),
    ("Apply", ["S", "kernel_S"], ["zero_column"]),
    ("Apply", ["D", "e1"], ["e2"]),
    ("MatrixFromColumns", ["e1", "e2"], ["B"]),
    ("MatrixFromColumns", ["e2", "e1"], ["D"]),
    ("MatrixFromColumns", ["e2", "minus_e1"], ["rotation90"]),
    ("MatrixFromColumns", ["v123", "v123"], ["v123_twice"]),
    ("MatrixFromColumns", ["e1"], ["e1"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Add": (r"{in0} \op{+} {in1} = {out0}", True),
    "Determinant": (r"\op{\det(}{in0}\op{)} = {out0}", False),
    "Inverse": (r"{in0}^{\op{-1}} = {out0}", False),
    "MatrixOrder": (r"\op{\mathrm{ord}(}{in0}\op{)} = {out0}", False),
    "Trace": (r"\op{\operatorname{tr}(}{in0}\op{)} = {out0}", False),
    "Rank": (r"\op{\operatorname{rank}(}{in0}\op{)} = {out0}", False),
    "Transpose": (r"{in0}^{\op{T}} = {out0}", False),
    "Multiply": (r"{in0} {in1} = {out0}", False),
    "Apply": (r"{in0} {in1} = {out0}", False),
    "GramMatrix": (r"\op{G(}{in0}\op{)} = {out0}", False),
}

REFERENCES: dict[str, list[Reference]] = {
    "Cokernel": [("Wikipedia", "https://en.wikipedia.org/wiki/Smith_normal_form")],
    "JordanNormalForm": [("Wikipedia", "https://en.wikipedia.org/wiki/Jordan_normal_form")],
}

FILINGS: dict[str, list[str]] = {
    "LinearAlgebra": ["MatrixOperations"],
    "MatrixOperations": list(OPERATORS),
}
