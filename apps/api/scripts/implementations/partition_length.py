def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    return len(p.partition)
