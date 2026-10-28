import math


def _parts(z):
    re, im = expand_complex(z).as_real_imag()
    if not (re.is_Integer and im.is_Integer):
        return None
    return int(re), int(im)


def accepts(z):
    if not (isinstance(z, Expr) and z.is_number and bool(z.is_algebraic)):
        return False
    parts = _parts(z)
    return parts is not None and parts[1] != 0 and parts[0] ** 2 + parts[1] ** 2 > 1


def _divide(z, w):
    norm = w[0] ** 2 + w[1] ** 2
    re, im = z[0] * w[0] + z[1] * w[1], z[1] * w[0] - z[0] * w[1]
    if re % norm or im % norm:
        return None
    return re // norm, im // norm


def _two_squares(p):
    for s in range(1, math.isqrt(p) + 1):
        t = math.isqrt(p - s * s)
        if t * t == p - s * s:
            return s, t
    raise ValueError(f"{p} is not a sum of two squares")


def _first_quadrant_primes_over(p):
    if p == 2:
        return [(1, 1)]
    if p % 4 == 3:
        return [(p, 0)]
    s, t = _two_squares(p)
    return [(s, t), (t, s)]


def compute(z):
    z = _parts(z)
    factors = []
    for p in factorint(z[0] ** 2 + z[1] ** 2):
        for w in _first_quadrant_primes_over(p):
            while (quotient := _divide(z, w)) is not None:
                z = quotient
                factors.append(w)
    factors.sort(key=lambda w: (w[0] ** 2 + w[1] ** 2, math.atan2(w[1], w[0])))
    return [Integer(re) + Integer(im) * I for re, im in factors]
