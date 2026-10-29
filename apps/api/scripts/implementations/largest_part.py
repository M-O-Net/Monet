def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    return max(p.partition)
