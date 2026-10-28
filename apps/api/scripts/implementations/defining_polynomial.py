def accepts(f):
    return isinstance(f, NumberField)


def compute(f):
    return f.polynomial
