import json
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


def _accepts(code, item):
    return _load(code)["accepts"](_value(item))


def _compute(code, inputs_json):
    inputs = [_value(item) for item in json.loads(inputs_json)]
    result = _load(code)["compute"](*inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    return [_described(value) for value in values]


def probe(item_json, implementations_json):
    item = json.loads(item_json)
    applicable = []
    deadline = time.monotonic() + _PYTHON_PROBE_DEADLINE_SECONDS
    for implementation in json.loads(implementations_json):
        remaining = min(deadline - time.monotonic(), _PYTHON_LINE_DEADLINE_SECONDS)
        if remaining <= 0:
            break
        try:
            if _with_line_deadline(remaining, _accepts, implementation["code"], item):
                applicable.append(implementation["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable})


def run(code, inputs_json):
    outputs = _with_line_deadline(_PYTHON_LINE_DEADLINE_SECONDS, _compute, code, inputs_json)
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})
