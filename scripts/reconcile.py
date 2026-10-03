#!/usr/bin/env python3
"""Orchestrator reconcile: rebuild an initiative's state from GitHub, as facts.

This is a state reader, not a router. It reports each layer's state, scores, open
hypotheses and decisions, plus the contract obligations that are mechanical (drift to
fix, decided decisions to record, PM replies to answer, blocked layers without a
decision). It never says which layer to work on next: the BUS process is non-linear
and can start or return to any layer, so that choice is the orchestrator's judgment,
written in .agents/skills/orchestrator/SKILL.md where PMs can edit it.

Usage: reconcile.py <slug> [--json]
"""
import json
import re
import sys

import upstream_contract as c
import upstream_validate as v

LAYER_LABEL = {"B": "layer:business", "U": "layer:user", "S": "layer:solution"}


def _has(issue, label):
    return label in issue.get("labels", [])


def _id(issue, pattern):
    m = re.match(pattern, issue.get("title", ""))
    return m.group(0) if m else None


def _state(issue):
    return next((l.split(":", 1)[1] for l in issue["labels"] if l.startswith("state:")), None)


def _scores(issue):
    m = re.search(c.SCORE_HEADER, (issue.get("body") or "").replace("\r\n", "\n"), re.MULTILINE)
    return (int(m["d"]), int(m["g"])) if m else (None, None)


def _blocked_since(epic):
    times = [e["created_at"] for e in epic.get("label_events", [])
             if e["label"] == "state:blocked" and e["action"] == "added"]
    return max(times) if times else ""


def _recorded_after(kids, since):
    """A decision under this layer was recorded (closed with its record) after `since`."""
    for k in kids:
        if _has(k, "type:decision") and k.get("state") == "closed":
            for cm in k.get("comments", []):
                text = cm["body"].replace("\r\n", "\n")
                if cm["created_at"] > since and re.search(c.DECISION_TITLE, text, re.MULTILINE):
                    return True
    return False


def _layer(snap, code):
    epic = next((i for i in snap["issues"] if _has(i, "epic") and _has(i, LAYER_LABEL[code])), None)
    if epic is None:
        return None
    kids = [i for i in snap["issues"] if i.get("parent") == epic["number"]]
    d, g = _scores(epic)
    blocked = _state(epic) == "blocked"
    return {"issue": epic["number"], "state": _state(epic), "definition": d, "grounding": g,
            "unblock_decided": blocked and _recorded_after(kids, _blocked_since(epic)),
            "open_hypotheses": sorted(_id(k, c.HYPOTHESIS_ID) for k in kids
                                      if _has(k, "type:hypothesis") and _has(k, "hyp:open")),
            "pending_decisions": sorted(_id(k, c.DECISION_ID) for k in kids
                                        if _has(k, "type:decision") and _has(k, "human:pending")
                                        and k.get("state") == "open")}


def _needs_reply(issue):
    """Assigned PM commented after the last non-PM comment, without a /decide."""
    assignees = set(issue.get("assignees", []))
    comments = sorted(issue.get("comments", []), key=lambda cm: cm["created_at"])
    if not comments or comments[-1]["author"] not in assignees:
        return False
    return not re.search(c.DECIDE_COMMAND, comments[-1]["body"].replace("\r\n", "\n"), re.MULTILINE)


def _awaits_agent(snap, decision):
    """Autonomous mode: an open decision with no human:* or agent:* label waits for the agent."""
    if decision.get("state") != "open" or any(l.startswith(("human:", "agent:")) for l in decision["labels"]):
        return False
    parent = next((i for i in snap["issues"] if i["number"] == decision.get("parent")), None)
    return bool(parent and _has(parent, "mode:autonomous"))


def _obligations(report):
    """Mechanical must-dos from the contract. Not a work order between layers."""
    out = [f"fix drift: {e}" for e in report["drift"]]
    out += [f"record decision {d} (decided, still open)" for d in report["decided_unrecorded"]]
    out += [f"reply to the PM on {r['decision']} (comment without /decide)" for r in report["needs_reply"]]
    out += [f"decide {d} (autonomous mode)" for d in report["agent_decide"]]
    for code, layer in report["layers"].items():
        if layer["state"] == "blocked" and not layer["pending_decisions"]:
            out.append(f"{code} is blocked: " + ("the PM decided how to unblock; act on it" if layer["unblock_decided"]
                                                else "open a decision for the PM"))
    return out


def reconcile(snap):
    decisions = [i for i in snap["issues"] if _has(i, "type:decision")]
    report = {
        "drift": [str(e) for e in v.validate_snapshot(snap) + v.validate_files_and_comments(snap)],
        "layers": {code: layer for code in LAYER_LABEL if (layer := _layer(snap, code))},
        "needs_reply": [{"decision": _id(d, c.DECISION_ID), "issue": d["number"]} for d in decisions
                        if d.get("state") == "open" and _has(d, "human:pending") and _needs_reply(d)],
        "decided_unrecorded": [_id(d, c.DECISION_ID) for d in decisions
                               if d.get("state") == "open" and _has(d, "human:decided")],
        "agent_decide": [_id(d, c.DECISION_ID) for d in decisions if _awaits_agent(snap, d)],
    }
    report["obligations"] = _obligations(report)
    return report


def summary(report):
    lines = [f"{code}: {layer['state']} · D{layer['definition']} G{layer['grounding']}"
             f" · open H {', '.join(layer['open_hypotheses']) or '-'}"
             f" · pending D {', '.join(layer['pending_decisions']) or '-'}"
             for code, layer in report["layers"].items()]
    lines += [f"Must do: {o}" for o in report["obligations"][:8]] or ["Must do: nothing pending"]
    return "\n".join(lines[:15])


def main(argv):
    from pathlib import Path

    import gh_client as gh
    import github_snapshot as g
    root = Path(__file__).resolve().parents[1]
    if len(argv) < 2:
        print("usage: reconcile.py <slug> [--json]", file=sys.stderr)
        return 2
    snap = g.load_initiative(gh.current_repo(), root / "initiatives" / argv[1], root)
    if snap is None:
        print(f"initiatives/{argv[1]} has no milestone yet", file=sys.stderr)
        return 1
    report = reconcile(snap)
    print(json.dumps(report, indent=2) if "--json" in argv else summary(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
