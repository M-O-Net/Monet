from fractions import Fraction

from seed_data.build import (
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    holonomic,
    instance,
    integer,
    oeis,
    recurrence,
    seq,
)


def finite(*values: int) -> Instance:
    shown = r", \  ".join(str(v) for v in values)
    return instance(
        rf"\left( {shown}\right)", {"tuple": [integer(v) for v in values]}, ["FiniteSequences"]
    )


INSTANCES: dict[str, Instance] = {
    "first_fibonacci": instance(
        r"\left( 1, \  1, \  2, \  3, \  5\right)",
        {"tuple": [integer(v) for v in (1, 1, 2, 3, 5)]},
        ["FiniteSequences"],
    ),
    "first_primes": instance(
        r"\left( 2, \  3, \  5, \  7, \  11\right)",
        {"tuple": [integer(v) for v in (2, 3, 5, 7, 11)]},
        ["FiniteSequences"],
    ),
    "first_factorials": instance(
        r"\left( 1, \  2, \  6, \  24, \  120\right)",
        {"tuple": [integer(v) for v in (1, 2, 6, 24, 120)]},
        ["FiniteSequences"],
    ),
    "squares": instance(
        r"\left(n^{2}\right)_{n \geq 0}",
        seq("Pow(Symbol('n'), Integer(2))", 0),
        ["SequencesByFormula"],
    ),
    "powers_of_two": instance(
        r"\left(2^{n}\right)_{n \geq 0}",
        seq("Pow(Integer(2), Symbol('n'))", 0),
        ["SequencesByFormula"],
    ),
    "factorials": instance(
        r"\left(n!\right)_{n \geq 0}",
        seq("factorial(Symbol('n'))", 0),
        ["SequencesByFormula"],
    ),
    "prime_counting": instance(
        r"\left(\operatorname{primepi}{\left(n \right)}\right)_{n \geq 1}",
        seq("primepi(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        r"$\pi(n)$, the number of primes up to $n$.",
    ),
    "big_omega": instance(
        r"\left(\Omega\left(n\right)\right)_{n \geq 1}",
        seq("primeomega(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        "The number of prime factors of n, counted with multiplicity. Additive, not "
        "multiplicative.",
    ),
    "little_omega": instance(
        r"\left(\nu\left(n\right)\right)_{n \geq 1}",
        seq("primenu(Symbol('n'))", 1),
        ["ArithmeticFunctions"],
        r"The number of distinct primes dividing $n$, often written $\omega(n)$.",
    ),
    "totient": instance(
        r"\left(\phi\left(n\right)\right)_{n \geq 1}",
        seq("totient(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        "Euler's totient, as a sequence.",
    ),
    "divisor_sum": instance(
        r"\left(\sigma\left(n\right)\right)_{n \geq 1}",
        seq("divisor_sigma(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        r"The sum of the divisors of $n$.",
    ),
    "mobius": instance(
        r"\left(\mu\left(n\right)\right)_{n \geq 1}",
        seq("mobius(Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        "The Möbius function.",
    ),
    "catalan_numbers": instance(
        r"\left(n + 2\right) a_{n + 1} - 2 \left(2 n + 1\right) a_{n} = 0, \quad a_{0} = 1",
        holonomic([[-2, -4], [2, 1]], [1]),
        ["HolonomicSequences"],
        r"The Catalan numbers $1, 1, 2, 5, 14, 42, \dots$",
    ),
    "central_binomials": instance(
        r"\left(n + 1\right) a_{n + 1} - 2 \left(2 n + 1\right) a_{n} = 0, \quad a_{0} = 1",
        holonomic([[-2, -4], [1, 1]], [1]),
        ["HolonomicSequences"],
        r"The central binomial coefficients $\binom{2n}{n}$: $1, 2, 6, 20, 70, \dots$",
    ),
    "apery_numbers": instance(
        r"\left(n + 2\right)^{3} a_{n + 2} - \left(2 n + 3\right) \left(17 n^{2} + 51 n + 39\right)"
        r" a_{n + 1} + \left(n + 1\right)^{3} a_{n} = 0, \quad a_{0} = 1, a_{1} = 5",
        holonomic([[1, 3, 3, 1], [-117, -231, -153, -34], [8, 12, 6, 1]], [1, 5]),
        ["HolonomicSequences"],
        r"The Apéry numbers $1, 5, 73, 1445, \dots$, behind the irrationality of $\zeta(3)$.",
    ),
    "fibonacci": instance(
        r"a_{n} = a_{n - 1} + a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([1, 1], [0, 1]),
        ["LinearRecurrences"],
        "The Fibonacci numbers.",
    ),
    "lucas": instance(
        r"a_{n} = a_{n - 1} + a_{n - 2}, \quad a_{0} = 2, a_{1} = 1",
        recurrence([1, 1], [2, 1]),
        ["LinearRecurrences"],
        "The Lucas numbers: Fibonacci's recurrence from different initial values.",
    ),
    "pell": instance(
        r"a_{n} = 2 a_{n - 1} + a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([2, 1], [0, 1]),
        ["LinearRecurrences"],
        "The Pell numbers.",
    ),
    "first_lucas": finite(2, 1, 3, 4, 7, 11),
    "first_pell": finite(0, 1, 2, 5, 12, 29),
    "first_catalan": finite(1, 1, 2, 5, 14, 42, 132),
    "first_central_binomials": finite(1, 2, 6, 20, 70),
    "first_apery": finite(1, 5, 73, 1445, 33001),
    "running_fibonacci": finite(1, 2, 4, 7, 12),
    "running_primes": finite(2, 5, 10, 17, 28),
    "running_factorials": finite(1, 3, 9, 33, 153),
    "catalan_hankel_transform": finite(1, 1, 1, 1),
    "central_hankel_transform": finite(1, 2, 4),
    "factorial_hankel_transform": finite(1, 2, 24),
    "fibonacci_hankel_transform": finite(1, 1, 0),
    "primes_hankel_transform": finite(2, 1, -2),
    "sum_of_squares": instance(
        r"\left(\frac{n \left(n + 1\right) \left(2 n + 1\right)}{6}\right)_{n \geq 0}",
        seq(
            "Mul(Rational(1, 6), Symbol('n'), Add(Symbol('n'), Integer(1)), "
            "Add(Mul(Integer(2), Symbol('n')), Integer(1)))",
            0,
        ),
        ["SequencesByFormula"],
        r"The square pyramidal numbers $0^{2} + 1^{2} + \dots + n^{2}$.",
    ),
    "mersenne": instance(
        r"\left(2^{n + 1} - 1\right)_{n \geq 0}",
        seq("Add(Pow(Integer(2), Add(Symbol('n'), Integer(1))), Integer(-1))", 0),
        ["SequencesByFormula"],
    ),
    "reciprocals": instance(
        r"\left(\frac{1}{n}\right)_{n \geq 1}",
        seq("Pow(Symbol('n'), Integer(-1))", 1),
        ["SequencesByFormula"],
    ),
    "harmonic_numbers": instance(
        r"\left(H_{n}\right)_{n \geq 1}",
        seq("harmonic(Symbol('n'))", 1),
        ["SequencesByFormula"],
        r"The harmonic numbers $1 + \frac{1}{2} + \dots + \frac{1}{n}$.",
    ),
    "odd_numbers": instance(
        r"\left(2 n - 1\right)_{n \geq 1}",
        seq("Add(Mul(Integer(2), Symbol('n')), Integer(-1))", 1),
        ["ArithmeticFunctions"],
    ),
    "squares_from_one": instance(
        r"\left(n^{2}\right)_{n \geq 1}",
        seq("Pow(Symbol('n'), Integer(2))", 1),
        ["MultiplicativeFunctions"],
    ),
    "naturals": instance(
        r"\left(n\right)_{n \geq 0}",
        seq("Symbol('n')", 0),
        ["SequencesByFormula"],
    ),
    "binet": instance(
        r"\left(\frac{\varphi^{n} - \psi^{n}}{\sqrt{5}}\right)_{n \geq 0}",
        seq(
            "Add(Mul(Integer(-1), Rational(1, 5), Pow(Integer(5), Rational(1, 2)), "
            "Pow(Add(Rational(1, 2), Mul(Integer(-1), Rational(1, 2), Pow(Integer(5), "
            "Rational(1, 2)))), Symbol('n'))), Mul(Rational(1, 5), Pow(Integer(5), "
            "Rational(1, 2)), Pow(Add(Rational(1, 2), Mul(Rational(1, 2), Pow(Integer(5), "
            "Rational(1, 2)))), Symbol('n'))))",
            0,
        ),
        ["SequencesByFormula"],
        r"Binet's formula for the Fibonacci numbers, with $\varphi, \psi = \frac{1 \pm "
        r"\sqrt{5}}{2}$.",
    ),
    "lucas_closed_form": instance(
        r"\left(\varphi^{n} + \psi^{n}\right)_{n \geq 0}",
        seq(
            "Add(Pow(Add(Rational(1, 2), Mul(Integer(-1), Rational(1, 2), Pow(Integer(5), "
            "Rational(1, 2)))), Symbol('n')), Pow(Add(Rational(1, 2), Mul(Rational(1, 2), "
            "Pow(Integer(5), Rational(1, 2)))), Symbol('n')))",
            0,
        ),
        ["SequencesByFormula"],
    ),
    "pell_closed_form": instance(
        r"\left(\frac{\left(1 + \sqrt{2}\right)^{n} - \left(1 - \sqrt{2}\right)^{n}}{2 \sqrt{2}}"
        r"\right)_{n \geq 0}",
        seq(
            "Add(Mul(Integer(-1), Rational(1, 4), Pow(Integer(2), Rational(1, 2)), "
            "Pow(Add(Integer(1), Mul(Integer(-1), Pow(Integer(2), Rational(1, 2)))), "
            "Symbol('n'))), Mul(Rational(1, 4), Pow(Integer(2), Rational(1, 2)), "
            "Pow(Add(Integer(1), Pow(Integer(2), Rational(1, 2))), Symbol('n'))))",
            0,
        ),
        ["SequencesByFormula"],
    ),
    "constant_one": instance(
        r"\left(1\right)_{n \geq 1}",
        seq("Integer(1)", 1),
        ["MultiplicativeFunctions"],
        r"The constant function $\mathbf{1}$: convolving with it sums over divisors.",
    ),
    "identity_function": instance(
        r"\left(n\right)_{n \geq 1}",
        seq("Symbol('n')", 1),
        ["MultiplicativeFunctions"],
    ),
    "unit_function": instance(
        r"\left(\delta_{1 n}\right)_{n \geq 1}",
        seq("KroneckerDelta(Integer(1), Symbol('n'))", 1),
        ["MultiplicativeFunctions"],
        r"$\varepsilon$, the identity for Dirichlet convolution: $1$ at $n = 1$, else $0$.",
    ),
    "divisor_count_function": instance(
        r"\left(\sigma_{0}\left(n\right)\right)_{n \geq 1}",
        seq("divisor_sigma(Symbol('n'), Integer(0))", 1),
        ["MultiplicativeFunctions"],
        r"$\tau(n)$, the number of divisors of $n$, as a sequence.",
    ),
    "doubling": instance(
        r"a_{n} = 2 a_{n - 1}, \quad a_{0} = 1",
        recurrence([2], [1]),
        ["LinearRecurrences"],
    ),
    "naturals_recurrence": instance(
        r"a_{n} = 2 a_{n - 1} - a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([2, -1], [0, 1]),
        ["LinearRecurrences"],
        "A repeated characteristic root: the solution is n itself.",
    ),
    "squares_recurrence": instance(
        r"a_{n} = 3 a_{n - 1} - 3 a_{n - 2} + a_{n - 3}, \quad a_{0} = 0, a_{1} = 1, a_{2} = 4",
        recurrence([3, -3, 1], [0, 1, 4]),
        ["LinearRecurrences"],
    ),
    "fibonacci_squares": instance(
        r"a_{n} = 2 a_{n - 1} + 2 a_{n - 2} - a_{n - 3}, \quad a_{0} = 0, a_{1} = 1, a_{2} = 1",
        recurrence([2, 2, -1], [0, 1, 1]),
        ["LinearRecurrences"],
        r"$F_{n}^{2}$.",
    ),
    "even_fibonacci": instance(
        r"a_{n} = 3 a_{n - 1} - a_{n - 2}, \quad a_{0} = 0, a_{1} = 1",
        recurrence([3, -1], [0, 1]),
        ["LinearRecurrences"],
        r"$F_{2n} = F_{n} L_{n}$.",
    ),
    "lucas_squares": instance(
        r"a_{n} = 2 a_{n - 1} + 2 a_{n - 2} - a_{n - 3}, \quad a_{0} = 4, a_{1} = 1, a_{2} = 9",
        recurrence([2, 2, -1], [4, 1, 9]),
        ["LinearRecurrences"],
        r"$L_{n}^{2}$.",
    ),
    "constant_two": instance(
        r"a_{n} = a_{n - 1}, \quad a_{0} = 2", recurrence([1], [2]), ["LinearRecurrences"]
    ),
    "one_plus_powers_of_three": instance(
        r"a_{n} = 4 a_{n - 1} - 3 a_{n - 2}, \quad a_{0} = 2, a_{1} = 4",
        recurrence([4, -3], [2, 4]),
        ["LinearRecurrences"],
        r"$1 + 3^{n}$.",
    ),
    "rotation90_traces": instance(
        r"a_{n} = - a_{n - 2}, \quad a_{0} = 2, a_{1} = 0",
        recurrence([0, -1], [2, 0]),
        ["LinearRecurrences"],
        r"$2, 0, -2, 0, 2, \dots$",
    ),
    "cycle3_traces": instance(
        r"a_{n} = a_{n - 3}, \quad a_{0} = 3, a_{1} = 0, a_{2} = 0",
        recurrence([0, 0, 1], [3, 0, 0]),
        ["LinearRecurrences"],
        r"$3, 0, 0, 3, 0, 0, \dots$",
    ),
    "powers_of_four": instance(
        r"a_{n} = 4 a_{n - 1}, \quad a_{0} = 1",
        recurrence([4], [1]),
        ["LinearRecurrences"],
    ),
    "central_binomial_squares": instance(
        r"\left(n + 1\right)^{2} a_{n + 1} - 4 \left(2 n + 1\right)^{2} a_{n} = 0, \quad a_{0} = 1",
        holonomic([[-4, -16, -16], [1, 2, 1]], [1]),
        ["HolonomicSequences"],
        r"$\binom{2n}{n}^{2}$: $1, 4, 36, 400, \dots$",
    ),
}

REFERENCES: dict[str, list[Reference]] = {
    "catalan_numbers": oeis("A000108"),
    "central_binomials": oeis("A000984"),
    "apery_numbers": oeis("A005259"),
    "fibonacci": oeis("A000045"),
    "lucas": oeis("A000032"),
    "pell": oeis("A000129"),
    "squares": oeis("A000290"),
    "powers_of_two": oeis("A000079"),
    "factorials": oeis("A000142"),
    "prime_counting": oeis("A000720"),
    "big_omega": oeis("A001222"),
    "little_omega": oeis("A001221"),
    "totient": oeis("A000010"),
    "divisor_sum": oeis("A000203"),
    "mobius": oeis("A008683"),
    "first_lucas": oeis("A000032"),
    "first_pell": oeis("A000129"),
    "first_catalan": oeis("A000108"),
    "first_central_binomials": oeis("A000984"),
    "first_apery": oeis("A005259"),
    "running_primes": oeis("A007504"),
    "running_factorials": oeis("A007489"),
    "sum_of_squares": oeis("A000330"),
    "mersenne": oeis("A000225"),
    "harmonic_numbers": oeis("A001008"),
    "odd_numbers": oeis("A005408"),
    "naturals": oeis("A001477"),
    "divisor_count_function": oeis("A000005"),
    "fibonacci_squares": oeis("A007598"),
    "even_fibonacci": oeis("A001906"),
    "lucas_squares": oeis("A001254"),
    "powers_of_four": oeis("A000302"),
    "central_binomial_squares": oeis("A002894"),
    "HankelTransform": [
        (
            "Layman, The Hankel Transform and Some of Its Properties",
            "https://cs.uwaterloo.ca/journals/JIS/VOL4/LAYMAN/hankel.html",
        )
    ],
    "DirichletConvolution": [("Wikipedia", "https://en.wikipedia.org/wiki/Dirichlet_convolution")],
}

SECTIONS: dict[str, Specimen] = {
    "SequenceOperations": (
        r"\text{Sequence Operations}",
        "Operations taking a sequence as their input.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "ReadAtN": (
        r"\text{Read at } n",
        r"Evaluate a sequence as a map from the integers: the term $a_{n}$, counting a finite "
        "sequence from 1.",
    ),
    "AsSequence": (
        r"\text{As Sequence}",
        r"Lift a map from the positive integers to an object: the sequence $f(1), f(2), \dots$ "
        r"Read at $n$ undoes it. An operator carries no value a computation could read, so its "
        "relations are entered by hand.",
    ),
    "PartialSums": (
        r"\text{Partial Sums}",
        r"The running totals $a_{s} + \dots + a_{n}$.",
    ),
    "ClosedForm": (
        r"\text{Closed Form}",
        "The formula in n solving a linear recurrence with constant coefficients.",
    ),
    "FindLinearRecurrence": (
        r"\text{Find Linear Recurrence}",
        "The shortest linear recurrence with constant coefficients the terms satisfy. On a "
        "finite sequence it is a guess fitted to the terms given, not a proof.",
    ),
    "GuessPRecursive": (
        r"\text{Guess P-recursive Recurrence}",
        "A recurrence with polynomial coefficients fitted to finitely many terms. Nothing in the "
        "sandbox computes it, so its relations are entered by hand.",
    ),
    "TermwiseProduct": (
        r"\text{Termwise Product}",
        r"The sequence $a_{n} b_{n}$. Both classes, constant and polynomial coefficients, are "
        "closed under it.",
    ),
    "DirichletConvolution": (
        r"\text{Dirichlet Convolution}",
        r"$(f * g)(n) = \sum_{d \mid n} f(d) g(n / d)$, recognised among the standard arithmetic "
        "functions by its first terms.",
    ),
    "RecurrenceCharacteristicPolynomial": (
        r"\text{Characteristic Polynomial of a Recurrence}",
        r"For $a_{n} = c_{1} a_{n-1} + \dots + c_{k} a_{n-k}$, the polynomial "
        r"$x^{k} - c_{1} x^{k-1} - \dots - c_{k}$.",
    ),
    "GeneratingFunction": (
        r"\text{Generating Function}",
        r"$\sum a_{n} x^{n}$ as a function: rational for constant coefficients, D-finite for "
        "polynomial ones.",
    ),
    "HankelMatrix": (
        r"\text{Hankel Matrix}",
        r"For $a_{0}, \dots, a_{2k}$, the symmetric matrix $(a_{i+j})_{0 \le i, j \le k}$.",
    ),
    "HankelTransform": (
        r"\text{Hankel Transform}",
        r"The determinants $\det (a_{i+j})_{0 \le i, j \le n}$, as far as the terms given reach.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("ReadAtN", "SequencesByFormula", "Integers"),
    ("ReadAtN", "SequencesByFormula", "RationalNumbers"),
    ("ReadAtN", "FiniteSequences", "Integers"),
    ("ReadAtN", "HolonomicSequences", "Integers"),
    ("PartialSums", "SequencesByFormula", "SequencesByFormula"),
    ("PartialSums", "FiniteSequences", "FiniteSequences"),
    ("ClosedForm", "LinearRecurrences", "SequencesByFormula"),
    ("FindLinearRecurrence", "SequencesByFormula", "LinearRecurrences"),
    ("FindLinearRecurrence", "FiniteSequences", "LinearRecurrences"),
    ("GuessPRecursive", "FiniteSequences", "HolonomicSequences"),
    ("TermwiseProduct", "LinearRecurrences", "LinearRecurrences"),
    ("TermwiseProduct", "HolonomicSequences", "HolonomicSequences"),
    ("DirichletConvolution", "ArithmeticFunctions", "ArithmeticFunctions"),
    ("DirichletConvolution", "MultiplicativeFunctions", "MultiplicativeFunctions"),
    ("RecurrenceCharacteristicPolynomial", "LinearRecurrences", "Polynomials"),
    ("GeneratingFunction", "LinearRecurrences", "RationalFunctions"),
    ("GeneratingFunction", "HolonomicSequences", "DFiniteFunctions"),
    ("HankelMatrix", "FiniteSequences", "SymmetricMatrices"),
    ("HankelTransform", "FiniteSequences", "FiniteSequences"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "ReadAtN": "read_at_n",
    "PartialSums": "partial_sums",
    "ClosedForm": "closed_form",
    "FindLinearRecurrence": "find_linear_recurrence",
    "TermwiseProduct": "termwise_product",
    "DirichletConvolution": "dirichlet_convolution",
    "RecurrenceCharacteristicPolynomial": "recurrence_characteristic_polynomial",
    "GeneratingFunction": "generating_function",
    "HankelMatrix": "hankel_matrix",
    "HankelTransform": "hankel_transform",
}

RELATIONS: list[RelationSpec] = [
    ("ReadAtN", ["squares", 7], [49]),
    ("ReadAtN", ["fibonacci", 10], [55]),
    ("ReadAtN", ["binet", 10], [55]),
    ("ReadAtN", ["catalan_numbers", 5], [42]),
    ("ReadAtN", ["apery_numbers", 3], [1445]),
    ("ReadAtN", ["first_primes", 5], [11]),
    ("ReadAtN", ["first_fibonacci", 4], [3]),
    ("ReadAtN", ["totient", 12], [4]),
    ("ReadAtN", ["prime_counting", 100], [25]),
    ("ReadAtN", ["mobius", 30], [-1]),
    ("ReadAtN", ["reciprocals", 4], [Fraction(1, 4)]),
    ("AsSequence", ["EulerTotient"], ["totient"]),
    ("AsSequence", ["DivisorCount"], ["divisor_count_function"]),
    ("PartialSums", ["squares"], ["sum_of_squares"]),
    ("PartialSums", ["powers_of_two"], ["mersenne"]),
    ("PartialSums", ["reciprocals"], ["harmonic_numbers"]),
    ("PartialSums", ["odd_numbers"], ["squares_from_one"]),
    ("PartialSums", ["first_fibonacci"], ["running_fibonacci"]),
    ("PartialSums", ["first_primes"], ["running_primes"]),
    ("PartialSums", ["first_factorials"], ["running_factorials"]),
    ("ClosedForm", ["fibonacci"], ["binet"]),
    ("ClosedForm", ["lucas"], ["lucas_closed_form"]),
    ("ClosedForm", ["pell"], ["pell_closed_form"]),
    ("ClosedForm", ["doubling"], ["powers_of_two"]),
    ("ClosedForm", ["naturals_recurrence"], ["naturals"]),
    ("FindLinearRecurrence", ["powers_of_two"], ["doubling"]),
    ("FindLinearRecurrence", ["squares"], ["squares_recurrence"]),
    ("FindLinearRecurrence", ["binet"], ["fibonacci"]),
    ("FindLinearRecurrence", ["naturals"], ["naturals_recurrence"]),
    ("FindLinearRecurrence", ["first_lucas"], ["lucas"]),
    ("FindLinearRecurrence", ["first_pell"], ["pell"]),
    ("GuessPRecursive", ["first_catalan"], ["catalan_numbers"]),
    ("GuessPRecursive", ["first_central_binomials"], ["central_binomials"]),
    ("GuessPRecursive", ["first_apery"], ["apery_numbers"]),
    ("TermwiseProduct", ["fibonacci", "fibonacci"], ["fibonacci_squares"]),
    ("TermwiseProduct", ["fibonacci", "lucas"], ["even_fibonacci"]),
    ("TermwiseProduct", ["lucas", "lucas"], ["lucas_squares"]),
    ("TermwiseProduct", ["doubling", "doubling"], ["powers_of_four"]),
    ("DirichletConvolution", ["totient", "constant_one"], ["identity_function"]),
    ("DirichletConvolution", ["mobius", "constant_one"], ["unit_function"]),
    ("DirichletConvolution", ["constant_one", "mobius"], ["unit_function"]),
    ("DirichletConvolution", ["constant_one", "constant_one"], ["divisor_count_function"]),
    ("DirichletConvolution", ["identity_function", "constant_one"], ["divisor_sum"]),
    ("DirichletConvolution", ["mobius", "identity_function"], ["totient"]),
    ("RecurrenceCharacteristicPolynomial", ["fibonacci"], ["golden_polynomial"]),
    ("RecurrenceCharacteristicPolynomial", ["lucas"], ["golden_polynomial"]),
    ("RecurrenceCharacteristicPolynomial", ["pell"], ["pell_polynomial"]),
    ("RecurrenceCharacteristicPolynomial", ["doubling"], ["x_minus_2"]),
    ("RecurrenceCharacteristicPolynomial", ["naturals_recurrence"], ["Q"]),
    ("RecurrenceCharacteristicPolynomial", ["fibonacci_squares"], ["fibonacci_squares_polynomial"]),
    ("GeneratingFunction", ["fibonacci"], ["fibonacci_generating_function"]),
    ("GeneratingFunction", ["lucas"], ["lucas_generating_function"]),
    ("GeneratingFunction", ["pell"], ["pell_generating_function"]),
    ("GeneratingFunction", ["doubling"], ["doubling_generating_function"]),
    ("GeneratingFunction", ["naturals_recurrence"], ["naturals_generating_function"]),
    ("HankelMatrix", ["first_catalan"], ["hankel_catalan"]),
    ("HankelMatrix", ["first_central_binomials"], ["hankel_central_binomials"]),
    ("HankelMatrix", ["first_fibonacci"], ["hankel_fibonacci"]),
    ("HankelMatrix", ["first_factorials"], ["hankel_factorials"]),
    ("HankelMatrix", ["first_primes"], ["hankel_primes"]),
    ("Determinant", ["hankel_catalan"], [1]),
    ("Determinant", ["hankel_central_binomials"], [4]),
    ("Determinant", ["hankel_fibonacci"], [0]),
    ("Determinant", ["hankel_factorials"], [24]),
    ("Determinant", ["hankel_primes"], [-2]),
    ("HankelTransform", ["first_catalan"], ["catalan_hankel_transform"]),
    ("HankelTransform", ["first_central_binomials"], ["central_hankel_transform"]),
    ("HankelTransform", ["first_factorials"], ["factorial_hankel_transform"]),
    ("HankelTransform", ["first_fibonacci"], ["fibonacci_hankel_transform"]),
    ("HankelTransform", ["first_primes"], ["primes_hankel_transform"]),
]

ASSERTED: list[RelationSpec] = [
    ("TermwiseProduct", ["central_binomials", "central_binomials"], ["central_binomial_squares"]),
    ("GeneratingFunction", ["catalan_numbers"], ["catalan_generating_function"]),
    ("GeneratingFunction", ["central_binomials"], ["central_binomial_generating_function"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "ReadAtN": (r"{in0}\op{\text{ at }}{in1} = {out0}", False),
}

FILINGS: dict[str, list[str]] = {
    "SequencesAndRecurrences": ["SequenceOperations"],
    "SequenceOperations": list(OPERATORS),
}
