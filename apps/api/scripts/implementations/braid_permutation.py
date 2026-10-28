def accepts(b):
    return isinstance(b, Braid)


def compute(b):
    position = list(range(b.strands))
    for letter in b.word:
        left = abs(letter) - 1
        for strand, at in enumerate(position):
            if at in (left, left + 1):
                position[strand] = 2 * left + 1 - at
    return Permutation(position)
