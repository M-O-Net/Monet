def _generator(strands, letter):
    t = Symbol("t")
    size = strands - 1
    i = abs(letter) - 1
    m = eye(size)
    m[i, i] = -t
    if i > 0:
        m[i, i - 1] = t
    if i < size - 1:
        m[i, i + 1] = 1
    return m if letter > 0 else m.inv()


def accepts(b):
    return isinstance(b, Braid) and b.strands > 1


def compute(b):
    product = eye(b.strands - 1)
    for letter in b.word:
        product = product * _generator(b.strands, letter)
    return product.applyfunc(expand)
