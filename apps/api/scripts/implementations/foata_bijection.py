def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    word = []
    for letter in p.array_form:
        if word:
            cuts = [i for i, v in enumerate(word) if (v < letter) == (word[-1] < letter)]
            blocks = [
                word[start + 1 : end + 1] for start, end in zip([-1, *cuts], cuts, strict=False)
            ]
            word = [entry for block in blocks for entry in block[-1:] + block[:-1]]
        word.append(letter)
    return Permutation(word)
