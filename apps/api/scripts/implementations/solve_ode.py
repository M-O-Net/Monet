def _unknown(equation):
    if not isinstance(equation, Equality):
        return None
    x = Symbol("x")
    applied = [f for f in equation.atoms(sympy.core.function.AppliedUndef) if f.args == (x,)]
    return applied[0] if len(applied) == 1 else None


def _canonical(e):
    return factor(cancel(e)) if e.is_rational_function(Symbol("x")) else expand(e)


def accepts(equation):
    return _unknown(equation) is not None


def compute(equation, *initial):
    x, y = Symbol("x"), _unknown(equation)
    order = ode_order(equation, y)
    if len(initial) != order:
        raise ValueError(f"an order {order} equation needs {order} initial values")
    conditions = {y.func(0): initial[0]}
    conditions.update({y.diff(x, k).subs(x, 0): initial[k] for k in range(1, order)})
    solution = dsolve(equation, y, ics=conditions)
    if isinstance(solution, list):
        raise ValueError("the initial values leave more than one solution")
    return _canonical(solution.rhs)
