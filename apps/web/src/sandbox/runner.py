import json
import sys
import time

_BASE = namespace()  # noqa: F821 — prelude.py is exec'd into these globals first
_parse = _BASE["parse"]
_render = _BASE["render"]

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


def _accepts(code, latex):
    return _load(code)["accepts"](_parse(latex))


def _compute(code, inputs_json):
    inputs = [_parse(latex) for latex in json.loads(inputs_json)]
    result = _load(code)["compute"](*inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    return [_as_latex(value) for value in values]


def probe(latex, implementations_json):
    applicable = []
    deadline = time.monotonic() + _PYTHON_PROBE_DEADLINE_SECONDS
    for item in json.loads(implementations_json):
        remaining = min(deadline - time.monotonic(), _PYTHON_LINE_DEADLINE_SECONDS)
        if remaining <= 0:
            break
        try:
            if _with_line_deadline(remaining, _accepts, item["code"], latex):
                applicable.append(item["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable})


def run(code, inputs_json):
    outputs = _with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _compute, code, inputs_json)
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})
