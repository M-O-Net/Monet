import json
import sys
import time

_BASE = namespace()  # noqa: F821 — prelude.py is exec'd into these globals first
_parse = _BASE["parse"]
_render = _BASE["render"]

_PYTHON_LINE_DEADLINE_SECONDS = 5.0
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


def _with_line_deadline(fn, *args):
    sys.settrace(_python_line_deadline_trace(_PYTHON_LINE_DEADLINE_SECONDS))
    try:
        return fn(*args)
    finally:
        sys.settrace(None)


def _as_latex(value):
    return value if isinstance(value, str) else _render(value)


def probe(latex, implementations_json):
    applicable = []
    for item in json.loads(implementations_json):
        try:
            if _with_line_deadline(_load(item["code"])["accepts"], _parse(latex)):
                applicable.append(item["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable})


def run(code, inputs_json):
    inputs = [_parse(latex) for latex in json.loads(inputs_json)]
    result = _with_line_deadline(_load(code)["compute"], *inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    outputs = [_as_latex(value) for value in values]
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})
