def accepts(t):
    return isinstance(t, Tableau)


def compute(t):
    return Tableau([[row[j] for row in t.rows if j < len(row)] for j in range(len(t.rows[0]))])
