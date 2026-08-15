#!/usr/bin/env python3
"""PreToolUse hook: keeps every PR born as a draft, and the only path off `main` running through
`just land`. Denies three Bash invocations, each with a message naming the replacement it owes:

  `gh pr create` without `--draft`/`-d`  ->  `just pr`    (always opens a draft)
  `gh pr ready` (not `--undo`)           ->  `just land`  (full suite, ready, wait, merge)
  `gh pr merge`                          ->  `just land`  (same -- merging is not a separate step)

This is the local half of the design in root AGENTS.md's Merge gate section: every PR is born
a draft, so pushes to it cost nothing in CI (ci.yml's `changes` job is gated on
`github.event.pull_request.draft == false`) and, below `main`, get almost nothing from
`.githooks/pre-push` either -- each commit was already checked by `.githooks/pre-commit`. `just
land` is the only path a PR is allowed to reach `main` through: the full local suite, then ready,
then CI, then merge (or revert to draft on a red CI run). Denying the raw commands is what keeps
an agent from reaching for them out of habit and skipping that sequence rather than deciding to;
`.githooks/pre-push` is the other half -- it denies a PUSH to an already-ready PR, which is what
would let a fix reach `main` without any of this having run again.

`gh pr ready --undo` (converts a PR back to draft) is deliberately NOT denied -- it moves the
same direction `just pr` already does, so there is nothing here for it to bypass.

KNOWN HOLE, accepted rather than closed: clicking "Ready for review" or "Merge" in the GitHub web
UI bypasses this -- and every local hook -- entirely, and so does `gh api` called directly (e.g.
`gh api -X PUT repos/{owner}/{repo}/pulls/{n}/merge`) -- same bypass, through a command this file
does match on `gh` but has no reason to parse the way it parses `gh pr ready`/`gh pr merge`. This
file is a habit guard, not a security boundary, so widening the matcher to cover `gh api` isn't
warranted -- `.github/workflows/ci.yml` is the actual backstop for all of these.

Matches `gh` invocations the same way block-main-branch.py matches git/shell ones: tokenize the
raw command with shlex (so quoting and multi-character operators like `&&` survive intact), split
on connectors so a mutator anywhere in a compound command is caught rather than only its first
clause, and classify each segment's own tokens -- never a regex over the raw string, which a
differently-spaced flag or a quoted argument would slip past. No cwd tracking is needed here,
unlike block-main-branch.py: which PR a `gh pr` command targets depends on the branch and its
remote, not on any `cd` the command makes, so there is nothing this hook would resolve
differently per segment.

Adding a new command to deny is a one-line addition to `denial_for` below, matching the sibling
hook's own "one-line addition" convention.
"""

import json
import shlex
import sys

REQUIRE_DRAFT_REASON = (
    "Every PR must be opened as a draft, never ready -- use `just pr` instead of `gh pr create`. "
    "A draft push costs nothing in CI (ci.yml skips the whole job graph on a draft PR); "
    "`just land` runs the full suite, then readies, then merges. See root AGENTS.md > Merge gate."
)

REQUIRE_LAND_REASON = (
    "Use `just land` instead of `{cmd}` -- it runs the full local suite, flips the PR ready, "
    "waits for CI, and merges on green (or reverts to draft on red). {cmd} on its own skips some "
    "of that sequence. See root AGENTS.md > Merge gate."
)


def tokenize(cmd: str) -> list[str]:
    """shlex with punctuation_chars=True keeps multi-character operators (&&, ||, >>) intact
    while still respecting quoting -- the same approach block-main-branch.py's tokenize uses.
    Malformed input (unbalanced quotes) fails open: no tokens, nothing gets matched, the same
    "just don't match" fallback every unrecognized case here already has."""
    try:
        lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return []


CONNECTORS = {"|", "||", "&", "&&", ";"}


def is_operator_token(tok: str) -> bool:
    return bool(tok) and all(c in "();<>|&" for c in tok)


def segments(tokens: list[str]) -> list[list[str]]:
    """Split a flat token stream at every connector and operator, so `... && gh pr ready` or
    `... ; gh pr create` are still caught, not only a command that's the whole string."""
    out: list[list[str]] = []
    current: list[str] = []
    for tok in tokens:
        if tok in CONNECTORS or is_operator_token(tok):
            if current:
                out.append(current)
            current = []
            continue
        current.append(tok)
    if current:
        out.append(current)
    return out


def denial_for(segment: list[str]) -> str | None:
    """The denial reason for this segment, or None if it is not a tracked `gh pr` invocation."""
    if segment[:2] != ["gh", "pr"] or len(segment) < 3:
        return None
    sub = segment[2]
    rest = segment[3:]
    if sub == "ready":
        return None if "--undo" in rest else REQUIRE_LAND_REASON.format(cmd="gh pr ready")
    if sub == "merge":
        return REQUIRE_LAND_REASON.format(cmd="gh pr merge")
    if sub == "create":
        has_draft = any(t in ("--draft", "-d") for t in rest)
        return None if has_draft else REQUIRE_DRAFT_REASON
    return None


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def allow() -> None:
    print("{}")


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        allow()
        return
    cmd = data["tool_input"]["command"]
    for segment in segments(tokenize(cmd)):
        reason = denial_for(segment)
        if reason is not None:
            deny(reason)
            return
    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail open on anything unexpected (malformed stdin, missing fields, ...), the same
        # fallback block-main-branch.py uses.
        allow()
