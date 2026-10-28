from seed_data.build import (
    CYCLOTOMIC_WIKI,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    instance,
    lmfdb_field,
    oeis,
    polynomial,
    rational,
)

INSTANCES: dict[str, Instance] = {
    "P": instance(
        r"x^{2} - 4 x + 3",
        polynomial(3, -4, 1),
        ["MonicIntegerPolynomials", "RationalFunctions"],
    ),
    "Q": instance(r"x^{2} - 2 x + 1", polynomial(1, -2, 1), ["MonicIntegerPolynomials"]),
    "R": instance(
        r"x^{2} - 1",
        polynomial(-1, 0, 1),
        ["MonicIntegerPolynomials", "RationalFunctions", "EvenFunctions"],
    ),
    "Phi4": instance(
        r"x^{2} + 1",
        polynomial(1, 0, 1),
        ["CyclotomicPolynomials"],
        r"The 4th cyclotomic polynomial, whose roots are $\pm i$.",
    ),
    "Phi6": instance(
        r"x^{2} - x + 1",
        polynomial(1, -1, 1),
        ["CyclotomicPolynomials", "RationalFunctions"],
        "The 6th cyclotomic polynomial — and the Alexander polynomial of the trefoil.",
    ),
    "Phi10": instance(
        r"x^{4} - x^{3} + x^{2} - x + 1",
        polynomial(1, -1, 1, -1, 1),
        ["CyclotomicPolynomials"],
        r"The 10th cyclotomic polynomial — and the Alexander polynomial of $5_1$.",
    ),
    "Phi14": instance(
        r"x^{6} - x^{5} + x^{4} - x^{3} + x^{2} - x + 1",
        polynomial(1, -1, 1, -1, 1, -1, 1),
        ["CyclotomicPolynomials"],
        r"The 14th cyclotomic polynomial — and the Alexander polynomial of $7_1$.",
    ),
    "cube_minus_one": instance(r"x^{3} - 1", polynomial(-1, 0, 0, 1), ["MonicIntegerPolynomials"]),
    "square_minus_two": instance(
        r"x^{2} - 2",
        polynomial(-2, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "golden_polynomial": instance(
        r"x^{2} - x - 1",
        polynomial(-1, -1, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        "The minimal polynomial of the golden ratio.",
    ),
    "cube_minus_two": instance(
        r"x^{3} - 2",
        polynomial(-2, 0, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "plastic_polynomial": instance(
        r"x^{3} - x - 1",
        polynomial(-1, -1, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        "Its real root is the plastic number.",
    ),
    "two_square_plus_one": instance(
        r"2 x^{2} + 1",
        polynomial(1, 0, 2),
        ["IntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "integer_quadratic": instance(
        r"2 x^{2} + 3 x + 1", polynomial(1, 3, 2), ["IntegerPolynomials"]
    ),
    "integer_cubic": instance(r"2 x^{3} - 2 x", polynomial(0, -2, 0, 2), ["IntegerPolynomials"]),
    "integer_quadratic2": instance(
        r"6 x^{2} - x - 1", polynomial(-1, -1, 6), ["IntegerPolynomials"]
    ),
    "rational_quadratic": instance(
        r"x^{2} - \frac{1}{4}", polynomial(rational(-1, 4), 0, 1), ["Polynomials"]
    ),
    "rational_quadratic2": instance(
        r"\frac{x^{2}}{2} - \frac{x}{2}",
        polynomial(0, rational(-1, 2), rational(1, 2)),
        ["Polynomials"],
    ),
    "rational_cubic": instance(
        r"\frac{x^{3}}{3} - x", polynomial(0, -1, 0, rational(1, 3)), ["Polynomials"]
    ),
    "irreducible_quadratic": instance(
        r"x^{2} - \frac{1}{2}", polynomial(rational(-1, 2), 0, 1), ["IrreduciblePolynomials"]
    ),
    "irreducible_quadratic2": instance(
        r"\frac{x^{2}}{2} + \frac{1}{3}",
        polynomial(rational(1, 3), 0, rational(1, 2)),
        ["IrreduciblePolynomials"],
    ),
    "irreducible_cubic": instance(
        r"x^{3} - \frac{1}{2}",
        polynomial(rational(-1, 2), 0, 0, 1),
        ["IrreduciblePolynomials"],
    ),
    "T2": instance(
        r"2 x^{2} - 1",
        polynomial(-1, 0, 2),
        ["ChebyshevPolynomials", "IrreduciblePolynomials"],
        r"$T_{2}$: $\cos 2\theta = 2\cos^{2}\theta - 1$.",
    ),
    "T3": instance(
        r"4 x^{3} - 3 x",
        polynomial(0, -3, 0, 4),
        ["ChebyshevPolynomials"],
        r"$T_{3}$: $\cos 3\theta = 4\cos^{3}\theta - 3\cos\theta$.",
    ),
    "T4": instance(
        r"8 x^{4} - 8 x^{2} + 1",
        polynomial(1, 0, -8, 0, 8),
        ["ChebyshevPolynomials", "IrreduciblePolynomials"],
        r"$T_{4}$.",
    ),
    "pell_polynomial": instance(
        r"x^{2} - 2 x - 1",
        polynomial(-1, -2, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        r"Its roots $1 \pm \sqrt{2}$ drive the Pell numbers.",
    ),
    "x_minus_2": instance(
        "x - 2", polynomial(-2, 1), ["MonicIntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "fibonacci_squares_polynomial": instance(
        r"x^{3} - 2 x^{2} - 2 x + 1",
        polynomial(1, -2, -2, 1),
        ["MonicIntegerPolynomials"],
        r"$(x + 1)(x^{2} - 3 x + 1)$, whose roots are $-1$, $\varphi^{2}$ and $\psi^{2}$.",
    ),
}

SECTIONS: dict[str, Specimen] = {
    "PolynomialOperations": (
        r"\text{Polynomial Operations}",
        "Operations taking polynomials as their input: companion matrices, degree.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "CompanionMatrix": (
        r"\text{Companion Matrix}",
        "For a monic polynomial, the matrix whose characteristic polynomial is that polynomial.",
    ),
    "Degree": (r"\text{Degree}", "The highest power of the variable in a polynomial."),
    "Roots": (
        r"\text{Roots}",
        "Every value at which a polynomial vanishes, one output each.",
    ),
    "CyclotomicPolynomial": (
        r"\text{Cyclotomic Polynomial}",
        r"For $n$, the monic factor of $x^{n} - 1$ whose roots are exactly the "
        r"primitive $n$th roots of unity.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("CompanionMatrix", "Polynomials", "Matrices"),
    ("Degree", "Polynomials", "Integers"),
    ("CyclotomicPolynomial", "Integers", "CyclotomicPolynomials"),
    ("Roots", "Polynomials", "RationalNumbers"),
    ("Roots", "Polynomials", "AlgebraicNumbers"),
    ("Roots", "CyclotomicPolynomials", "RootsOfUnity"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "CompanionMatrix": "companion_matrix",
    "Degree": "degree",
    "CyclotomicPolynomial": "cyclotomic_polynomial",
    "Roots": "roots",
}

RELATIONS: list[RelationSpec] = [
    ("CompanionMatrix", ["P"], ["C"]),
    ("Degree", ["P"], ["two"]),
    ("CyclotomicPolynomial", ["six"], ["Phi6"]),
    ("CyclotomicPolynomial", ["ten"], ["Phi10"]),
    ("CyclotomicPolynomial", ["fourteen"], ["Phi14"]),
    ("CompanionMatrix", ["Phi6"], ["CompPhi6"]),
    ("CompanionMatrix", ["R"], ["D"]),
    ("Roots", ["P"], ["one", "three"]),
    ("CyclotomicPolynomial", ["four"], ["Phi4"]),
    ("CompanionMatrix", ["Phi4"], ["rotation90"]),
    ("CompanionMatrix", ["cube_minus_one"], ["cycle3"]),
    ("Roots", ["rational_quadratic"], ["minus_half", "half"]),
    ("Degree", ["T4"], ["four"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Degree": (r"\op{\deg(}{in0}\op{)} = {out0}", False),
    "CyclotomicPolynomial": (r"\op{\Phi}_{{in0}}(x) = {out0}", False),
}

REFERENCES: dict[str, list[Reference]] = {
    # LMFDB names the last two by Q(zeta_5) and Q(zeta_7): Q(zeta_2m) = Q(zeta_m) for odd
    # m, so they are the same fields under a different name. Each page's defining
    # polynomial is exactly the object it is filed under here.
    "Phi6": [*lmfdb_field("2.0.3.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi10": [*lmfdb_field("4.0.125.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi14": [*lmfdb_field("6.0.16807.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "CyclotomicPolynomial": [CYCLOTOMIC_WIKI],
}

FILINGS: dict[str, list[str]] = {
    "PolynomialAlgebra": ["PolynomialOperations"],
    "PolynomialOperations": ["CompanionMatrix", "Degree", "Roots", "CyclotomicPolynomial"],
}
