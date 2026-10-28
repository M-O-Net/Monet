def accepts(k):
    return isinstance(k, Knot) and k.name.split("_")[0].isdigit()


def compute(k):
    return Integer(int(k.name.split("_")[0]))
