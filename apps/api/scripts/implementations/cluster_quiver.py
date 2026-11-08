import itertools
import math


def _decorated(window):
    n = len(window)
    perm = [(x - 1) % n + 1 for x in window]
    loops = {i for i in range(1, n + 1) if window[i - 1] == i}
    return perm, loops


def _boundary_labels(shape, n):
    labels_s, labels_w = {}, {}
    col, label = n - len(shape), 1
    for r, length in enumerate(shape):
        while col > length:
            labels_w[col - 1] = label
            label += 1
            col -= 1
        labels_s[r] = label
        label += 1
    while col > 0:
        labels_w[col - 1] = label
        label += 1
        col -= 1
    return labels_s, labels_w


def _column_length(shape, c):
    return sum(1 for length in shape if length > c)


def _window_of(shape, filling, n):
    labels_s, labels_w = _boundary_labels(shape, n)
    perm, loops = {}, set()

    def walk(r, c, direction):
        while r >= 0 and c >= 0:
            if filling[(r, c)] == 1:
                direction = "N" if direction == "W" else "W"
            if direction == "W":
                c -= 1
            else:
                r -= 1
        return labels_w[c] if r < 0 else labels_s[r]

    for r, label in labels_s.items():
        perm[label] = walk(r, shape[r] - 1, "W") if shape[r] > 0 else label
    for c, label in labels_w.items():
        length = _column_length(shape, c)
        perm[label] = walk(length - 1, c, "N") if length > 0 else label
        if perm[label] == label:
            loops.add(label)
    window = []
    for i in range(1, n + 1):
        image = perm[i]
        if image != i:
            window.append(image if image > i else image + n)
        else:
            window.append(i if i in loops else i + n)
    return tuple(window)


def _le_diagram(window):
    n = len(window)
    k = sum(1 for x in window if x > n)
    perm, loops = _decorated(window)
    target = {i: perm[i - 1] for i in range(1, n + 1)}
    for sources in itertools.combinations(range(1, n + 1), k):
        shape, seen_w = [], 0
        for label in range(1, n + 1):
            if label in sources:
                shape.append(n - k - seen_w)
            else:
                seen_w += 1
        shape = tuple(shape)
        labels_s, labels_w = _boundary_labels(shape, n)
        if set(labels_s.values()) != set(sources):
            continue
        if any(shape[r] == 0 and (target[a] != a or a in loops) for r, a in labels_s.items()):
            continue
        if any(
            _column_length(shape, c) == 0 and (target[a] != a or a not in loops)
            for c, a in labels_w.items()
        ):
            continue
        order = [(r, c) for r in range(len(shape) - 1, -1, -1) for c in range(shape[r] - 1, -1, -1)]
        filling, crossed = {}, set()
        east_in = {(r, shape[r] - 1): labels_s[r] for r in range(len(shape)) if shape[r] > 0}
        south_in = {
            (_column_length(shape, c) - 1, c): a
            for c, a in labels_w.items()
            if _column_length(shape, c) > 0
        }
        found = []

        def le_violation(r0, c0, shape=shape, filling=filling):
            return any(
                c0 < shape[r]
                and filling.get((r, c0)) == 0
                and any(filling.get((r, cc)) == 1 for cc in range(c0))
                for r in range(r0 + 1, len(shape))
            )

        def fill(
            i,
            shape=shape,
            order=order,
            filling=filling,
            crossed=crossed,
            found=found,
            east_in=east_in,
            south_in=south_in,
            labels_s=labels_s,
            labels_w=labels_w,
        ):
            if i == len(order):
                found.append(dict(filling))
                return
            r, c = order[i]
            a, b = east_in[(r, c)], south_in[(r, c)]
            for value in (1, 0):
                if value == 0 and (min(a, b), max(a, b)) in crossed:
                    continue
                north, west = (a, b) if value == 1 else (b, a)
                if r == 0 and target[north] != labels_w[c]:
                    continue
                if c == 0 and target[west] != labels_s[r]:
                    continue
                filling[(r, c)] = value
                if value == 1 and le_violation(r, c):
                    del filling[(r, c)]
                    continue
                if value == 0:
                    crossed.add((min(a, b), max(a, b)))
                if r > 0:
                    south_in[(r - 1, c)] = north
                if c > 0:
                    east_in[(r, c - 1)] = west
                fill(i + 1)
                if value == 0:
                    crossed.discard((min(a, b), max(a, b)))
                del filling[(r, c)]

        fill(0)
        for candidate in found:
            if _window_of(shape, candidate, n) == tuple(window):
                return shape, candidate
    raise ValueError("no Le-diagram")


