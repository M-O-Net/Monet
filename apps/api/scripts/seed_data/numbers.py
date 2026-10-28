from seed_data.build import (
    Instance,
    RelationSpec,
    Specimen,
    algebraic,
    expr,
    instance,
    integer,
    rational,
    residue,
)

INSTANCES: dict[str, Instance] = {
    "zero": instance("0", integer(0), ["Integers"]),
    "neg_one": instance("-1", integer(-1), ["Integers"]),
    "neg_seven": instance("-7", integer(-7), ["Integers"]),
    "one": instance("1", integer(1), ["PositiveIntegers"]),
    "four": instance("4", integer(4), ["PositiveIntegers"]),
    "six": instance("6", integer(6), ["PositiveIntegers"]),
    "ten": instance("10", integer(10), ["PositiveIntegers"]),
    "twelve": instance("12", integer(12), ["PositiveIntegers"]),
    "fourteen": instance("14", integer(14), ["PositiveIntegers"]),
    "two": instance("2", integer(2), ["PrimeNumbers"]),
    "three": instance("3", integer(3), ["PrimeNumbers"]),
    "five": instance("5", integer(5), ["PrimeNumbers"]),
    "seven": instance("7", integer(7), ["PrimeNumbers"]),
    "thirteen": instance("13", integer(13), ["PrimeNumbers"]),
    "half": instance(r"\frac{1}{2}", rational(1, 2), ["RationalNumbers"]),
    "minus_half": instance(r"- \frac{1}{2}", rational(-1, 2), ["RationalNumbers"]),
    "three_quarters": instance(r"\frac{3}{4}", rational(3, 4), ["RationalNumbers"]),
    "twenty_two_sevenths": instance(
        r"\frac{22}{7}",
        rational(22, 7),
        ["RationalNumbers"],
        r"A classical approximation to $\pi$.",
    ),
    "four_mod_12": instance(r"4 \bmod 12", residue(4, 12), ["ResidueClasses"]),
    "six_mod_9": instance(r"6 \bmod 9", residue(6, 9), ["ResidueClasses"]),
    "zero_mod_5": instance(r"0 \bmod 5", residue(0, 5), ["ResidueClasses"]),
    "five_mod_12": instance(
        r"5 \bmod 12",
        residue(5, 12),
        ["UnitsModN"],
        r"Its own inverse. No unit modulo 12 is a primitive root: every one squares to $1$.",
    ),
    "three_mod_8": instance(r"3 \bmod 8", residue(3, 8), ["UnitsModN"]),
    "four_mod_7": instance(
        r"4 \bmod 7", residue(4, 7), ["UnitsModN"], r"Order 3: its powers are $4, 2, 1$."
    ),
    "three_mod_7": instance(
        r"3 \bmod 7",
        residue(3, 7),
        ["PrimitiveRoots"],
        r"Its powers run through every unit: $3, 2, 6, 4, 5, 1$.",
    ),
    "two_mod_5": instance(r"2 \bmod 5", residue(2, 5), ["PrimitiveRoots"]),
    "three_mod_10": instance(r"3 \bmod 10", residue(3, 10), ["PrimitiveRoots"]),
    "half_sqrt2": instance(r"\frac{\sqrt{2}}{2}", algebraic([-1, 0, 2], 1), ["AlgebraicNumbers"]),
    "half_i": instance(r"\frac{i}{2}", algebraic([1, 0, 4], 1), ["AlgebraicNumbers"]),
    "cbrt_half": instance(
        r"\frac{2^{\frac{2}{3}}}{2}",
        algebraic([-1, 0, 0, 2], 0),
        ["AlgebraicNumbers"],
        r"The real cube root of $\frac{1}{2}$.",
    ),
    "sqrt2": instance(r"\sqrt{2}", algebraic([-2, 0, 1], 1), ["AlgebraicIntegers"]),
    "golden_ratio": instance(
        r"\frac{1}{2} + \frac{\sqrt{5}}{2}",
        algebraic([-1, -1, 1], 1),
        ["AlgebraicIntegers"],
        r"The golden ratio, the larger root of $x^{2} - x - 1$.",
    ),
    "cbrt2": instance(r"\sqrt[3]{2}", algebraic([-2, 0, 0, 1], 0), ["AlgebraicIntegers"]),
    "i": instance(
        "i",
        algebraic([1, 0, 1], 1),
        ["RootsOfUnity", "GaussianIntegers"],
        "A fourth root of unity, and a unit of the Gaussian integers.",
    ),
    "omega": instance(
        r"- \frac{1}{2} + \frac{\sqrt{3} i}{2}",
        algebraic([1, 1, 1], 1),
        ["RootsOfUnity"],
        r"$e^{2 \pi i / 3}$, a primitive cube root of unity.",
    ),
    "zeta5": instance(r"e^{\frac{2 i \pi}{5}}", algebraic([1, 1, 1, 1, 1], 3), ["RootsOfUnity"]),
    "three_plus_4i": instance(
        "3 + 4 i",
        algebraic([25, -6, 1], 1),
        ["GaussianIntegers"],
        r"Norm $25$: it factors as $(2 + i)^{2}$ times a unit.",
    ),
    "two_i": instance("2 i", algebraic([4, 0, 1], 1), ["GaussianIntegers"]),
    "one_plus_i": instance(
        "1 + i",
        algebraic([2, -2, 1], 1),
        ["GaussianPrimes"],
        r"Norm $2$. The only Gaussian prime dividing $2$, up to units.",
    ),
    "two_plus_i": instance(
        "2 + i",
        algebraic([5, -4, 1], 1),
        ["GaussianPrimes"],
        r"Norm $5$: the rational prime $5$ splits as $(2 + i)(2 - i)$.",
    ),
    "three_plus_2i": instance(
        "3 + 2 i", algebraic([13, -6, 1], 1), ["GaussianPrimes"], r"Norm $13$."
    ),
    "true": instance(r"\text{True}", {"bool": True}, ["Booleans"]),
    "false": instance(r"\text{False}", {"bool": False}, ["Booleans"]),
    "pi": instance(r"\pi", expr("pi"), ["Expressions"]),
    "e": instance("e", expr("E"), ["Expressions"], "Euler's number."),
    "zeta3": instance(
        r"\zeta\left(3\right)",
        expr("zeta(Integer(3))"),
        ["Expressions"],
        "Apéry's constant, proved irrational with the help of the Apéry numbers.",
    ),
}

SECTIONS: dict[str, Specimen] = {
    "NumberOperations": (
        r"\text{Number Operations}",
        "Operations taking a whole number as input.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "EulerTotient": (
        r"\text{Euler Totient}",
        r"How many of $1 \dots n$ share no factor with $n$. It is also the degree of "
        r"the $n$th cyclotomic polynomial.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("EulerTotient", "Integers", "Integers"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "EulerTotient": "euler_totient",
}

RELATIONS: list[RelationSpec] = [
    ("EulerTotient", ["six"], ["two"]),
    ("EulerTotient", ["ten"], ["four"]),
    ("EulerTotient", ["fourteen"], ["six"]),
    ("EulerTotient", ["thirteen"], ["twelve"]),
    ("EulerTotient", ["seven"], ["six"]),
    ("EulerTotient", ["five"], ["four"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "EulerTotient": (r"\op{\varphi(}{in0}\op{)} = {out0}", False),
}

FILINGS: dict[str, list[str]] = {
    "NumberTheory": ["NumberOperations"],
    "NumberOperations": ["EulerTotient"],
}
