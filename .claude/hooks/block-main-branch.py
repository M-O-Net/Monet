#!/usr/bin/env python3
"""PreToolUse hook: blocks edits, commits, branch switches, and raw shell file-mutators in the
main checkout. Forces all feature work into an isolated worktree, per root AGENTS.md's Merge gate
section.

Resolves git-dir/git-common-dir from the ACTUAL TARGET of the tool call -- the file being
written, or the repo a Bash `git commit` would run against. An ABSOLUTE target names one checkout
no matter where anything runs, and is never reinterpreted against a cwd: a session whose shell cwd
is a worktree can still pass an absolute path into the main checkout (by mistake or otherwise),
and cwd-based detection alone silently allows that, since a linked worktree's own git-dir always
differs from its git-common-dir regardless of what path the tool call actually targets.

A RELATIVE target is resolved against the cwd the command would really run in. That starts as this
process's own cwd, which is the session's: Claude Code spawns the hook there, and the Bash tool
resets its shell there between calls, so it is also where each Bash command begins. From there it
follows any `cd` earlier in the same compound command that the shell itself would honour -- see
segments_with_cwd -- so `cd <worktree> && mkdir .brief` resolves inside the worktree and is
allowed, while a bare `mkdir .brief` still resolves, and denies, in whichever checkout the session
is actually sitting in.

The payload's `cwd` field is deliberately not read. It is the session cwd -- the very directory
this process is spawned in -- so it carries nothing os.getcwd() does not, and it is not the Bash
command's own working directory: the Bash tool input has no such field, and there is no way to
learn a command's cwd other than by reading the command.

What stays unresolvable is shell state this hook does not parse: a `cd` through a variable, a
`pushd`, a directory change inside a function. Those leave the resolution point where it was, so a
deny on a relative target means "resolved from here, it lands in the main checkout" -- not "this is
a main-checkout write". Both still deny; reason_for() below keeps the two apart in what the denial
SAYS, since a guard that names a cause it cannot confirm sends the reader to fix something that
isn't broken.

Adding a new command to block is a one-line addition to GIT_MUTATING_VERBS (for a `git <verb>`)
or SHELL_MUTATORS (for a raw shell command) below -- not a new regex/case branch.
"""

import json
import os
import shlex
import subprocess
import sys

REASON = (
    "Feature work must happen in an isolated worktree, not the main checkout. Never develop "
    "directly on main. Follow root AGENTS.md > Merge gate exactly for how to create and set one up "
    "-- do not skip any of its steps."
)


def reason_for(target: str, cwd: str) -> str:
    """The denial message for a target this hook has already decided to block, and the cwd it was
    resolved against.

    An absolute target names one checkout no matter where this hook runs, so blocking it really
    does mean the tool call was aimed at the main checkout -- REASON is accurate. A relative one
    was resolved against `cwd`, which is the best available account of where the command would
    run but not a guarantee, so all that has been established is that it lands in the main
    checkout FROM THERE. Say that, name the target and that cwd, and give the escape hatch (an
    absolute path), rather than asserting a main-checkout write that hasn't been shown."""
    if os.path.isabs(target):
        return REASON
    return (
        f"Could not resolve {target!r} to a specific checkout: it is a relative path, so this "
        f"hook resolved it against the cwd the command would run in ({cwd}), where it lands in "
        "the main checkout. A relative path in the main checkout and the same one inside a "
        "worktree are indistinguishable here, so this is a refusal by default -- NOT a confirmed "
        "main-checkout write, and not evidence that you lack a worktree. If you are working in "
        "one, `cd` into it first in the same command, or re-run with an absolute path under it. "
        "If you really are in the main checkout: " + REASON
    )


# git subcommands that mutate the index/working tree of whichever checkout they target.
GIT_MUTATING_VERBS = {
    "commit", "checkout", "switch", "mv", "rm", "restore", "reset", "apply",
    "stash", "clean", "revert", "cherry-pick", "rebase", "merge",
}

# git's pre-command (global) options whose operand is a SEPARATE token. check_git_segment must
# skip both, because the token after one of these is git's operand and never the subcommand --
# left unskipped it reads as an unrecognized verb and ends the scan before the real verb is seen,
# which is a total bypass of this hook (`git -c user.email=x -C <main> commit`).
#
# Membership is decided by what git ACTUALLY does with the token after the flag, not by what its
# synopsis suggests: `--attr-source` and `--shallow-file` take separated operands and appear in no
# synopsis line, while `--exec-path` reads like one and is not -- bare, it prints the exec path and
# exits. Adding a flag that does not really consume an operand would make this hook skip a real
# verb, so a wrong entry here OPENS a hole rather than closing one; verify against git before
# adding. The attached forms (`--git-dir=<p>`, `-c` is separated-only) already parse as flags.
GIT_FLAGS_TAKING_SEPARATE_OPERAND = {
    "-c", "-C", "--attr-source", "--config-env",
    "--git-dir", "--namespace", "--shallow-file", "--work-tree",
}