def _le_graph(shape, filling, n):
    plus = {b for b, v in filling.items() if v == 1}
    pos, colour, adj, port = {}, {}, {}, {}

    def add(v, xy, col):
        pos[v], colour[v], adj[v] = xy, col, []

    def edge(u, v, kind):
        adj[u].append((v, kind))
        adj[v].append((u, kind))

    for r, c in sorted(plus):
        has_w = any((r, cc) in plus for cc in range(c))
        has_n = any((rr, c) in plus for rr in range(r))
        x, y = c + 0.5, -r - 0.5
        if has_w and has_n:
            add(("A", r, c), (x + 0.15, y + 0.15), "black")
            add(("B", r, c), (x - 0.15, y - 0.15), "white")
            edge(("A", r, c), ("B", r, c), "connector")
            port[(r, c)] = {"N": ("A", r, c), "E": ("A", r, c), "S": ("B", r, c), "W": ("B", r, c)}
        elif has_w:
            add(("B", r, c), (x, y), "white")
            port[(r, c)] = dict.fromkeys("WNES", ("B", r, c))
        else:
            add(("A", r, c), (x, y), "black")
            port[(r, c)] = dict.fromkeys("WNES", ("A", r, c))
    labels_s, labels_w = _boundary_labels(shape, n)
    for r, label in labels_s.items():
        add(("bd", label), (shape[r], -r - 0.5), "boundary")
    for c, label in labels_w.items():
        add(("bd", label), (c + 0.5, -_column_length(shape, c)), "boundary")
    for r in range(len(shape)):
        row = sorted(c for (rr, c) in plus if rr == r)
        for c1, c2 in itertools.pairwise(row):
            edge(port[(r, c1)]["E"], port[(r, c2)]["W"], "h")
        if row:
            edge(port[(r, row[-1])]["E"], ("bd", labels_s[r]), "h")
    for c in range(shape[0] if shape else 0):
        col = sorted(r for (r, cc) in plus if cc == c)
        for r1, r2 in itertools.pairwise(col):
            edge(port[(r1, c)]["S"], port[(r2, c)]["N"], "v")
        if col:
            edge(port[(col[-1], c)]["S"], ("bd", labels_w[c]), "v")
    return pos, colour, adj


def _faces(pos, adj, n):
    far = (-1000.0, 1000.0)

    def angle(v, point):
        return math.atan2(point[1] - pos[v][1], point[0] - pos[v][0])

    rot = {}
    for v, nbrs in adj.items():
        items = [(angle(v, pos[u]), u, kind) for u, kind in nbrs]
        if v[0] == "bd":
            i = v[1]
            for j in (i - 1, i + 1):
                if 1 <= j <= n:
                    items.append((angle(v, pos[("bd", j)]), ("bd", j), "arc"))
            if i in (1, n) and n > 1:
                items.append((angle(v, far), ("bd", n if i == 1 else 1), "arc"))
        items.sort()
        rot[v] = [(u, kind) for _, u, kind in items]
    darts = {(v, u, kind) for v, nbrs in rot.items() for u, kind in nbrs}
    seen, faces = set(), []
    for dart in sorted(darts, key=str):
        face = []
        d = dart
        while d not in seen:
            seen.add(d)
            face.append(d)
            v, u, kind = d
            ring = rot[u]
            i = next(i for i, (w, kk) in enumerate(ring) if w == v and kk == kind)
            w, kk = ring[(i - 1) % len(ring)]
            d = (u, w, kk)
        if face:
            faces.append(face)
    return faces


def _mutable_quiver(window):
    n = len(window)
    shape, filling = _le_diagram(window)
    pos, colour, adj = _le_graph(shape, filling, n)
    faces = _faces(pos, adj, n)
    keep = [i for i, face in enumerate(faces) if not all(kind == "arc" for _, _, kind in face)]
    face_of = {d: i for i in keep for d in faces[i]}
    frozen = {i for i in keep if any(kind == "arc" for _, _, kind in faces[i])}
    index = {face: j for j, face in enumerate(keep)}
    size = len(keep)
    b = [[0] * size for _ in range(size)]
    for v in adj:
        if colour[v] != "black" or len(adj[v]) < 3:
            continue
        for u, kind in adj[v]:
            prev, cur = v, u
            while cur[0] != "bd" and len(adj[cur]) == 2:
                prev, cur = cur, next(x for x, _ in adj[cur] if x != prev)
            if cur[0] == "bd" or colour[cur] != "white" or len(adj[cur]) < 3:
                continue
            left, right = face_of.get((v, u, kind)), face_of.get((u, v, kind))
            if left is None or right is None or left == right:
                continue
            b[index[left]][index[right]] += 1
            b[index[right]][index[left]] -= 1
    mutable = [index[i] for i in keep if i not in frozen]
    return [[b[i][j] for j in mutable] for i in mutable]


def _cycle_count(window):
    n = len(window)
    perm, _ = _decorated(window)
    seen, cycles = set(), 0
    for start in range(1, n + 1):
        if start not in seen:
            cycles += 1
            while start not in seen:
                seen.add(start)
                start = perm[start - 1]
    return cycles


def _affine_length(window):
    n = len(window)

    def f(j):
        return window[(j - 1) % n] + n * ((j - 1) // n)

    return sum(1 for i in range(1, n + 1) for j in range(i + 1, i + n + 1) if f(i) > f(j))


def accepts(p):
    if not isinstance(p, Positroid) or p.n < 3 or _cycle_count(p.window) != 1:
        return False
    k = sum(1 for x in p.window if x > p.n)
    return k * (p.n - k) - _affine_length(p.window) > p.n - 1


def compute(p):
    return Matrix(_mutable_quiver(p.window))
