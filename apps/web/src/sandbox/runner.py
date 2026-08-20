"""The two entry points the sandbox frame calls, layered on top of prelude.py.

Implementations deal in sympy, not strings: this module parses each input LaTeX into a sympy object
before calling `accepts`/`compute`, and renders whatever comes back. `parse` and `render` stay
available in the namespace for an implementation that genuinely needs them, but no ordinary one should
have to mention either.

Arguments and results cross as JSON strings rather than as JS objects: a JsProxy would need
explicit lifetime management on every call, and implementation output is small enough that the round
trip through json costs nothing.
"""

import json
import sys
import time

_BASE = namespace()  # noqa: F821 — prelude.py is exec'd into these globals first
_parse = _BASE["parse"]
_render = _BASE["render"]

_TIME_LIMIT_SECONDS = 5.0
_CHECK_EVERY = 2000


def _deadline_trace(seconds):
    deadline = time.monotonic() + seconds
    counter = [0]

    def trace(frame, event, arg):
        counter[0] += 1
        if counter[0] % _CHECK_EVERY == 0 and time.monotonic() > deadline:
            raise TimeoutError(f"implementation ran longer than {seconds:g}s and was stopped")
        return trace

    return trace


def _load(code):
    """Exec one implementation against a fresh copy of the prelude namespace."""
    scope = dict(_BASE)
    exec(compile(code, "<implementation>", "exec"), scope)  # noqa: S102
    return scope


def _guarded(fn, *args):
    sys.settrace(_deadline_trace(_TIME_LIMIT_SECONDS))
    try:
        return fn(*args)
    finally:
        sys.settrace(None)


def _as_latex(value):
    """An implementation normally returns sympy; a string is taken as LaTeX that's already final."""
    return value if isinstance(value, str) else _render(value)


def probe(latex, implementations_json):
    """Return the ids of the implementations that accept this object.

    Parsed per implementation rather than once: sympy's Matrix is mutable, and handing the same
    instance to several strangers' `accepts` in turn would let the first one change what the
    rest see.

    An implementation that raises while reading the object simply doesn't apply to it — that's the
    normal way `accepts` says no about an object it can't make sense of, including one it can't
    parse at all, not an error worth surfacing.
    """
    applicable = []
    for item in json.loads(implementations_json):
        try:
            if _guarded(_load(item["code"])["accepts"], _parse(latex)):
                applicable.append(item["id"])
        except Exception:  # noqa: BLE001, S110
            pass
    return json.dumps({"applicable": applicable})


def run(code, inputs_json):
    """Run one implementation over its inputs and return its outputs as LaTeX."""
    inputs = [_parse(latex) for latex in json.loads(inputs_json)]
    result = _guarded(_load(code)["compute"], *inputs)
    values = list(result) if isinstance(result, (list, tuple)) else [result]
    outputs = [_as_latex(value) for value in values]
    if not outputs:
        raise ValueError("compute() returned no outputs")
    return json.dumps({"outputs": outputs})
