def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and all(entry.is_number for entry in m)
        and len(m.nullspace(simplify=True)) > 0
    )


def compute(m):
    return m.nullspace(simplify=True)
