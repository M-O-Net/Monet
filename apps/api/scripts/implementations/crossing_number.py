import re

ROLFSEN_NAME = re.compile(r"(\d+)[an]?_\d+")


def accepts(k):
    return isinstance(k, Knot) and ROLFSEN_NAME.fullmatch(k.name) is not None


def compute(k):
    return Integer(int(ROLFSEN_NAME.fullmatch(k.name)[1]))
