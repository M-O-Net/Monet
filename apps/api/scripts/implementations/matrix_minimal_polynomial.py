def accepts(m):
    return isinstance(m, MatrixBase) and m.is_square and all(entry.is_Rational for entry in m)


def compute(m):
    x, size = Symbol("x"), m.rows
    powers = [eye(size)]
    for degree in range(1, size + 1):
        powers.append(powers[-1] * m)
        flattened = Matrix.hstack(*(power.reshape(size * size, 1) for power in powers))
        relations = flattened.nullspace()
        if relations:
            relation = relations[0] / relations[0][degree]
            return sum(relation[i] * x**i for i in range(degree + 1))
    raise ValueError("no polynomial of degree at most the size annihilates the matrix")
