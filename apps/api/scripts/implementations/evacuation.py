def accepts(t):
    return isinstance(t, Tableau)


def _slide_out(rows):
    i, j = 0, 0
    while True:
        below = rows[i + 1][j] if i + 1 < len(rows) and j < len(rows[i + 1]) else None
        right = rows[i][j + 1] if j + 1 < len(rows[i]) else None
        if below is None and right is None:
            del rows[i][j]
            if not rows[i]:
                del rows[i]
            return i, j
        if right is None or (below is not None and below < right):
            rows[i][j], i = below, i + 1
        else:
            rows[i][j], j = right, j + 1


def compute(t):
    rows = [list(row) for row in t.rows]
    evacuated = [[0] * len(row) for row in rows]
    for label in range(sum(map(len, rows)), 0, -1):
        i, j = _slide_out(rows)
        evacuated[i][j] = label
    return Tableau(evacuated)
