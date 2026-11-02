def _is_rational(f):
    return isinstance(f, Expr) and f.is_rational_function(Symbol("x"))


def _holonomic(f):
    if isinstance(f, HolonomicFunction):
        return f
    try:
        return sympy.holonomic.expr_to_holonomic(f, Symbol("x"))
    except (NotImplementedError, TypeError, ValueError):
        return None


def accepts(f):
    if isinstance(f, HolonomicFunction):
        return True
    if not (isinstance(f, Expr) and f.free_symbols == {Symbol("x")}):
        return False
    return _is_rational(f) or _holonomic(f) is not None


def _logarithmic_derivative(f):
    expression = f.to_expr() if isinstance(f, HolonomicFunction) else f
    ratio = cancel(simplify(expression.diff(Symbol("x")) / expression))
    return ratio if ratio.is_rational_function(Symbol("x")) else None


def _first_order(ratio):
    numerator, denominator = fraction(together(ratio))
    return [-numerator, denominator]


def _coefficients(f):
    if _is_rational(f):
        return _first_order(cancel(f.diff(Symbol("x")) / f))
    operator = _holonomic(f).annihilator
    coefficients = [operator.parent.base.to_sympy(c) for c in operator.listofpoly]
    if len(coefficients) == 2:
        return coefficients
    if len(coefficients) > 3:
        raise ValueError(
            f"sympy finds an order {len(coefficients) - 1} equation, and Monet cannot "
            "confirm that no lower order exists"
        )
    ratio = _logarithmic_derivative(f)
    return coefficients if ratio is None else _first_order(ratio)


def compute(f):
    x = Symbol("x")
    y = Function("y")(x)
    coefficients = [together(c) for c in _coefficients(f)]
    common = lcm([fraction(c)[1] for c in coefficients])
    polys = [Poly(cancel(c * common), x) for c in coefficients]
    content = gcd_list([p.content() for p in polys if not p.is_zero])
    polys = [p.quo_ground(content) for p in polys]
    if polys[-1].LC() < 0:
        polys = [-p for p in polys]
    terms = [p.as_expr() * y.diff(x, k) for k, p in enumerate(polys) if not p.is_zero]
    return Eq(Add(*terms), 0)
