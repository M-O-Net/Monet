def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    return sum(1 for k, part in enumerate(sorted(p.partition, reverse=True), start=1) if part >= k)
