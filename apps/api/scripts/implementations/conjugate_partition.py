def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    return IntegerPartition(p.conjugate)
