def _decorated(p):
    n = p.n
    perm = [(x - 1) % n + 1 for x in p.window]
    loops = {i for i in range(1, n + 1) if p.window[i - 1] == i}
    return perm, loops


def _positroid(perm, loops):
    n = len(perm)
    window = []
    for i, image in enumerate(perm, 1):
        if image > i:
            window.append(image)
        elif image < i:
            window.append(image + n)
        else:
            window.append(i if i in loops else i + n)
    return Positroid(window)


def _inverse(perm):
    inverse = [0] * len(perm)
    for i, image in enumerate(perm, 1):
        inverse[image - 1] = i
    return inverse


def accepts(p):
    return isinstance(p, Positroid) and p.n >= 1


def compute(p):
    perm, loops = _decorated(p)
    n = p.n
    images = [perm[(j - 2) % n] % n + 1 for j in range(1, n + 1)]
    return _positroid(images, {i % n + 1 for i in loops})