# The subset of those whose operand names the checkout the command targets. `--work-tree` is
# deliberately NOT here: it renames the work tree without naming the repo, so honoring it alone
# would let `git --work-tree <elsewhere> commit`, run against the main checkout, retarget this
# hook's verdict away from main -- widening what is allowed, which this guard must never do.
GIT_FLAGS_NAMING_THE_TARGET = {"-C", "--git-dir"}


def all_args(args: list[str]) -> list[str]:
    """Every non-flag argument is a mutation target: `mv a b` mutates `a` too, by deleting it
    from there -- not just `b`; `mkdir a b` creates both."""
    return [a for a in args if not a.startswith("-")]


def last_arg(args: list[str]) -> list[str]:
    """These create/copy INTO a destination -- only the last non-flag argument is written;
    earlier argument(s) are read-only references (a `cp mainfile worktree/mainfile` reading FROM
    main to seed a worktree, or `ln -s mainfile worktree/link` linking TO a main file, is
    legitimate and must stay allowed)."""
    non_flags = all_args(args)
    return non_flags[-1:]


def sed_targets(args: list[str]) -> list[str]:
    """sed only mutates in place with -i/--in-place; without it, sed is a read-only filter to
    stdout and must not be flagged at all."""
    has_i = any(a in ("-i", "--in-place") or a.startswith(("-i.", "--in-place=")) for a in args)
    return all_args(args) if has_i else []


def dd_targets(args: list[str]) -> list[str]:
    """Only `of=` is a write target; `if=` is a read-only source and must not be flagged."""
    return [a[len("of="):] for a in args if a.startswith("of=")]


def first_arg(args: list[str]) -> list[str]:
    """patch mutates whichever file it's applying to. Unlike cp, when a target *and* a patch
    file are both given positionally (`patch origfile patchfile`) the mutated one is FIRST, not
    last -- the opposite of cp/install's convention."""
    non_flags = all_args(args)
    return non_flags[:1]


# Which argument(s) count as a mutation target differs per verb -- see each classifier's
# docstring above. A patch file passed via `-i <patchfile>` rather than positionally can still be
# misidentified as a target by first_arg/all_args since it's a non-flag token indistinguishable
# from a real target without full flag-arity parsing; that's a false positive (over-blocks, not
# under-blocks) and is accepted on purpose -- erring toward blocking beats missing a mutation.
SHELL_MUTATORS = {
    "mv": all_args, "rm": all_args, "truncate": all_args, "tee": all_args,
    "mkdir": all_args, "rmdir": all_args, "patch": first_arg,
    "cp": last_arg, "install": last_arg, "ln": last_arg,
    "sed": sed_targets,
    "dd": dd_targets,
}

# Tokens made up entirely of these characters are shell operators, never real paths.
OPERATOR_CHARS = set("();<>|&")
# Operators that separate one command from the next within a compound command.
CONNECTORS = {"|", "||", "&", "&&", ";", "(", ")"}


def is_operator_token(tok: str) -> bool:
    return bool(tok) and all(c in OPERATOR_CHARS for c in tok)


# Operator characters that never join another operator to form one shell operator. There is no
# `);` or `(;` operator, so a run like the `);` of `(ls); rm -f <main>/a` -- which shlex groups
# purely because the two characters are adjacent -- is really two, and leaving it grouped hides
# every command after it from split_segments entirely: no connector is recognised, the tail joins
# the preceding segment as arguments, and the mutator's own classifier is never consulted.
STANDALONE_OPERATOR_CHARS = set("();")


def split_operator_runs(tokens: list[str]) -> list[str]:
    """Break an adjacency-grouped operator token into the operators it really is. Only `(`, `)`
    and `;` are separated out: `&&`, `||` and the redirect forms (`>>`, `>&`) are genuine
    multi-character operators and must survive whole, or strip_redirections stops recognising
    them."""
    out: list[str] = []
    for tok in tokens:
        if not is_operator_token(tok) or not set(tok) & STANDALONE_OPERATOR_CHARS:
            out.append(tok)
            continue
        run = ""
        for char in tok:
            if char in STANDALONE_OPERATOR_CHARS:
                if run:
                    out.append(run)
                    run = ""
                out.append(char)
            else:
                run += char
        if run:
            out.append(run)
    return out


