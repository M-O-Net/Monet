from seed_data.build import (
    Instance,
    Reference,
    RelationSpec,
    Specimen,
    algebraic,
    dfinite,
    expr,
    instance,
    polynomial,
    rational,
)

INSTANCES: dict[str, Instance] = {
    "exp": (
        "e^{x}",
        "The exponential function.",
        [
            ("ElementaryFunctions", expr("exp(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[-1], [1]], [1])),
        ],
    ),
    "log": instance(r"\log{\left(x \right)}", expr("log(Symbol('x'))"), ["ElementaryFunctions"]),
    "catalan_generating_function": (
        r"\frac{1 - \sqrt{1 - 4 x}}{2 x}",
        "The generating function of the Catalan numbers.",
        [
            (
                "ElementaryFunctions",
                expr(
                    "Mul(Rational(1, 2), Pow(Symbol('x'), Integer(-1)), Add(Integer(1), "
                    "Mul(Integer(-1), Pow(Add(Integer(1), Mul(Integer(-1), Integer(4), "
                    "Symbol('x'))), Rational(1, 2)))))"
                ),
            ),
            ("DFiniteFunctions", dfinite([[2], [-2, 10], [0, -1, 4]], [1, 1])),
        ],
    ),
    "reciprocal_shift": instance(
        r"\frac{1}{x - 1}",
        expr("Pow(Add(Symbol('x'), Integer(-1)), Integer(-1))"),
        ["RationalFunctions"],
    ),
    "mobius_transformation": instance(
        r"\frac{x + 1}{x - 1}",
        expr("Mul(Pow(Add(Symbol('x'), Integer(-1)), Integer(-1)), Add(Symbol('x'), Integer(1)))"),
        ["RationalFunctions"],
    ),
    "lorentzian": (
        r"\frac{1}{x^{2} + 1}",
        r"The derivative of $\arctan x$.",
        [
            *(
                (kind, expr("Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1))"))
                for kind in ("RationalFunctions", "EvenFunctions")
            ),
            ("DFiniteFunctions", dfinite([[0, 2], [1, 0, 1]], [1])),
        ],
    ),
    "odd_rational": instance(
        r"\frac{x}{x^{2} + 1}",
        expr("Mul(Symbol('x'), Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1)))"),
        ["RationalFunctions", "OddFunctions"],
    ),
    "cos": (
        r"\cos{\left(x \right)}",
        None,
        [
            ("EvenFunctions", expr("cos(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[1], [0], [1]], [1, 0])),
        ],
    ),
    "sin": (
        r"\sin{\left(x \right)}",
        None,
        [
            ("OddFunctions", expr("sin(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[1], [0], [1]], [0, 1])),
        ],
    ),
    "arctan": (
        r"\operatorname{atan}{\left(x \right)}",
        "The inverse tangent.",
        [
            ("OddFunctions", expr("atan(Symbol('x'))")),
            ("DFiniteFunctions", dfinite([[0], [0, 2], [1, 0, 1]], [0, 1])),
        ],
    ),
    "airy_ai": instance(
        r"y'' - x y = 0, \quad y(0) = \frac{\sqrt[3]{3}}{3 \Gamma\left(\frac{2}{3}\right)}, "
        r"y'(0) = - \frac{3^{\frac{2}{3}}}{3 \Gamma\left(\frac{1}{3}\right)}",
        dfinite(
            [[0, -1], [0], [1]],
            [
                expr(
                    "Mul(Rational(1, 3), Pow(Integer(3), Rational(1, 3)), "
                    "Pow(gamma(Rational(2, 3)), Integer(-1)))"
                ),
                expr(
                    "Mul(Integer(-1), Rational(1, 3), Pow(Integer(3), Rational(2, 3)), "
                    "Pow(gamma(Rational(1, 3)), Integer(-1)))"
                ),
            ],
        ),
        ["DFiniteFunctions"],
        r"The Airy function $\operatorname{Ai}(x)$: D-finite, but not elementary.",
    ),
    "riccati": instance(
        r"\frac{d}{d x} y{\left(x \right)} = y^{2}{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1))), "
            "Pow(Function('y')(Symbol('x')), Integer(2)))"
        ),
        ["OrdinaryDifferentialEquations"],
        "Nonlinear: its solutions blow up in finite time.",
    ),
    "airy_equation": instance(
        r"\frac{d^{2}}{d x^{2}} y{\left(x \right)} = x y{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(2))), "
            "Mul(Symbol('x'), Function('y')(Symbol('x'))))"
        ),
        ["OrdinaryDifferentialEquations"],
        "The Airy equation: linear, with a coefficient that is not constant.",
    ),
    "pendulum": instance(
        r"\sin{\left(y{\left(x \right)} \right)} + \frac{d^{2}}{d x^{2}} y{\left(x \right)} = 0",
        expr(
            "Equality(Add(sin(Function('y')(Symbol('x'))), Derivative(Function('y')(Symbol('x')),"
            " Tuple(Symbol('x'), Integer(2)))), Integer(0))"
        ),
        ["OrdinaryDifferentialEquations"],
        "The undamped pendulum.",
    ),
    "harmonic_oscillator": instance(
        r"y{\left(x \right)} + \frac{d^{2}}{d x^{2}} y{\left(x \right)} = 0",
        expr(
            "Equality(Add(Function('y')(Symbol('x')), Derivative(Function('y')(Symbol('x')), "
            "Tuple(Symbol('x'), Integer(2)))), Integer(0))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"The harmonic oscillator, solved by $\sin x$ and $\cos x$.",
    ),
    "two_exponentials": instance(
        r"2 y{\left(x \right)} - 3 \frac{d}{d x} y{\left(x \right)} + \frac{d^{2}}{d x^{2}} "
        r"y{\left(x \right)} = 0",
        expr(
            "Equality(Add(Mul(Integer(2), Function('y')(Symbol('x'))), Mul(Integer(-1), "
            "Integer(3), Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1)))),"
            " Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(2)))), "
            "Integer(0))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"Solved by $e^{x}$ and $e^{2x}$.",
    ),
    "growth": instance(
        r"\frac{d}{d x} y{\left(x \right)} = y{\left(x \right)}",
        expr(
            "Equality(Derivative(Function('y')(Symbol('x')), Tuple(Symbol('x'), Integer(1))), "
            "Function('y')(Symbol('x')))"
        ),
        ["LinearConstantCoefficientODEs"],
        r"Exponential growth, solved by $e^{x}$.",
    ),
    "fibonacci_generating_function": instance(
        r"\frac{x}{1 - x - x^{2}}",
        expr(
            "Mul(Symbol('x'), Pow(Add(Mul(Integer(-1), Pow(Symbol('x'), Integer(2))), "
            "Mul(Integer(-1), Symbol('x')), Integer(1)), Integer(-1)))"
        ),
        ["RationalFunctions"],
    ),
    "lucas_generating_function": instance(
        r"\frac{2 - x}{1 - x - x^{2}}",
        expr(
            "Mul(Add(Integer(2), Mul(Integer(-1), Symbol('x'))), Pow(Add(Mul(Integer(-1), "
            "Pow(Symbol('x'), Integer(2))), Mul(Integer(-1), Symbol('x')), Integer(1)), "
            "Integer(-1)))"
        ),
        ["RationalFunctions"],
    ),
    "pell_generating_function": instance(
        r"\frac{x}{1 - 2 x - x^{2}}",
        expr(
            "Mul(Symbol('x'), Pow(Add(Mul(Integer(-1), Pow(Symbol('x'), Integer(2))), "
            "Mul(Integer(-1), Integer(2), Symbol('x')), Integer(1)), Integer(-1)))"
        ),
        ["RationalFunctions"],
    ),
    "doubling_generating_function": instance(
        r"\frac{1}{1 - 2 x}",
        expr("Pow(Add(Integer(1), Mul(Integer(-1), Integer(2), Symbol('x'))), Integer(-1))"),
        ["RationalFunctions"],
    ),
    "naturals_generating_function": instance(
        r"\frac{x}{1 - 2 x + x^{2}}",
        expr(
            "Mul(Symbol('x'), Pow(Add(Pow(Symbol('x'), Integer(2)), Mul(Integer(-1), "
            "Integer(2), Symbol('x')), Integer(1)), Integer(-1)))"
        ),
        ["RationalFunctions"],
        r"$\frac{x}{(1 - x)^{2}} = x + 2 x^{2} + 3 x^{3} + \dots$",
    ),
    "central_binomial_generating_function": (
        r"\frac{1}{\sqrt{1 - 4 x}}",
        r"The generating function of the central binomial coefficients $\binom{2n}{n}$.",
        [
            (
                "ElementaryFunctions",
                expr(
                    "Pow(Add(Integer(1), Mul(Integer(-1), Integer(4), Symbol('x'))), "
                    "Rational(-1, 2))"
                ),
            ),
            ("DFiniteFunctions", dfinite([[2], [-1, 4]], [1])),
        ],
    ),
    "minus_sin": instance(
        r"- \sin{\left(x \right)}", expr("Mul(Integer(-1), sin(Symbol('x')))"), ["OddFunctions"]
    ),
    "minus_cos": instance(
        r"- \cos{\left(x \right)}", expr("Mul(Integer(-1), cos(Symbol('x')))"), ["EvenFunctions"]
    ),
    "reciprocal_x": instance(
        r"\frac{1}{x}",
        expr("Pow(Symbol('x'), Integer(-1))"),
        ["RationalFunctions", "OddFunctions"],
    ),
    "lorentzian_derivative": instance(
        r"- \frac{2 x}{\left(x^{2} + 1\right)^{2}}",
        expr(
            "Mul(Integer(-1), Integer(2), Symbol('x'), Pow(Add(Pow(Symbol('x'), Integer(2)), "
            "Integer(1)), Integer(-2)))"
        ),
        ["RationalFunctions", "OddFunctions"],
    ),
    "odd_rational_derivative": instance(
        r"- \frac{\left(x - 1\right) \left(x + 1\right)}{\left(x^{2} + 1\right)^{2}}",
        expr(
            "Mul(Integer(-1), Add(Symbol('x'), Integer(-1)), Add(Symbol('x'), Integer(1)), "
            "Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-2)))"
        ),
        ["RationalFunctions", "EvenFunctions"],
    ),
    "reciprocal_shift_derivative": instance(
        r"- \frac{1}{\left(x - 1\right)^{2}}",
        expr("Mul(Integer(-1), Pow(Add(Symbol('x'), Integer(-1)), Integer(-2)))"),
        ["RationalFunctions"],
    ),
    "log_shift": instance(
        r"\log{\left(x - 1 \right)}",
        expr("log(Add(Symbol('x'), Integer(-1)))"),
        ["ElementaryFunctions"],
    ),
    "x_log_x_minus_x": instance(
        r"x \log{\left(x \right)} - x",
        expr("Add(Mul(Symbol('x'), log(Symbol('x'))), Mul(Integer(-1), Symbol('x')))"),
        ["ElementaryFunctions"],
    ),
    "half_log_lorentz": instance(
        r"\frac{\log{\left(x^{2} + 1 \right)}}{2}",
        expr("Mul(Rational(1, 2), log(Add(Pow(Symbol('x'), Integer(2)), Integer(1))))"),
        ["EvenFunctions"],
    ),
    "exp2x_minus_expx": instance(
        r"e^{2 x} - e^{x}",
        expr("Add(exp(Mul(Integer(2), Symbol('x'))), Mul(Integer(-1), exp(Symbol('x'))))"),
        ["ElementaryFunctions"],
    ),
    "riccati_solution": instance(
        r"- \frac{1}{x - 1}",
        expr("Mul(Integer(-1), Pow(Add(Symbol('x'), Integer(-1)), Integer(-1)))"),
        ["RationalFunctions"],
        r"$\frac{1}{1 - x}$: it blows up at $x = 1$.",
    ),
    "minus_golden_ratio": instance(
        r"- \frac{1}{2} - \frac{\sqrt{5}}{2}", algebraic([-1, 1, 1], 0), ["AlgebraicIntegers"]
    ),
    "golden_ratio_reciprocal": instance(
        r"- \frac{1}{2} + \frac{\sqrt{5}}{2}",
        algebraic([-1, 1, 1], 1),
        ["AlgebraicIntegers"],
        r"$1 / \varphi = \varphi - 1$.",
    ),
    "two_x_minus_4": instance(
        "2 x - 4", polynomial(-4, 2), ["IntegerPolynomials", "IrreduciblePolynomials"]
    ),
    "P_antiderivative": instance(
        r"\frac{x^{3}}{3} - 2 x^{2} + 3 x",
        polynomial(0, 3, -2, rational(1, 3)),
        ["Polynomials"],
    ),
    "taylor_exp_3": instance(
        r"\frac{x^{3}}{6} + \frac{x^{2}}{2} + x + 1",
        polynomial(1, 1, rational(1, 2), rational(1, 6)),
        ["IrreduciblePolynomials"],
    ),
    "taylor_sin_5": instance(
        r"\frac{x^{5}}{120} - \frac{x^{3}}{6} + x",
        polynomial(0, 1, 0, rational(-1, 6), 0, rational(1, 120)),
        ["Polynomials"],
    ),
    "taylor_cos_4": instance(
        r"\frac{x^{4}}{24} - \frac{x^{2}}{2} + 1",
        polynomial(1, 0, rational(-1, 2), 0, rational(1, 24)),
        ["IrreduciblePolynomials"],
    ),
    "taylor_arctan_3": instance(
        r"x - \frac{x^{3}}{3}", polynomial(0, 1, 0, rational(-1, 3)), ["Polynomials"]
    ),
}

SECTIONS: dict[str, Specimen] = {
    "AnalysisOperations": (
        r"\text{Analysis Operations}",
        "Operations taking a function or a differential equation as their input.",
    ),
}

OPERATORS: dict[str, Specimen] = {
    "Derivative": (r"\text{Derivative}", r"$\frac{d f}{d x}$."),
    "Antiderivative": (
        r"\text{Antiderivative}",
        r"$\int f \, dx$ with the constant of integration taken to be $0$.",
    ),
    "TaylorPolynomial": (
        r"\text{Taylor Polynomial}",
        r"For $f$ and $n$, the Taylor polynomial of degree $n$ about $0$.",
    ),
    "TaylorSeries": (
        r"\text{Taylor Series}",
        r"For $f$ and a point $a$, the coefficients $f^{(n)}(a) / n!$ of the whole series: a "
        "formula when one formula gives every coefficient from n = 0, a P-recursive sequence "
        "for a D-finite function about its own base point.",
    ),
    "CoefficientFormula": (
        r"\text{Coefficient Formula}",
        r"The Taylor coefficients about $0$ as a formula in $n$: Taylor Series at $0$.",
    ),
    "Poles": (
        r"\text{Poles}",
        "The roots of the reduced denominator of a rational function, repeated by order.",
    ),
    "SolveODE": (
        r"\text{Solve ODE}",
        r"The solution of an ordinary differential equation in $y(x)$ from initial values "
        r"$y(0), y'(0), \dots$, one further input per order.",
    ),
    "ODECharacteristicPolynomial": (
        r"\text{Characteristic Polynomial of a Linear ODE}",
        r"Replace $y^{(k)}$ by $x^{k}$ and make the result monic. Its roots are the exponents "
        "of the solutions.",
    ),
    "HolonomicAnnihilator": (
        r"\text{Holonomic Annihilator}",
        "The linear differential equation with polynomial coefficients, and initial values at "
        "0, that a function satisfies.",
    ),
    "CoefficientRecurrence": (
        r"\text{Coefficient Recurrence}",
        "The recurrence the Taylor coefficients about 0 satisfy: constant coefficients for a "
        "rational function, polynomial ones for a D-finite function. The inverse of "
        "Generating Function.",
    ),
}

SIGNATURES: list[tuple[str, str, str]] = [
    ("Derivative", "ElementaryFunctions", "ElementaryFunctions"),
    ("Derivative", "RationalFunctions", "RationalFunctions"),
    ("Derivative", "EvenFunctions", "OddFunctions"),
    ("Derivative", "OddFunctions", "EvenFunctions"),
    ("Derivative", "Polynomials", "Polynomials"),
    ("Antiderivative", "ElementaryFunctions", "ElementaryFunctions"),
    ("Antiderivative", "RationalFunctions", "ElementaryFunctions"),
    ("Antiderivative", "Polynomials", "Polynomials"),
    ("TaylorPolynomial", "ElementaryFunctions", "Polynomials"),
    ("TaylorPolynomial", "Polynomials", "Polynomials"),
    ("TaylorSeries", "ElementaryFunctions", "SequencesByFormula"),
    ("TaylorSeries", "Polynomials", "SequencesByFormula"),
    ("TaylorSeries", "DFiniteFunctions", "HolonomicSequences"),
    ("CoefficientFormula", "ElementaryFunctions", "SequencesByFormula"),
    ("CoefficientFormula", "Polynomials", "SequencesByFormula"),
    ("Poles", "RationalFunctions", "AlgebraicNumbers"),
    ("Poles", "RationalFunctions", "RationalNumbers"),
    ("SolveODE", "OrdinaryDifferentialEquations", "ElementaryFunctions"),
    ("SolveODE", "LinearConstantCoefficientODEs", "ElementaryFunctions"),
    ("ODECharacteristicPolynomial", "LinearConstantCoefficientODEs", "Polynomials"),
    ("HolonomicAnnihilator", "ElementaryFunctions", "DFiniteFunctions"),
    ("HolonomicAnnihilator", "Polynomials", "DFiniteFunctions"),
    ("CoefficientRecurrence", "DFiniteFunctions", "HolonomicSequences"),
    ("CoefficientRecurrence", "ElementaryFunctions", "HolonomicSequences"),
    ("CoefficientRecurrence", "RationalFunctions", "LinearRecurrences"),
]

IMPLEMENTATIONS: dict[str, str] = {
    "Derivative": "derivative",
    "Antiderivative": "antiderivative",
    "TaylorPolynomial": "taylor_polynomial",
    "TaylorSeries": "taylor_series",
    "CoefficientFormula": "coefficient_formula",
    "Poles": "poles",
    "SolveODE": "solve_ode",
    "ODECharacteristicPolynomial": "ode_characteristic_polynomial",
    "HolonomicAnnihilator": "holonomic_annihilator",
    "CoefficientRecurrence": "coefficient_recurrence",
}

RELATIONS: list[RelationSpec] = [
    ("Derivative", ["sin"], ["cos"]),
    ("Derivative", ["cos"], ["minus_sin"]),
    ("Derivative", ["exp"], ["exp"]),
    ("Derivative", ["log"], ["reciprocal_x"]),
    ("Derivative", ["arctan"], ["lorentzian"]),
    ("Derivative", ["lorentzian"], ["lorentzian_derivative"]),
    ("Derivative", ["odd_rational"], ["odd_rational_derivative"]),
    ("Derivative", ["reciprocal_shift"], ["reciprocal_shift_derivative"]),
    ("Derivative", ["P"], ["two_x_minus_4"]),
    ("Antiderivative", ["cos"], ["sin"]),
    ("Antiderivative", ["sin"], ["minus_cos"]),
    ("Antiderivative", ["exp"], ["exp"]),
    ("Antiderivative", ["lorentzian"], ["arctan"]),
    ("Antiderivative", ["reciprocal_x"], ["log"]),
    ("Antiderivative", ["reciprocal_shift"], ["log_shift"]),
    ("Antiderivative", ["log"], ["x_log_x_minus_x"]),
    ("Antiderivative", ["odd_rational"], ["half_log_lorentz"]),
    ("Antiderivative", ["P"], ["P_antiderivative"]),
    ("TaylorPolynomial", ["exp", 3], ["taylor_exp_3"]),
    ("TaylorPolynomial", ["sin", 5], ["taylor_sin_5"]),
    ("TaylorPolynomial", ["cos", 4], ["taylor_cos_4"]),
    ("TaylorPolynomial", ["lorentzian", 4], ["Phi12"]),
    ("TaylorPolynomial", ["arctan", 3], ["taylor_arctan_3"]),
    ("TaylorPolynomial", ["P", 5], ["P"]),
    ("TaylorSeries", ["exp", 0], ["reciprocal_factorials"]),
    ("TaylorSeries", ["exp", 1], ["e_over_factorials"]),
    ("TaylorSeries", ["reciprocal_shift", 0], ["constant_minus_one"]),
    ("TaylorSeries", ["reciprocal_shift", 2], ["alternating_signs"]),
    ("TaylorSeries", ["airy_ai", 0], ["airy_coefficients"]),
    ("CoefficientFormula", ["exp"], ["reciprocal_factorials"]),
    ("CoefficientFormula", ["reciprocal_shift"], ["constant_minus_one"]),
    ("CoefficientFormula", ["doubling_generating_function"], ["powers_of_two"]),
    ("Poles", ["reciprocal_shift"], [1]),
    ("Poles", ["mobius_transformation"], [1]),
    ("Poles", ["lorentzian"], ["minus_i", "i"]),
    ("Poles", ["odd_rational"], ["minus_i", "i"]),
    ("Poles", ["reciprocal_shift_derivative"], [1, 1]),
    ("Poles", ["reciprocal_x"], [0]),
    ("Poles", ["fibonacci_generating_function"], ["minus_golden_ratio", "golden_ratio_reciprocal"]),
    ("SolveODE", ["harmonic_oscillator", 0, 1], ["sin"]),
    ("SolveODE", ["harmonic_oscillator", 1, 0], ["cos"]),
    ("SolveODE", ["growth", 1], ["exp"]),
    ("SolveODE", ["two_exponentials", 1, 1], ["exp"]),
    ("SolveODE", ["two_exponentials", 0, 1], ["exp2x_minus_expx"]),
    ("SolveODE", ["riccati", 1], ["riccati_solution"]),
    ("ODECharacteristicPolynomial", ["harmonic_oscillator"], ["Phi4"]),
    ("ODECharacteristicPolynomial", ["two_exponentials"], ["diag12_polynomial"]),
    ("ODECharacteristicPolynomial", ["growth"], ["Phi1"]),
    ("HolonomicAnnihilator", ["exp"], ["exp"]),
    ("HolonomicAnnihilator", ["sin"], ["sin"]),
    ("HolonomicAnnihilator", ["cos"], ["cos"]),
    ("HolonomicAnnihilator", ["lorentzian"], ["lorentzian"]),
    ("HolonomicAnnihilator", ["catalan_generating_function"], ["catalan_generating_function"]),
    (
        "HolonomicAnnihilator",
        ["central_binomial_generating_function"],
        ["central_binomial_generating_function"],
    ),
    ("CoefficientRecurrence", ["catalan_generating_function"], ["catalan_numbers"]),
    ("CoefficientRecurrence", ["central_binomial_generating_function"], ["central_binomials"]),
    ("CoefficientRecurrence", ["exp"], ["exp_coefficients"]),
    ("CoefficientRecurrence", ["sin"], ["sine_coefficients"]),
    ("CoefficientRecurrence", ["airy_ai"], ["airy_coefficients"]),
    ("CoefficientRecurrence", ["fibonacci_generating_function"], ["fibonacci"]),
    ("CoefficientRecurrence", ["lucas_generating_function"], ["lucas"]),
    ("CoefficientRecurrence", ["pell_generating_function"], ["pell"]),
    ("CoefficientRecurrence", ["doubling_generating_function"], ["doubling"]),
    ("CoefficientRecurrence", ["naturals_generating_function"], ["naturals_recurrence"]),
    ("CoefficientRecurrence", ["lorentzian"], ["lorentzian_coefficients"]),
    ("CoefficientRecurrence", ["reciprocal_shift"], ["constant_minus_one_recurrence"]),
]

DISPLAYS: dict[str, tuple[str | None, bool]] = {
    "Derivative": (r"\op{\frac{d}{dx}} {in0} = {out0}", False),
    "Antiderivative": (r"\op{\int} {in0} \op{\, dx} = {out0}", False),
}

REFERENCES: dict[str, list[Reference]] = {
    "airy_coefficients": [("DLMF 9.4", "https://dlmf.nist.gov/9.4")],
    "HolonomicAnnihilator": [
        ("Wikipedia", "https://en.wikipedia.org/wiki/Holonomic_function"),
    ],
}

FILINGS: dict[str, list[str]] = {
    "Analysis": ["AnalysisOperations"],
    "AnalysisOperations": [*OPERATORS, "Evaluate"],
}
