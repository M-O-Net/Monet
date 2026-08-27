import json
import sys
import time

_BASE = namespace()  # noqa: F821 — prelude.py is exec'd into these globals first
_parse = _BASE["parse"]
_render = _BASE["render"]
_MatrixBase = _BASE["MatrixBase"]

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


def _as_latex(value):
    return value if isinstance(value, str) else _render(value)


def _unshared(value):
    return value.copy() if isinstance(value, _MatrixBase) else value


def _accepts(code, value):
    return _load(code)["accepts"](_unshared(value))


def _compute(code, inputs_json):
    inputs = [_parse(latex) for latex in json.loads(inputs_json)]
    result = _load(code)["compute"](*inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    return [_as_latex(value) for value in values]


def probe(latex, implementations_json):
    items = json.loads(implementations_json)
    deadline = time.monotonic() + _PYTHON_PROBE_DEADLINE_SECONDS
    budget = min(deadline - time.monotonic(), _PYTHON_LINE_DEADLINE_SECONDS)
    try:
        value = _with_line_deadline(budget, _parse, latex)
    except Exception:  # noqa: BLE001
        return json.dumps({"applicable": [], "skipped": 0})

    applicable = []
    for position, item in enumerate(items):
        remaining = min(deadline - time.monotonic(), _PYTHON_LINE_DEADLINE_SECONDS)
        if remaining <= 0:
            return json.dumps({"applicable": applicable, "skipped": len(items) - position})
        try:
            if _with_line_deadline(remaining, _accepts, item["code"], value):
                applicable.append(item["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable, "skipped": 0})


def run(code, inputs_json):
    outputs = _with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _compute, code, inputs_json)
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})
