"""Snapshot builders for validator tests.

A snapshot is the validator's only input: GitHub issues (with labels, comments and
label events) plus repository files, as plain dicts and strings.
"""

T0 = "2026-10-02T10:00:00Z"
T1 = "2026-10-02T11:00:00Z"
T2 = "2026-10-02T12:00:00Z"
T3 = "2026-10-02T13:00:00Z"

PM = "junior-pm"


def issue(number, title, labels, body="", parent=None, state="open",
          assignees=(), comments=(), label_events=()):
    return {
        "number": number,
        "title": title,
        "labels": list(labels),
        "body": body,
        "parent": parent,
        "state": state,
        "assignees": list(assignees),
        "comments": list(comments),
        "label_events": list(label_events),
    }


def comment(author, body, created_at=T1):
    return {"author": author, "body": body, "created_at": created_at}


def event(label, action, created_at, actor="agent"):
    return {"label": label, "action": action, "created_at": created_at, "actor": actor}


def header(definition, grounding, spread=0):
    return f"> **Definition:** {definition} · **Grounding:** {grounding} · **Spread:** {spread}"


def first_score(layer, definition, grounding):
    return comment("agent", f"## Score · {layer} · Definition – → {definition} · Grounding – → {grounding}\n"
                            "Why: intake baseline", T0)


def usual_basket():
    """Intake snapshot of evals/usual-basket, built from spec/v1/09-worked-example.md."""
    epic_labels = ["epic", "state:ready", "mode:piloted"]
    issues = [
        issue(1, "B · Business problem", epic_labels + ["layer:business"], header(5, 3),
              comments=[first_score("B", 5, 3)]),
        issue(2, "U · User problem", epic_labels + ["layer:user"], header(1, 2),
              comments=[first_score("U", 1, 2)]),
        issue(3, "S · Solution", epic_labels + ["layer:solution"], header(5, 0),
              comments=[first_score("S", 5, 0)]),
        issue(4, "PRD", ["epic", "state:ready", "mode:piloted", "layer:prd"]),
        issue(5, "H-01 · a faster flow",
              ["type:hypothesis", "hyp:open", "layer:solution"], parent=3),
        issue(6, "H-02 · if it is faster, it converts more than the App",
              ["type:hypothesis", "hyp:open", "layer:user"], parent=2),
        issue(7, "H-03 · it helps recurrence or changes AOV",
              ["type:hypothesis", "hyp:open", "layer:business"], parent=1),
    ]
    files = {
        "initiatives/usual-basket/hypotheses.md": (
            "| ID | Statement | Kind | Origin | Basis | Raised at | Routed to | Status | Resolution |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| H-01 | a faster flow | solution | business demand | intake | B | S | open | — |\n"
            "| H-02 | if it is faster, it converts more than the App | causal | business demand | intake | B | U | open | — |\n"
            "| H-03 | it helps recurrence or changes AOV | causal | business demand | intake | B | B | open | — |\n"
        ),
    }
    return {"issues": issues, "files": files}


def by_number(snapshot, number):
    return next(i for i in snapshot["issues"] if i["number"] == number)
