#!/usr/bin/env python3
"""Codex hooks (configured in .codex/config.toml).

pre-tool-use: blocks an agent's `gh issue edit` label change that would add a validator
error (and any attempt by an agent to add human:decided, which only the /decide Action
may apply). stop: blocks the end of a turn once if files and GitHub have drifted.
Exit code 2 with the reason on stderr blocks (Codex hooks reference). If GitHub cannot
be reached the hooks fail open and say so on stderr.
"""
import copy
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

import upstream_validate as v

ROOT = Path(__file__).resolve().parents[1]


_SEPARATORS = {";", "&&", "||", "|", "&", "\n"}


def _segments(command):
    """Shell-like tokens (quotes respected), split on command separators."""
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    segments, current = [], []
    try:
        for token in lexer:
            if token in _SEPARATORS:
                segments.append(current)
                current = []
            else:
                current.append(token)
    except ValueError:  # unbalanced quotes: nothing reliable to parse
        return []
    return segments + [current]


def _labels(value):
    return [x.strip() for x in value.split(",") if x.strip()]


def label_edits(command):
    """[(issue number, added labels, removed labels)] for each `gh issue edit` in a shell command.

    Only covers `gh issue edit`. `gh api .../labels` bypasses this hook; the GitHub Action,
    the reconcile and the PR check remain the real gate (spec/v1/08)."""
    edits = []
    for tokens in _segments(command):
        if tokens[:3] != ["gh", "issue", "edit"]:
            continue
        number, added, removed, skip = None, [], [], False
        for i, token in enumerate(tokens[3:], start=3):
            if skip:
                skip = False
                continue
            if token in ("--add-label", "--remove-label") and i + 1 < len(tokens):
                (added if token == "--add-label" else removed).extend(_labels(tokens[i + 1]))
                skip = True
            elif token.startswith("-"):
                skip = "=" not in token and i + 1 < len(tokens) and not tokens[i + 1].startswith("-")
            elif number is None and token.isdigit():
                number = int(token)
        if number is not None:
            edits.append((number, added, removed))
    return edits


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _simulate(snap, number, added, removed):
    after = copy.deepcopy(snap)
    issue = next(i for i in after["issues"] if i["number"] == number)
    issue["labels"] = [l for l in issue["labels"] if l not in removed] + [l for l in added if l not in issue["labels"]]
    issue["label_events"] = issue.get("label_events", []) + [
        {"label": l, "action": "added", "created_at": _now(), "actor": "agent"} for l in added]
    return after


def _key(e):
    return (e.check, e.where, e.message)


def pre_tool_use(event, load):
    """Reason to block, or None. load(issue number) -> snapshot containing it, or None."""
    if event.get("tool_name") != "Bash":
        return None
    reasons = []
    for number, added, removed in label_edits(event.get("tool_input", {}).get("command", "")):
        if "human:decided" in added:
            reasons.append(f"#{number}: only the PM's /decide may apply human:decided")
            continue
        snap = load(number)
        if not snap or not any(i["number"] == number for i in snap["issues"]):
            continue
        before = {_key(e) for e in v.validate_snapshot(snap)}
        new = [e for e in v.validate_snapshot(_simulate(snap, number, added, removed)) if _key(e) not in before]
        reasons += [str(e) for e in new]
    return "\n".join(reasons) or None


def stop(event, snapshots):
    """Reason to keep going (once), or None."""
    if event.get("stop_hook_active"):
        return None
    errors = [str(e) for snap in snapshots for e in v.validate_files_and_comments(snap)]
    return ("Files and GitHub have drifted; fix before stopping:\n" + "\n".join(errors)) if errors else None


# ---------- live loading ----------

def _initiative_dirs():
    base = ROOT / "initiatives"
    return [d for d in sorted(base.iterdir()) if d.is_dir()] if base.exists() else []


def _live_snapshots():
    import gh_client as gh
    import github_snapshot as g
    repo = gh.current_repo()
    snaps = [g.load_initiative(repo, d, ROOT) for d in _initiative_dirs()]
    return [s for s in snaps if s]


def _live_loader():
    cache = {}

    def load(number):
        if "all" not in cache:
            cache["all"] = _live_snapshots()
        return next((s for s in cache["all"] if any(i["number"] == number for i in s["issues"])), None)
    return load


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    event = json.loads(sys.stdin.read() or "{}")
    try:
        if mode == "pre-tool-use":
            reason = pre_tool_use(event, _live_loader())
        elif mode == "stop":
            reason = stop(event, [] if event.get("stop_hook_active") else _live_snapshots())
        else:
            print("usage: codex_hooks.py pre-tool-use|stop", file=sys.stderr)
            return 0
    except Exception as err:  # fail open: a broken hook must not stop all agent work
        print(f"upstream hook skipped ({mode}): {err}", file=sys.stderr)
        return 0
    if reason:
        print(reason, file=sys.stderr)
        return 2
    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
