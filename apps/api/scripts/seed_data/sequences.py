from seed_data.build import Instance, Reference, holonomic, instance, integer, oeis, recurrence, seq

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
}
