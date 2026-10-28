def accepts(angle):
    return (
        isinstance(angle, Expr)
        and angle.is_number
        and bool(angle.is_real)
        and "expr" in to_data(angle)
    )


def compute(angle):
    return Matrix([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
