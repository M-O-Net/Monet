from fractions import Fraction

from seed_data.build import (
    CYCLOTOMIC_WIKI,
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    algebraic,
    fraction,
    instance,
    lmfdb_field,
    matrix_instance,
    number_field,
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
    "Phi1": instance(
        "x - 1",
        polynomial(-1, 1),
        ["CyclotomicPolynomials"],
        r"The 1st cyclotomic polynomial, whose one root is $1$.",
    ),
    "x_polynomial": instance(
        "x",
        polynomial(0, 1),
        ["ChebyshevPolynomials", "MonicIntegerPolynomials", "IrreduciblePolynomials"],
        r"$T_{1}$.",
    ),
    "x_cubed": instance(r"x^{3}", polynomial(0, 0, 0, 1), ["MonicIntegerPolynomials"]),
    "jordan3_charpoly": instance(
        r"x^{3} - 7 x^{2} + 16 x - 12",
        polynomial(-12, 16, -7, 1),
        ["MonicIntegerPolynomials"],
        r"$(x - 2)^{2} (x - 3)$.",
    ),
    "diag12_polynomial": instance(
        r"x^{2} - 3 x + 2", polynomial(2, -3, 1), ["MonicIntegerPolynomials"]
    ),
    "jordan_mixed_minimal_polynomial": instance(
        r"x^{2} - 5 x + 6", polynomial(6, -5, 1), ["MonicIntegerPolynomials"]
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
    "Phi2": instance("x + 1", polynomial(1, 1), ["CyclotomicPolynomials"]),
    "Phi3": instance(r"x^{2} + x + 1", polynomial(1, 1, 1), ["CyclotomicPolynomials"]),
    "Phi5": instance(
        r"x^{4} + x^{3} + x^{2} + x + 1", polynomial(1, 1, 1, 1, 1), ["CyclotomicPolynomials"]
    ),
    "Phi8": instance(r"x^{4} + 1", polynomial(1, 0, 0, 0, 1), ["CyclotomicPolynomials"]),
    "Phi12": instance(r"x^{4} - x^{2} + 1", polynomial(1, 0, -1, 0, 1), ["CyclotomicPolynomials"]),
    "x_minus_3": instance(
        "x - 3", polynomial(-3, 1), ["MonicIntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "two_x_minus_1": instance(
        "2 x - 1", polynomial(-1, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "three_x_plus_1": instance(
        "3 x + 1", polynomial(1, 3), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "two_x_plus_1": instance(
        "2 x + 1", polynomial(1, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "x_squared_minus_3": instance(
        r"x^{2} - 3",
        polynomial(-3, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
    ),
    "two_x": instance("2 x", polynomial(0, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]),
    "minus_x": instance("- x", polynomial(0, -1), ["IntegerPolynomials", "IrreduciblePolynomials"]),
    "three_x_minus_2": instance(
        "3 x - 2", polynomial(-2, 3), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "one_minus_x": instance(
        "1 - x", polynomial(1, -1), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "half_x_minus_quarter": instance(
        r"\frac{x}{2} - \frac{1}{4}",
        polynomial(rational(-1, 4), rational(1, 2)),
        ["IrreduciblePolynomials"],
    ),
    "T5": instance(
        r"16 x^{5} - 20 x^{3} + 5 x",
        polynomial(0, 5, 0, -20, 0, 16),
        ["ChebyshevPolynomials"],
        r"$T_{5}$: $\cos 5\theta = 16 \cos^{5}\theta - 20 \cos^{3}\theta + 5 \cos\theta$.",
    ),
    "two_cube_minus_one": instance(
        r"2 x^{3} - 1", polynomial(-1, 0, 0, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "sqrt2_plus_sqrt3_minimal_polynomial": instance(
        r"x^{4} - 10 x^{2} + 1",
        polynomial(1, 0, -10, 0, 1),
        ["MonicIntegerPolynomials", "IrreduciblePolynomials"],
        r"The minimal polynomial of $\sqrt{2} + \sqrt{3}$, whose splitting field has Galois "
        r"group $V_{4}$.",
    ),
    "x_squared": instance(r"x^{2}", polynomial(0, 0, 1), ["MonicIntegerPolynomials"]),
    "fibonacci_interpolant": instance(
        r"\frac{x^{4}}{12} - \frac{2 x^{3}}{3} + \frac{23 x^{2}}{12} - \frac{4 x}{3} + 1",
        polynomial(1, rational(-4, 3), rational(23, 12), rational(-2, 3), rational(1, 12)),
        ["IrreduciblePolynomials"],
        r"The quartic through $(0, 1), (1, 1), (2, 2), (3, 3), (4, 5)$.",
    ),
    "q_sqrt_minus2": instance(r"\mathbb{Q}(\sqrt{-2})", number_field(2, 0, 1), ["QuadraticFields"]),
    "q_sqrt_minus6": instance(r"\mathbb{Q}(\sqrt{-6})", number_field(6, 0, 1), ["QuadraticFields"]),
    "matrix_2": matrix_instance(
        [[2]],
        [
            "DiagonalMatrices",
            "PositiveDefiniteMatrices",
            "InvertibleRationalMatrices",
            "CompanionMatrices",
            "ColumnVectors",
        ],
        r"The $1 \times 1$ matrix $(2)$, companion of $x - 2$.",
    ),
    "Q_companion": matrix_instance(
        [[0, -1], [1, 2]], ["CompanionMatrices", "SpecialLinearIntegerMatrices"]
    ),
    "rational_companion": matrix_instance(
        [[0, fraction(1, 4)], [1, 0]],
        ["CompanionMatrices", "InvertibleRationalMatrices", "DiagonalizableMatrices"],
    ),
    "sqrt2_plus_sqrt3": instance(
        r"\sqrt{2} + \sqrt{3}", algebraic([1, 0, -10, 0, 1], 3), ["AlgebraicIntegers"]
    ),
    "zeta6": instance(
        r"\frac{1}{2} + \frac{\sqrt{3} i}{2}",
        algebraic([1, -1, 1], 1),
        ["RootsOfUnity"],
        r"$e^{\pi i / 3}$, a primitive sixth root of unity.",
    ),
    "zeta6_bar": instance(
        r"\frac{1}{2} - \frac{\sqrt{3} i}{2}", algebraic([1, -1, 1], 0), ["RootsOfUnity"]
    ),
    "cbrt2_lower": instance(
        r"- \frac{\sqrt[3]{2}}{2} - \frac{\sqrt[3]{2} \sqrt{3} i}{2}",
        algebraic([-2, 0, 0, 1], 1),
        ["AlgebraicIntegers"],
    ),
    "cbrt2_upper": instance(
        r"- \frac{\sqrt[3]{2}}{2} + \frac{\sqrt[3]{2} \sqrt{3} i}{2}",
        algebraic([-2, 0, 0, 1], 2),
        ["AlgebraicIntegers"],
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
    "Factorisation": (
        r"\text{Factorisation}",
        "The irreducible factors over the rationals, each scaled to coprime integer "
        "coefficients with positive leading coefficient, repeated by multiplicity, lowest "
        "degree first. The constant left over is dropped.",
    ),
    "Discriminant": (
        r"\text{Discriminant}",
        "Zero exactly when the polynomial has a repeated root. For a quadratic, b² - 4ac.",
    ),
    "Resultant": (
        r"\text{Resultant}",
        r"$\operatorname{lc}(p)^{\deg q} \prod_{p(\alpha) = 0} q(\alpha)$: zero exactly when "
        "the two polynomials share a root.",
    ),
    "DivisionWithRemainder": (
        r"\text{Division with Remainder}",
        r"For $p$ and $q$, the quotient $s$ and remainder $r$ with $p = s q + r$ and "
        r"$\deg r < \deg q$. A constant lands on a number, since a polynomial here has degree "
        "at least one.",
    ),
    "ChebyshevPolynomial": (
        r"\text{Chebyshev Polynomial}",
        r"For $n$, the polynomial $T_{n}$ with $T_{n}(\cos\theta) = \cos n\theta$.",
    ),
    "MinimalPolynomial": (
        r"\text{Minimal Polynomial}",
        "The irreducible integer polynomial, positive leading coefficient, that an algebraic "
        "number is a root of: half its identity.",
    ),
    "GaloisGroup": (
        r"\text{Galois Group}",
        "The group permuting the roots of an irreducible polynomial, or of a number field's "
        "defining polynomial, given by the standard generators of its transitive group "
        "(degree at most 6).",
    ),
    "StemField": (
        r"\text{Stem Field}",
        r"$\mathbb{Q}[x] / (p)$, held by the reduced polynomial LMFDB uses. Only quadratic "
        "fields are computed: beyond them the reduction needs PARI, so those relations are "
        "entered from LMFDB.",
    ),
    "Evaluate": (
        r"\text{Evaluate}",
        r"A polynomial or function as a map: $(f, a) \mapsto f(a)$.",
    ),
    "Interpolate": (
        r"\text{Interpolate}",
        r"For values $v_{0}, \dots, v_{k}$, the polynomial of degree at most $k$ with "
        r"$p(i) = v_{i}$: the curried inverse of Evaluate on $0, 1, \dots, k$.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("CompanionMatrix", "Polynomials", "Matrices"),
    ("CompanionMatrix", "MonicIntegerPolynomials", "CompanionMatrices"),
    ("Degree", "Polynomials", "Integers"),
    ("CyclotomicPolynomial", "Integers", "CyclotomicPolynomials"),
    ("CyclotomicPolynomial", "PositiveIntegers", "CyclotomicPolynomials"),
    ("Roots", "Polynomials", "RationalNumbers"),
    ("Roots", "Polynomials", "AlgebraicNumbers"),
    ("Roots", "CyclotomicPolynomials", "RootsOfUnity"),
    ("Factorisation", "Polynomials", "IrreduciblePolynomials"),
    ("Discriminant", "Polynomials", "RationalNumbers"),
    ("Discriminant", "IntegerPolynomials", "Integers"),
    ("Resultant", "Polynomials", "RationalNumbers"),
    ("Resultant", "IntegerPolynomials", "Integers"),
    ("DivisionWithRemainder", "Polynomials", "Polynomials"),
    ("DivisionWithRemainder", "Polynomials", "RationalNumbers"),
    ("ChebyshevPolynomial", "PositiveIntegers", "ChebyshevPolynomials"),
    ("MinimalPolynomial", "AlgebraicNumbers", "IrreduciblePolynomials"),
    ("GaloisGroup", "IrreduciblePolynomials", "PermutationGroups"),
    ("GaloisGroup", "NumberFields", "PermutationGroups"),
    ("StemField", "IrreduciblePolynomials", "NumberFields"),
    ("StemField", "CyclotomicPolynomials", "CyclotomicFields"),
    ("Evaluate", "Polynomials", "RationalNumbers"),
    ("Evaluate", "Polynomials", "AlgebraicNumbers"),
    ("Evaluate", "ElementaryFunctions", "RationalNumbers"),
    ("Evaluate", "ElementaryFunctions", "AlgebraicNumbers"),
    ("Evaluate", "ElementaryFunctions", "Expressions"),
    ("Interpolate", "FiniteSequences", "Polynomials"),
    ("Interpolate", "FiniteSequences", "RationalNumbers"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "CompanionMatrix": "companion_matrix",
    "Degree": "degree",
    "CyclotomicPolynomial": "cyclotomic_polynomial",
    "Roots": "roots",
    "Factorisation": "factorisation",
    "Discriminant": "discriminant",
    "Resultant": "resultant",
    "DivisionWithRemainder": "division_with_remainder",
    "ChebyshevPolynomial": "chebyshev_polynomial",
    "MinimalPolynomial": "minimal_polynomial",
    "GaloisGroup": "galois_group",
    "StemField": "stem_field",
    "Evaluate": "evaluate",
    "Interpolate": "interpolate",
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
    ("Degree", ["cube_minus_two"], [3]),
    ("Degree", ["Phi14"], [6]),
    ("Degree", ["rational_cubic"], [3]),
    ("Degree", ["x_minus_2"], [1]),
    ("Roots", ["golden_polynomial"], ["golden_conjugate", "golden_ratio"]),
    ("Roots", ["Phi4"], ["minus_i", "i"]),
    ("Roots", ["Phi6"], ["zeta6_bar", "zeta6"]),
    ("Roots", ["cube_minus_one"], ["omega_bar", "omega", 1]),
    ("Roots", ["Q"], [1, 1]),
    ("Roots", ["cube_minus_two"], ["cbrt2_lower", "cbrt2_upper", "cbrt2"]),
    ("Roots", ["integer_cubic"], [-1, 0, 1]),
    ("CyclotomicPolynomial", [1], ["Phi1"]),
    ("CyclotomicPolynomial", [2], ["Phi2"]),
    ("CyclotomicPolynomial", [3], ["Phi3"]),
    ("CyclotomicPolynomial", [5], ["Phi5"]),
    ("CyclotomicPolynomial", [8], ["Phi8"]),
    ("CyclotomicPolynomial", [12], ["Phi12"]),
    ("CompanionMatrix", ["golden_polynomial"], ["golden_companion"]),
    ("CompanionMatrix", ["Phi3"], ["order3_companion"]),
    ("CompanionMatrix", ["x_minus_2"], ["matrix_2"]),
    ("CompanionMatrix", ["Q"], ["Q_companion"]),
    ("CompanionMatrix", ["rational_quadratic"], ["rational_companion"]),
    ("Factorisation", ["cube_minus_one"], ["Phi1", "Phi3"]),
    ("Factorisation", ["Q"], ["Phi1", "Phi1"]),
    ("Factorisation", ["P"], ["x_minus_3", "Phi1"]),
    ("Factorisation", ["integer_cubic"], ["Phi1", "x_polynomial", "Phi2"]),
    ("Factorisation", ["integer_quadratic2"], ["two_x_minus_1", "three_x_plus_1"]),
    ("Factorisation", ["integer_quadratic"], ["Phi2", "two_x_plus_1"]),
    ("Factorisation", ["rational_cubic"], ["x_polynomial", "x_squared_minus_3"]),
    ("Factorisation", ["T4"], ["T4"]),
    ("Factorisation", ["irreducible_quadratic"], ["T2"]),
    ("Discriminant", ["P"], [4]),
    ("Discriminant", ["Q"], [0]),
    ("Discriminant", ["golden_polynomial"], [5]),
    ("Discriminant", ["Phi4"], [-4]),
    ("Discriminant", ["Phi6"], [-3]),
    ("Discriminant", ["cube_minus_two"], [-108]),
    ("Discriminant", ["plastic_polynomial"], [-23]),
    ("Discriminant", ["rational_quadratic"], [1]),
    ("Discriminant", ["irreducible_quadratic2"], [Fraction(-2, 3)]),
    ("Discriminant", ["T2"], [8]),
    ("Resultant", ["P", "Q"], [0]),
    ("Resultant", ["P", "R"], [0]),
    ("Resultant", ["golden_polynomial", "square_minus_two"], [-1]),
    ("Resultant", ["Phi4", "Phi6"], [1]),
    ("Resultant", ["R", "Phi4"], [4]),
    ("Resultant", ["rational_quadratic", "square_minus_two"], [Fraction(49, 16)]),
    ("Resultant", ["T2", "square_minus_two"], [9]),
    ("Resultant", ["x_minus_2", "P"], [-1]),
    ("DivisionWithRemainder", ["cube_minus_one", "Phi1"], ["Phi3", 0]),
    ("DivisionWithRemainder", ["P", "Phi1"], ["x_minus_3", 0]),
    ("DivisionWithRemainder", ["T3", "T2"], ["two_x", "minus_x"]),
    ("DivisionWithRemainder", ["Phi6", "P"], [1, "three_x_minus_2"]),
    ("DivisionWithRemainder", ["golden_polynomial", "square_minus_two"], [1, "one_minus_x"]),
    ("DivisionWithRemainder", ["x_minus_2", "P"], [0, "x_minus_2"]),
    ("DivisionWithRemainder", ["R", "two_x_plus_1"], ["half_x_minus_quarter", Fraction(-3, 4)]),
    ("ChebyshevPolynomial", [1], ["x_polynomial"]),
    ("ChebyshevPolynomial", [2], ["T2"]),
    ("ChebyshevPolynomial", [3], ["T3"]),
    ("ChebyshevPolynomial", [4], ["T4"]),
    ("ChebyshevPolynomial", [5], ["T5"]),
    ("MinimalPolynomial", ["sqrt2"], ["square_minus_two"]),
    ("MinimalPolynomial", ["golden_ratio"], ["golden_polynomial"]),
    ("MinimalPolynomial", ["cbrt2"], ["cube_minus_two"]),
    ("MinimalPolynomial", ["i"], ["Phi4"]),
    ("MinimalPolynomial", ["omega"], ["Phi3"]),
    ("MinimalPolynomial", ["zeta5"], ["Phi5"]),
    ("MinimalPolynomial", ["half_sqrt2"], ["T2"]),
    ("MinimalPolynomial", ["cbrt_half"], ["two_cube_minus_one"]),
    ("MinimalPolynomial", ["sqrt2_plus_sqrt3"], ["sqrt2_plus_sqrt3_minimal_polynomial"]),
    ("MinimalPolynomial", ["sqrt2_plus_1"], ["pell_polynomial"]),
    ("GaloisGroup", ["cube_minus_two"], ["s3"]),
    ("GaloisGroup", ["plastic_polynomial"], ["s3"]),
    ("GaloisGroup", ["Phi5"], ["c4"]),
    ("GaloisGroup", ["T4"], ["c4"]),
    ("GaloisGroup", ["sqrt2_plus_sqrt3_minimal_polynomial"], ["klein_four"]),
    ("GaloisGroup", ["Phi8"], ["klein_four"]),
    ("GaloisGroup", ["golden_polynomial"], ["c2"]),
    ("GaloisGroup", ["q_cbrt2"], ["s3"]),
    ("GaloisGroup", ["q_zeta5"], ["c4"]),
    ("GaloisGroup", ["q_sqrt5"], ["c2"]),
    ("StemField", ["golden_polynomial"], ["q_sqrt5"]),
    ("StemField", ["square_minus_two"], ["q_sqrt2"]),
    ("StemField", ["T2"], ["q_sqrt2"]),
    ("StemField", ["pell_polynomial"], ["q_sqrt2"]),
    ("StemField", ["Phi6"], ["q_zeta3"]),
    ("StemField", ["Phi3"], ["q_zeta3"]),
    ("StemField", ["Phi4"], ["q_i"]),
    ("StemField", ["two_square_plus_one"], ["q_sqrt_minus2"]),
    ("StemField", ["irreducible_quadratic2"], ["q_sqrt_minus6"]),
    ("Evaluate", ["P", 3], [0]),
    ("Evaluate", ["P", 0], [3]),
    ("Evaluate", ["golden_polynomial", "golden_ratio"], [0]),
    ("Evaluate", ["Phi4", "i"], [0]),
    ("Evaluate", ["T3", Fraction(1, 2)], [-1]),
    ("Evaluate", ["exp", 0], [1]),
    ("Evaluate", ["sin", "pi"], [0]),
    ("Evaluate", ["cos", "pi"], [-1]),
    ("Evaluate", ["cos", "third_pi"], [Fraction(1, 2)]),
    ("Evaluate", ["lorentzian", 1], [Fraction(1, 2)]),
    ("Evaluate", ["log", 1], [0]),
    ("Evaluate", ["arctan", 1], ["quarter_pi"]),
    ("Interpolate", ["P_values"], ["P"]),
    ("Interpolate", ["first_squares"], ["x_squared"]),
    ("Interpolate", ["first_fibonacci"], ["fibonacci_interpolant"]),
    ("Interpolate", ["constant_fives"], [5]),
]

ASSERTED: list[RelationSpec] = [
    ("StemField", ["cube_minus_two"], ["q_cbrt2"]),
    ("StemField", ["Phi5"], ["q_zeta5"]),
    ("StemField", ["Phi10"], ["q_zeta5"]),
    ("StemField", ["Phi14"], ["q_zeta7"]),
    ("StemField", ["Phi8"], ["q_zeta8"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Degree": (r"\op{\deg(}{in0}\op{)} = {out0}", False),
    "CyclotomicPolynomial": (r"\op{\Phi}_{{in0}}(x) = {out0}", False),
    "Discriminant": (r"\op{\operatorname{disc}(}{in0}\op{)} = {out0}", False),
    "Resultant": (r"\op{\operatorname{res}(}{in0}\op{,} {in1}\op{)} = {out0}", False),
    "DivisionWithRemainder": (r"{in0} = {out0} \op{\cdot} {in1} \op{+} {out1}", False),
    "ChebyshevPolynomial": (r"\op{T}_{{in0}}(x) = {out0}", False),
    "Evaluate": (r"{in0} \op{\text{ at }} {in1} = {out0}", False),
}

REFERENCES: dict[str, list[Reference]] = {
    # LMFDB names the last two by Q(zeta_5) and Q(zeta_7): Q(zeta_2m) = Q(zeta_m) for odd
    # m, so they are the same fields under a different name. Each page's defining
    # polynomial is exactly the object it is filed under here.
    "Phi6": [*lmfdb_field("2.0.3.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi10": [*lmfdb_field("4.0.125.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "Phi14": [*lmfdb_field("6.0.16807.1"), *oeis("A013595"), CYCLOTOMIC_WIKI],
    "CyclotomicPolynomial": [CYCLOTOMIC_WIKI],
    "Phi5": [*lmfdb_field("4.0.125.1"), CYCLOTOMIC_WIKI],
    "Phi8": [*lmfdb_field("4.0.256.1"), CYCLOTOMIC_WIKI],
    "T5": oeis("A053120"),
    "ChebyshevPolynomial": [
        *oeis("A053120"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Chebyshev_polynomials"),
    ],
    "q_sqrt_minus2": lmfdb_field("2.0.8.1"),
    "q_sqrt_minus6": lmfdb_field("2.0.24.1"),
    "GaloisGroup": [("Wikipedia", "https://en.wikipedia.org/wiki/Galois_group")],
}

FILINGS: dict[str, list[str]] = {
    "PolynomialAlgebra": ["PolynomialOperations"],
    "PolynomialOperations": list(OPERATORS),
}
