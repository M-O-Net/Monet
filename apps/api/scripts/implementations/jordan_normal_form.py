def _position(z):
    point = complex(N(z, 30))
    return round(point.real, 12), round(point.imag, 12)


def _blocks(jordan):
    blocks, start = [], 0
    while start < jordan.rows:
        size = 1
        while start + size < jordan.rows and jordan[start + size - 1, start + size] == 1:
            size += 1
        blocks.append((jordan[start, start], size))
        start += size
    return blocks


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and all(entry.is_number and bool(entry.is_algebraic) for entry in m)
    )


def compute(m):
    _, jordan = m.jordan_form()
    blocks = sorted(_blocks(jordan), key=lambda block: (*_position(block[0]), -block[1]))
    normal, start = zeros(m.rows), 0
    for value, size in blocks:
        for k in range(size):
            normal[start + k, start + k] = value
            if k + 1 < size:
                normal[start + k, start + k + 1] = 1
        start += size
    return normal
