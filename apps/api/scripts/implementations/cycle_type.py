def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    return IntegerPartition([length for length, count in p.cycle_structure.items() for _ in range(count)])