def tokenize(cmd: str) -> list[str]:
    """Tokenize a raw shell command string. `punctuation_chars=True` groups runs of `();<>|&`
    into single operator tokens (so `&&`/`>>`/`2>&1`'s `>&` stay intact) while still respecting
    quoting -- a quoted "<" stays literal data, never mistaken for an operator, and a filename
    with an embedded space tokenizes correctly (both of which a plain IFS/word-split can't do).
    The runs it groups by mere adjacency are then split back apart, see split_operator_runs.
    Malformed input (e.g. unbalanced quotes) fails open: no tokens, nothing gets checked, same
    "just don't match" fallback the rest of this hook already relies on."""
    try:
        lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return split_operator_runs(list(lexer))
    except ValueError:
        return []


def strip_redirections(tokens: list[str]) -> list[str]:
    """Drop shell redirection operators and the operand each one takes, e.g. the `<`/`diff.patch`
    in `patch f < diff.patch`, or the `2`/`>&`/`1` in `... 2>&1` (an fd number immediately before
    a redirect operator is part of the redirect, not a real argument). Left unstripped, a token
    like a lone `<` resolves via dirname all the way to the hook's own cwd -- a false-positive
    deny on any main-checkout invocation involving redirection. Actually treating `>`/`>>` targets
    as real write destinations is a separate, deliberately deferred feature; this only keeps them
    from being misread as an unrelated, harmless-looking path."""
    out: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if is_operator_token(tok) and ("<" in tok or ">" in tok):
            if out and out[-1].isdigit():
                out.pop()  # fd number immediately preceding the operator, e.g. "2" in "2>&1"
            i += 1
            if i < len(tokens):
                i += 1  # the redirect's target/operand
            continue
        out.append(tok)
        i += 1
    return out


# Connectors after which a `cd` in the segment just ended moves the shell for everything that
# follows. `|` and `&` are deliberately absent: each runs its left-hand side in a SUBSHELL, so a
# `cd` there leaves the parent shell exactly where it was, and honouring it would move the
# resolution point away from where the rest of the command really runs -- widening what is
# allowed, which this guard must never do.
CD_PROPAGATING_CONNECTORS = {";", "&&", "||"}


def cd_destination(segment: list[str], cwd: str) -> str | None:
    """Where a `cd` segment moves the shell from `cwd`, or None if it does not move it.

    Only a single operand naming an EXISTING directory counts. A `cd` to a path that isn't there
    fails and leaves the shell where it was, so honouring it would resolve later targets in a
    directory the command never reaches. `cd` with no operand (HOME), `cd -`, and any form with
    more than one operand are unhonoured for the same reason: the destination is not determined
    by the command text alone.

    normpath collapses `..` textually, which is what bash's own `cd` does; it is only ever handed
    to `git -C` and printed in a denial, both of which want the path the user would recognise."""
    if not segment or segment[0] != "cd":
        return None
    operands = [a for a in segment[1:] if not a.startswith("-")]
    if len(operands) != 1:
        return None
    dest = os.path.normpath(os.path.join(cwd, operands[0]))
    return dest if os.path.isdir(dest) else None


def segments_with_cwd(tokens: list[str], cwd: str) -> list[tuple[list[str], str]]:
    """Split a flat token stream into per-command segments, each paired with the cwd the shell
    would be in when that segment runs.

    Splitting at every connector is what catches a mutator embedded anywhere in a compound
    command rather than only its first clause (`git status; mv a b`). Pairing each segment with a
    cwd is what lets a relative target resolve where the command would really put it
    (`cd <worktree> && mkdir .brief`).

    Shell state is tracked only where the shell's own semantics make it unambiguous: a `cd`
    counts when a sequential connector follows it (see CD_PROPAGATING_CONNECTORS), and a `(`
    saves the cwd its matching `)` restores, because a subshell's `cd` does not move the
    enclosing shell. Every other way a directory can change -- `pushd`, a `cd` inside backticks or
    a shell function, an operand that only expands at runtime -- leaves the cwd where it was,
    which is the same resolve-from-here default a bare relative target already gets. Arbitrary
    shell can't be fully parsed, so this stays defense-in-depth, not an airtight guarantee."""
    out: list[tuple[list[str], str]] = []
    saved: list[str] = []
    current: list[str] = []
    for tok in tokens:
        if tok not in CONNECTORS:
            current.append(tok)
            continue
        segment = strip_redirections(current)
        current = []
        if segment:
            out.append((segment, cwd))
        if tok in CD_PROPAGATING_CONNECTORS:
            cwd = cd_destination(segment, cwd) or cwd
        elif tok == "(":
            saved.append(cwd)
        elif tok == ")" and saved:
            cwd = saved.pop()
    segment = strip_redirections(current)
    if segment:
        out.append((segment, cwd))
    return out


