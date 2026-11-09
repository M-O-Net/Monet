def _arrows(m):
    size = m.rows
    return [[int(m[i, j]) if m[i, j] > 0 else 0 for j in range(size)] for i in range(size)]


def _topological_order(arrows):
    size = len(arrows)
    indegree = [sum(1 for i in range(size) if arrows[i][j]) for j in range(size)]
    ready = [j for j in range(size) if indegree[j] == 0]
    order = []
    while ready:
        v = ready.pop(0)
        order.append(v)
        for j in range(size):
            if arrows[v][j]:
                indegree[j] -= 1
                if indegree[j] == 0:
                    ready.append(j)
    return order if len(order) == size else None


def accepts(m):
    return (
        isinstance(m, MatrixBase)
        and m.is_square
        and m.rows > 0
        and all(x.is_integer for x in m)
        and m == -m.T
        and _topological_order(_arrows(m)) is not None
    )


def compute(m):
    arrows = _arrows(m)
    order = _topological_order(arrows)
    size = len(order)
    euler = Matrix(
        size,
        size,
        lambda a, b: (1 if a == b else 0) - arrows[order[a]][order[b]],
    )
    return (-euler.inv() * euler.T).charpoly(Symbol("x")).as_expr()
