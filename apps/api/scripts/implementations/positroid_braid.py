def _inverse(perm):
    inverse = [0] * len(perm)
    for i, image in enumerate(perm, 1):
        inverse[image - 1] = i
    return inverse


def _reduced_word(perm):
    perm, word = list(perm), []
    while True:
        for i in range(len(perm) - 1):
            if perm[i] > perm[i + 1]:
                perm[i], perm[i + 1] = perm[i + 1], perm[i]
                word.append(i + 1)
                break
        else:
            return word[::-1]


def accepts(p):
    return isinstance(p, Positroid) and p.n >= 2


def compute(p):
    n = p.n
    big = [j for j in range(1, n + 1) if p.window[j - 1] > n]
    small = [j for j in range(1, n + 1) if p.window[j - 1] <= n]
    w_inverse = big + small
    fbar = [(x - 1) % n + 1 for x in p.window]
    v = _inverse([fbar[j - 1] for j in w_inverse])
    w = _inverse(w_inverse)
    return Braid(n, _reduced_word(w) + [-s for s in reversed(_reduced_word(v))])
