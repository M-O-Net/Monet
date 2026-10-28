def _repeated(parts):
    return next((part for part in parts if parts.count(part) > 1), None)


def accepts(p):
    return isinstance(p, IntegerPartition)


def compute(p):
    parts = list(p.partition)
    while (part := _repeated(parts)) is not None:
        parts.remove(part)
        parts.remove(part)
        parts.append(2 * part)
    return IntegerPartition(parts)
