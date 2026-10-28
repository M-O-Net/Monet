import json
import math
import sys
import time

_BASE = namespace()  # noqa: F821 — prelude.py is exec'd into these globals first
_parse = _BASE["parse"]
_render = _BASE["render"]
_to_data = _BASE["to_data"]
_from_data = _BASE["from_data"]

_PYTHON_LINE_DEADLINE_SECONDS = 5.0
_PYTHON_PROBE_DEADLINE_SECONDS = 6.0
_CHECK_CLOCK_EVERY_N_LINES = 2000


def _python_line_deadline_trace(seconds):
    deadline = time.monotonic() + seconds
    counter = [0]

    def trace(frame, event, arg):
        counter[0] += 1
        if counter[0] % _CHECK_CLOCK_EVERY_N_LINES == 0 and time.monotonic() > deadline:
            raise TimeoutError(f"implementation ran longer than {seconds:g}s and was stopped")
        return trace

    return trace


def _load(code):
    scope = dict(_BASE)
    exec(compile(code, "<implementation>", "exec"), scope)  # noqa: S102
    return scope


def _with_line_deadline(seconds, fn, *args):
    sys.settrace(_python_line_deadline_trace(seconds))
    try:
        return fn(*args)
    finally:
        sys.settrace(None)


def _value(item):
    if item.get("data") is not None:
        try:
            return _from_data(item["data"])
        except LookupError:
            pass
    return _parse(item["latex"])


def _described(value):
    if isinstance(value, str):
        return {"latex": value, "data": None}
    return {"latex": _render(value), "data": _to_data(value)}


def _accepts(code, value):
    return _load(code)["accepts"](value.copy() if isinstance(value, _BASE["MatrixBase"]) else value)


def _compute(code, inputs_json):
    inputs = [_value(item) for item in json.loads(inputs_json)]
    result = _load(code)["compute"](*inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    return [_described(value) for value in values]


def probe(item_json, implementations_json):
    item = json.loads(item_json)
    applicable = []
    deadline = time.monotonic() + _PYTHON_PROBE_DEADLINE_SECONDS
    try:
        value = _with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _value, item)
    except Exception:
        return json.dumps({"applicable": applicable})
    for implementation in json.loads(implementations_json):
        remaining = min(deadline - time.monotonic(), _PYTHON_LINE_DEADLINE_SECONDS)
        if remaining <= 0:
            break
        try:
            if _with_line_deadline(remaining, _accepts, implementation["code"], value):
                applicable.append(implementation["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable})


def run(code, inputs_json):
    outputs = _with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _compute, code, inputs_json)
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})


def _describe(latex):
    return _described(_parse(latex))


def describe(latex):
    return json.dumps(_with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _describe, latex))


_sympy = _BASE["sympy"]

_PLOT_SAMPLES = 400
_SCAN_HALF_WIDTH = 10.0
_SCAN_SAMPLES = 2001
_DEFAULT_HALF_WIDTH = 5.0
_MIN_FEATURE_SPAN = 2.0
_MIN_PADDING = 1.2
_PADDING_PER_SPAN = 0.25
_BISECTION_STEPS = 60
_SHORT_LATEX_CHARACTERS = 80
_IMAGINARY_TOLERANCE = 1e-9


def _real(value):
    try:
        z = complex(value)
    except (TypeError, ValueError):
        return None
    if abs(z.imag) > _IMAGINARY_TOLERANCE * max(1.0, abs(z.real)):
        return None
    return z.real if math.isfinite(z.real) else None


def _evaluator(expression, var):
    compiled = _sympy.lambdify(var, expression, modules=["math", "mpmath"])

    def at(x):
        try:
            return _real(compiled(x))
        except (ArithmeticError, ValueError, TypeError):
            return None

    return at


def _short_latex(value):
    latex = _render(value)
    return latex if len(latex) <= _SHORT_LATEX_CHARACTERS else None


def _polynomial_roots(poly):
    found = []
    for factor, multiplicity in poly.sqf_list()[1]:
        exact = _sympy.roots(factor, quartics=False)
        if sum(exact.values()) == factor.degree():
            found.extend((root, _short_latex(root), count * multiplicity) for root, count in exact.items())
        else:
            found.extend((root, None, multiplicity) for root in factor.nroots(n=15, maxsteps=200))
    return found


