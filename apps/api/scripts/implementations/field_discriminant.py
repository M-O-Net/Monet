from sympy.polys.numberfields.basis import round_two


def accepts(f):
    return isinstance(f, NumberField)


def compute(f):
    _, discriminant = round_two(Poly(f.polynomial, Symbol("x"), domain=ZZ))
    return discriminant
