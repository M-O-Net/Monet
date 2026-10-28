def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    rows = p.partition
    columns = p.conjugate
    hooks = prod(rows[i] - j + columns[j] - i - 1 for i in range(len(rows)) for j in range(rows[i]))
    return factorial(p.integer) / hooks