def _real_zeros(poly):
    if poly.degree() < 1:
        return []
    roots = poly.sqf_part().nroots(n=15, maxsteps=200)
    return [x for x in (_real(root) for root in roots) if x is not None]


def _bisect(at, a, b, ya):
    for _ in range(_BISECTION_STEPS):
        mid = (a + b) / 2
        ym = at(mid)
        if ym is None:
            return None
        if ym == 0:
            return mid
        if (ym < 0) == (ya < 0):
            a, ya = mid, ym
        else:
            b = mid
    return (a + b) / 2


def _scanned_features(at):
    step = 2 * _SCAN_HALF_WIDTH / (_SCAN_SAMPLES - 1)
    xs = [-_SCAN_HALF_WIDTH + i * step for i in range(_SCAN_SAMPLES)]
    ys = [at(x) for x in xs]
    roots = []
    for i in range(_SCAN_SAMPLES - 1):
        ya, yb = ys[i], ys[i + 1]
        if ya is None or yb is None:
            continue
        if ya == 0:
            roots.append(xs[i])
        elif yb != 0 and (ya < 0) != (yb < 0):
            root = _bisect(at, xs[i], xs[i + 1], ya)
            y_root = None if root is None else at(root)
            if y_root is not None and abs(y_root) <= min(abs(ya), abs(yb)):
                roots.append(root)
    turns = []
    for i in range(1, _SCAN_SAMPLES - 1):
        before, here, after = ys[i - 1], ys[i], ys[i + 1]
        if before is None or here is None or after is None:
            continue
        if (here - before) * (after - here) < 0:
            turns.append(xs[i])
    return roots, turns


def _window(features, limit):
    if not features:
        return -_DEFAULT_HALF_WIDTH, _DEFAULT_HALF_WIDTH
    lo, hi = min(features), max(features)
    span = max(hi - lo, _MIN_FEATURE_SPAN)
    centre = (lo + hi) / 2
    half = span / 2 + max(_MIN_PADDING, _PADDING_PER_SPAN * span)
    return max(centre - half, -limit), min(centre + half, limit)


def _samples(at, window, extra):
    lo, hi = window
    step = (hi - lo) / (_PLOT_SAMPLES - 1)
    xs = sorted({lo + i * step for i in range(_PLOT_SAMPLES)} | {x for x in extra if lo <= x <= hi})
    return [[x, at(x)] for x in xs]


def _polynomial_features(poly, var):
    real_roots, complex_roots = [], []
    for root, latex, multiplicity in _polynomial_roots(poly):
        z = complex(_sympy.N(root, 15))
        x = _real(z)
        if x is None:
            complex_roots.append({"re": z.real, "im": z.imag, "latex": latex, "multiplicity": multiplicity})
        else:
            real_roots.append({"x": x, "latex": latex, "multiplicity": multiplicity})
    derivative = poly.diff(var)
    turns = _real_zeros(derivative) + _real_zeros(derivative.diff(var))
    return real_roots, complex_roots, turns


def _root_x(root):
    return root["x"]


def _analyze(item_json):
    value = _value(json.loads(item_json))
    if not isinstance(value, _sympy.Expr) or len(value.free_symbols) != 1:
        return None
    (var,) = value.free_symbols
    at = _evaluator(value, var)

    if value.is_polynomial(var) and _sympy.degree(value, var) >= 1:
        real_roots, complex_roots, turns = _polynomial_features(_sympy.Poly(value, var), var)
        limit = math.inf
    else:
        roots, turns = _scanned_features(at)
        real_roots = [{"x": x, "latex": None, "multiplicity": 1} for x in roots]
        complex_roots = None
        limit = _SCAN_HALF_WIDTH

    real_roots.sort(key=_root_x)
    root_xs = [root["x"] for root in real_roots]
    window = _window(root_xs + turns, limit)
    return {
        "variable": str(var),
        "window": list(window),
        "points": _samples(at, window, root_xs),
        "real_roots": real_roots,
        "complex_roots": complex_roots,
    }


def analyze(item_json):
    return json.dumps(_with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _analyze, item_json))
