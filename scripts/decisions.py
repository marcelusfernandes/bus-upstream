"""Reads decisions from an issue's comments (spec/v1/04-github-contract.md).

A decision lives inside the issue that requested it, so the issue tells the whole story:

    ## Decision request D-001 · B-01 · <question>     (agent: options + recommendation)
    /decide A  (Why: ...)                             (the assigned PM, own words)
    ## Decision D-001 · B-01 · <answer>               (agent: the record)

A bare `/decide X` applies only when exactly one request is waiting for the PM at that
moment; otherwise the PM names it (`/decide D-001 X`). Shared by the /decide Action,
the validator, the ops helper and reconcile, so all read decisions the same way.
"""
import re

import upstream_contract as c

OPTION_LINE = r"^- \*\*([A-Z])\*\* — (.+?) · trade-offs:"


def _text(cm):
    return (cm.get("body") or "").replace("\r\n", "\n")


def is_agent_comment(cm):
    """Agents comment with the PM's own GitHub account today, so authorship cannot tell them
    apart. An agent comment carries the hidden Enceladus marker (outside any quote) or, for
    comments written before the signature existed, starts with a `## ` title line. A PM who
    quote-replies an agent comment is still the PM."""
    lines = _text(cm).splitlines()
    if any(re.search(c.AGENT_MARKER, line) and not line.lstrip().startswith(">") for line in lines):
        return True
    first = next((line for line in lines if line.strip()), "")
    return first.startswith("## ")


def _ordered(issue):
    return sorted(issue.get("comments", []), key=lambda cm: cm["created_at"])


def requests(issue):
    """D-id -> {ref, question, options, requested_at} for every request on the issue."""
    found = {}
    for cm in _ordered(issue):
        m = re.search(c.DECISION_REQUEST_TITLE, _text(cm), re.MULTILINE)
        if m and m["id"] not in found:
            found[m["id"]] = {"ref": m["ref"], "question": m["question"], "requested_at": cm["created_at"],
                              "options": dict(re.findall(OPTION_LINE, _text(cm), re.MULTILINE))}
    return found


def record_comments(issue):
    """D-id -> its record comment (the first one)."""
    found = {}
    for cm in _ordered(issue):
        m = re.search(c.DECISION_TITLE, _text(cm), re.MULTILINE)
        if m:
            found.setdefault(m["id"], cm)
    return found


def records(issue):
    """D-id -> created_at of its record comment."""
    return {rid: cm["created_at"] for rid, cm in record_comments(issue).items()}


def recorded_by(issue, decision_id):
    """'agent', a PM login, or None, from the record's `Decided by:` line."""
    cm = record_comments(issue).get(decision_id)
    m = re.search(r"Decided by: (?:@(\S+)|(agent))", _text(cm)) if cm else None
    return (m.group(1) or m.group(2)) if m else None


def _valid_choice(req, choice):
    return choice.startswith("other: ") or choice in req["options"]


def _pm_decisions(issue):
    """[(D-id, decide dict)] in order: valid /decide comments by an assignee, resolved to a request."""
    reqs, recs = requests(issue), records(issue)
    assignees, decided, out = set(issue.get("assignees", [])), set(), []
    for cm in _ordered(issue):
        if cm["author"] not in assignees or is_agent_comment(cm):
            continue
        m = re.search(c.DECIDE_COMMAND, _text(cm), re.MULTILINE)
        if not m:
            continue
        waiting = [rid for rid, r in reqs.items() if r["requested_at"] < cm["created_at"]
                   and rid not in decided and not (rid in recs and recs[rid] < cm["created_at"])]
        target = m["target"] or (waiting[0] if len(waiting) == 1 else None)
        if target in waiting and _valid_choice(reqs[target], m["choice"]):
            why = re.search(r"^Why: (.+)$", _text(cm), re.MULTILINE)
            decided.add(target)
            out.append((target, {"author": cm["author"], "choice": m["choice"],
                                 "why": why.group(1).strip() if why else None, "created_at": cm["created_at"]}))
    return out


def pm_decisions(issue):
    """[(D-id, decide)] for every valid /decide by the assigned PM on this issue."""
    return _pm_decisions(issue)


def pm_decision(issue, decision_id):
    return next((dec for rid, dec in _pm_decisions(issue) if rid == decision_id), None)


def open_requests(issue):
    """Requests with no record yet, in request order."""
    recs = records(issue)
    return [rid for rid in requests(issue) if rid not in recs]


def awaiting_pm(issue):
    """Open requests the PM has not decided yet."""
    decided = {rid for rid, _ in _pm_decisions(issue)}
    return [rid for rid in open_requests(issue) if rid not in decided]


def decided_unrecorded(issue):
    decided = {rid for rid, _ in _pm_decisions(issue)}
    return [rid for rid in open_requests(issue) if rid in decided]


def answer_text(issue, decision_id, choice):
    if choice.startswith("other: "):
        return choice[len("other: "):].strip()
    return requests(issue)[decision_id]["options"].get(choice)


def expected_labels(issue, blocked=False, autonomous=False):
    """The decision labels an issue should carry, from its comments. One human: label at most:
    human:pending while anything waits for the PM (or the layer is blocked), otherwise
    human:decided once the PM has decided something here. agent:decided is history: it is
    expected once an agent record exists and is never removed (None = leave as is)."""
    waiting = (bool(awaiting_pm(issue)) and not autonomous) or blocked
    pm_decided = bool(_pm_decisions(issue)) or any(
        (by := recorded_by(issue, rid)) and by != "agent" for rid in records(issue))
    agent_decided = any(recorded_by(issue, rid) == "agent" for rid in records(issue))
    return {"human:pending": waiting,
            "human:decided": (not waiting) and pm_decided,
            "agent:decided": True if agent_decided else None}


def open_request_ids(snap):
    return {rid for i in snap["issues"] for rid in open_requests(i)}


def find_request(snap, decision_id):
    """(issue, request) holding the request for decision_id, or (None, None)."""
    for issue in snap["issues"]:
        req = requests(issue).get(decision_id)
        if req:
            return issue, req
    return None, None
