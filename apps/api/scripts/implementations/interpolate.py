def accepts(values):
    return (
        isinstance(values, Tuple)
        and len(values) > 0
        and all(isinstance(v, Expr) and v.is_Rational for v in values)
    )


def compute(values):
    return expand(interpolate(list(enumerate(values)), Symbol("x")))
