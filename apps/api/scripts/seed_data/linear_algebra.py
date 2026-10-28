from seed_data.build import (
    HALF_SQRT2_CELL,
    I_CELL,
    MINUS_HALF_SQRT2_CELL,
    SQRT2_CELL,
    SQRT3_CELL,
    Instance,
    RelationSpec,
    Specimen,
    fraction,
    matrix_instance,
    seifert,
)

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
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("CharacteristicPolynomial", "Matrices", "Polynomials"),
    ("Inverse", "Matrices", "Matrices"),
    ("Inverse", "SymmetricMatrices", "SymmetricMatrices"),
    ("Determinant", "Matrices", "Integers"),
    ("Add", "Matrices", "Matrices"),
    ("IsSingular", "Matrices", "Booleans"),
    ("MatrixOrder", "Matrices", "Integers"),
    ("Eigenvalues", "SquareMatrices", "RationalNumbers"),
    ("Eigenvalues", "SquareMatrices", "AlgebraicNumbers"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "CharacteristicPolynomial": "characteristic_polynomial",
    "Inverse": "inverse",
    "Determinant": "determinant",
    "Add": "add",
    "IsSingular": "is_singular",
    "MatrixOrder": "matrix_order",
    "Eigenvalues": "eigenvalues",
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
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Add": (r"{in0} \op{+} {in1} = {out0}", True),
    "Determinant": (r"\op{\det(}{in0}\op{)} = {out0}", False),
    "Inverse": (r"{in0}^{\op{-1}} = {out0}", False),
    "MatrixOrder": (r"\op{\mathrm{ord}(}{in0}\op{)} = {out0}", False),
}

FILINGS: dict[str, list[str]] = {
    "LinearAlgebra": ["MatrixOperations"],
    "MatrixOperations": [
        "CharacteristicPolynomial",
        "Inverse",
        "Determinant",
        "Add",
        "IsSingular",
        "MatrixOrder",
        "Eigenvalues",
    ],
}
