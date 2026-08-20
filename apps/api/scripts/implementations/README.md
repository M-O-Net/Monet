The seven implementations the demo dataset ships with, one per mathematical operator.

These are **seed data, not application code**: `../seed.py` reads each file's text and stores it
in the `implementations` table, from where it is served to the browser and executed there. They are
kept as real `.py` files rather than string literals so they can be read and diffed like code.

They deal in sympy, not strings — the sandbox parses each input object's LaTeX before calling
`accepts`/`compute` and renders whatever `compute` returns, so an implementation never mentions
LaTeX at all. Everything from `sympy` is in scope (which is why `ruff.toml` exempts this directory
from undefined-name checks). Nothing imports these files, and nothing on the server executes them.
