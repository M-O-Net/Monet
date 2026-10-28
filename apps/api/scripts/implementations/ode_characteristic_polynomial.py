def _coefficients(equation):
    if not isinstance(equation, Equality):
        return None
    x = Symbol("x")
    applied = [f for f in equation.atoms(sympy.core.function.AppliedUndef) if f.args == (x,)]
    if len(applied) != 1:
        return None
    y = applied[0]
    difference = expand(equation.lhs - equation.rhs)
    terms = [y.diff(x, k) if k else y for k in range(ode_order(equation, y) + 1)]
    coefficients = [difference.coeff(term) for term in terms]
    rest = expand(difference - sum(c * t for c, t in zip(coefficients, terms, strict=True)))
    if rest != 0 or any(c.free_symbols for c in coefficients) or coefficients[-1] == 0:
        return None
    return coefficients


def accepts(equation):
    return _coefficients(equation) is not None


def compute(equation):
    x, coefficients = Symbol("x"), _coefficients(equation)
    return sum(c * x**k for k, c in enumerate(coefficients)) / coefficients[-1]