def git_dirs_for_path(path: str) -> tuple[str, str] | None:
    """Returns (git-dir, git-common-dir), both absolute, as seen from the nearest existing
    ancestor of `path` -- a file/dir that may not exist yet (a new file's parent dir must exist).
    None means `path` isn't inside any git repo at all. --path-format=absolute matters: git
    otherwise renders --git-dir and --git-common-dir in different formats (one absolute, one
    relative) from a subdirectory, which would break a naive string comparison of the two."""
    d = path
    while d != "/" and not os.path.isdir(d):
        d = os.path.dirname(d) or "."
    try:
        result = subprocess.run(
            ["git", "-C", d, "rev-parse", "--path-format=absolute",
             "--git-dir", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    lines = result.stdout.strip().splitlines()
    if len(lines) != 2:
        return None
    return lines[0], lines[1]


def is_main_checkout(path: str, cwd: str) -> bool:
    """True if `path`, resolved against `cwd`, lives in a main checkout (git-dir ==
    git-common-dir) rather than a linked worktree (where they differ -- a worktree's git-dir lives
    under the main repo's git-common-dir). An absolute `path` ignores `cwd` outright, which is
    what keeps an absolute path into the main checkout denied from any cwd whatsoever."""
    dirs = git_dirs_for_path(os.path.join(cwd, path))
    if dirs is None:
        return False
    git_dir, common_dir = dirs
    return bool(common_dir) and git_dir == common_dir


def check_git_segment(tokens: list[str]) -> str | None:
    """If this segment is a mutating `git` invocation, return the checkout path it targets
    (honoring the last `-C <path>`/`--git-dir <path>`/`--git-dir=<path>` override, else ".").
    Returns None if this segment isn't a tracked git-mutating verb at all.

    Scanning stops at the first non-flag token that is not a tracked verb, which is what keeps
    `git status` and every other untracked subcommand allowed. A global flag's separated operand
    is not such a token -- it belongs to the flag -- so it is stepped over rather than ending the
    scan; see GIT_FLAGS_TAKING_SEPARATE_OPERAND."""
    if not tokens or tokens[0] != "git":
        return None
    target = "."
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in GIT_FLAGS_TAKING_SEPARATE_OPERAND and i + 1 < len(tokens):
            if tok in GIT_FLAGS_NAMING_THE_TARGET:
                target = tokens[i + 1]
            i += 2
            continue
        if tok.startswith("--git-dir="):
            target = tok.split("=", 1)[1]
            i += 1
            continue
        if tok in GIT_MUTATING_VERBS:
            return target
        if tok.startswith("-"):
            i += 1
            continue
        return None  # some other subcommand (e.g. "status") -- not tracked, bail
    return None


def check_shell_segment(tokens: list[str]) -> list[str]:
    if not tokens:
        return []
    classifier = SHELL_MUTATORS.get(tokens[0])
    return classifier(tokens[1:]) if classifier else []


def deny(target: str, cwd: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason_for(target, cwd),
        }
    }))


def allow() -> None:
    print("{}")


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name")
    # The session cwd, which is where Claude Code spawns this hook and where every Bash command
    # it is asked about begins. A file-editing tool's relative path has no shell to move it, so
    # this is the whole story for those; a Bash command can `cd` from here.
    cwd = os.getcwd()

    if tool in ("Edit", "Write", "NotebookEdit"):
        file_path = data["tool_input"]["file_path"]
        deny(file_path, cwd) if is_main_checkout(file_path, cwd) else allow()
        return

    if tool == "Bash":
        cmd = data["tool_input"]["command"]
        for segment, segment_cwd in segments_with_cwd(tokenize(cmd), cwd):
            git_target = check_git_segment(segment)
            if git_target is not None and is_main_checkout(git_target, segment_cwd):
                deny(git_target, segment_cwd)
                return
            for path in check_shell_segment(segment):
                if is_main_checkout(path, segment_cwd):
                    deny(path, segment_cwd)
                    return
        allow()
        return

    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail open on anything unexpected (malformed stdin, missing fields, ...), the same
        # "just don't match" fallback every other unrecognized case in this hook already has.
        allow()
