def accepts(s):
    return isinstance(s, Surface)


def compute(s):
    if s.orientable:
        names = [f"{letter}_{i}" for i in range(1, s.genus + 1) for letter in "ab"]
    else:
        names = [f"a_{i}" for i in range(1, s.genus + 1)]
    free, *generators = free_group(", ".join(names))
    if s.orientable:
        pairs = zip(generators[::2], generators[1::2], strict=True)
        relators = [prod((a * b * a**-1 * b**-1 for a, b in pairs), start=free.identity)]
    else:
        relators = [prod((a**2 for a in generators), start=free.identity)]
    return FpGroup(free, [r for r in relators if r != free.identity])
