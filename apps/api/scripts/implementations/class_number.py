def _discriminant(f):
    x = Symbol("x")
    poly = Poly(f.polynomial, x)
    if poly.degree() != 2 or not poly.is_monic:
        return None
    _, b, c = poly.all_coeffs()
    return int(b**2 - 4 * c)


def _below_root(value, discriminant):
    return value < 0 or value**2 < discriminant


def _imaginary(discriminant):
    count = 0
    a = 1
    while 3 * a * a <= -discriminant:
        for b in range(-a + 1, a + 1):
            numerator = b * b - discriminant
            if numerator % (4 * a):
                continue
            c = numerator // (4 * a)
            if c < a or (c == a and b < 0) or gcd(gcd(a, b), c) != 1:
                continue
            count += 1
        a += 1
    return count


def _reduced_forms(discriminant):
    forms = []
    b = discriminant % 2
    while b * b < discriminant:
        if b > 0:
            product = (b * b - discriminant) // 4
            for divisor in divisors(-product):
                for a in (divisor, -divisor):
                    lower = 2 * divisor + b
                    if lower**2 > discriminant and _below_root(2 * divisor - b, discriminant):
                        forms.append((a, b, product // a))
        b += 2
    return forms


def _next(form, discriminant):
    _, b, c = form
    step = 2 * abs(c)
    following = -b % step
    while not _below_root(following, discriminant):
        following -= step
    while _below_root(following + step, discriminant):
        following += step
    return c, following, (following**2 - discriminant) // (4 * c)


def _real(discriminant):
    remaining = set(_reduced_forms(discriminant))
    cycles = []
    while remaining:
        form = remaining.pop()
        cycle = {form}
        while (form := _next(form, discriminant)) not in cycle:
            cycle.add(form)
            remaining.discard(form)
        cycles.append(cycle)
    principal = next(cycle for cycle in cycles if any(a == 1 for a, _, _ in cycle))
    unit_of_norm_minus_one = any(a == -1 for a, _, _ in principal)
    return len(cycles) if unit_of_norm_minus_one else len(cycles) // 2


def accepts(f):
    return isinstance(f, NumberField) and _discriminant(f) is not None


def compute(f):
    discriminant = _discriminant(f)
    return _imaginary(discriminant) if discriminant < 0 else _real(discriminant)
