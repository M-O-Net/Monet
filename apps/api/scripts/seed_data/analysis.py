from seed_data.build import Instance, dfinite, expr, instance

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
    "lorentzian": instance(
        r"\frac{1}{x^{2} + 1}",
        expr("Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1))"),
        ["RationalFunctions", "EvenFunctions"],
        r"The derivative of $\arctan x$.",
    ),
    "odd_rational": instance(
        r"\frac{x}{x^{2} + 1}",
        expr("Mul(Symbol('x'), Pow(Add(Pow(Symbol('x'), Integer(2)), Integer(1)), Integer(-1)))"),
        ["RationalFunctions", "OddFunctions"],
    ),
    "cos": instance(r"\cos{\left(x \right)}", expr("cos(Symbol('x'))"), ["EvenFunctions"]),
    "sin": instance(r"\sin{\left(x \right)}", expr("sin(Symbol('x'))"), ["OddFunctions"]),
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
}
