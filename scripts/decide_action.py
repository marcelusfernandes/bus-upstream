#!/usr/bin/env python3
"""/decide handler for the GitHub Action (spec/v1/04-github-contract.md).

Only the assigned PM can decide. A valid /decide swaps human:pending -> human:decided
and acknowledges; it never closes the issue (the orchestrator posts the decision record
and closes). Comments without /decide are ignored here; the orchestrator's reconcile
finds PM replies on pending decisions. The comment body is untrusted: it is never
echoed for refused requests and never reaches a shell.
"""
import json
import re
import sys

import upstream_contract as c


def parse_decide(body):
    """(target D-id or None, choice) of the first /decide line, or None."""
    m = re.search(c.DECIDE_COMMAND, (body or "").replace("\r\n", "\n"), re.MULTILINE)
    return (m["target"], m["choice"]) if m else None


def _has(issue, label):
    return label in issue.get("labels", [])


def _reply(issue, text):
    return [{"kind": "comment", "issue": issue["number"], "body": text}]


def _refusal(target, author):
    if not _has(target, "type:decision"):
        return "This issue is not a decision. Use `/decide D-nnn <option>` to name one."
    if _has(target, "human:decided") or _has(target, "agent:decided"):
        return f"D-issue #{target['number']} is already decided."
    if not _has(target, "human:pending"):
        return f"D-issue #{target['number']} is not waiting for a decision."
    if author not in target.get("assignees", []):
        owners = ", ".join(f"@{a}" for a in target.get("assignees", [])) or "the assigned PM"
        return f"Only {owners} can decide #{target['number']}. Nothing changed."
    return None


TRUSTED_ASSOCIATIONS = ("OWNER", "MEMBER", "COLLABORATOR")


def plan(comment, here, lookup):
    """comment: {author, body, url, association}; here: the issue commented on;
    lookup(D-id) -> issue or None. Outsiders on a public repo are ignored silently."""
    if comment["author"].endswith("[bot]"):
        return []
    if comment.get("association", "OWNER") not in TRUSTED_ASSOCIATIONS:
        return []
    parsed = parse_decide(comment["body"])
    if parsed is None:
        return []
    target_id, choice = parsed
    target = lookup(target_id) if target_id else here
    if target is None:
        return _reply(here, f"No decision issue found for {target_id}. Nothing changed.")
    refusal = _refusal(target, comment["author"])
    if refusal:
        return _reply(here, refusal)
    n = target["number"]
    actions = [{"kind": "remove_label", "issue": n, "label": "human:pending"},
               {"kind": "add_label", "issue": n, "label": "human:decided"},
               {"kind": "comment", "issue": n,
                "body": f"Decision received from @{comment['author']}: **{choice}** ({comment['url']}). "
                        "The orchestrator will post the decision record and close this issue."}]
    if target["number"] != here["number"]:
        actions.append({"kind": "comment", "issue": here["number"], "body": f"Applied to #{n}."})
    return actions


def to_gh_commands(actions):
    cmds = []
    for a in actions:
        n = str(a["issue"])
        if a["kind"] == "comment":
            cmds.append(["gh", "issue", "comment", n, "--body", a["body"]])
        elif a["kind"] == "add_label":
            cmds.append(["gh", "issue", "edit", n, "--add-label", a["label"]])
        elif a["kind"] == "remove_label":
            cmds.append(["gh", "issue", "edit", n, "--remove-label", a["label"]])
    return cmds


def _issue_from_event(issue):
    return {"number": issue["number"], "title": issue["title"],
            "labels": [l["name"] for l in issue.get("labels", [])],
            "assignees": [a["login"] for a in issue.get("assignees", [])]}


def _lookup(decision_id):
    import gh_client as gh
    out = gh.run(["gh", "issue", "list", "--state", "all", "--label", "type:decision", "--search",
                  f"{decision_id} in:title", "--json", "number,title,labels,assignees"])
    for issue in json.loads(out):
        if re.search(rf"\b{decision_id}\b", issue["title"]):
            return _issue_from_event(issue)
    return None


def main(argv):
    import gh_client as gh
    with open(argv[1], encoding="utf-8") as f:
        event = json.load(f)
    comment = {"author": event["comment"]["user"]["login"], "body": event["comment"]["body"],
               "url": event["comment"]["html_url"],
               "association": event["comment"].get("author_association", "NONE")}
    for cmd in to_gh_commands(plan(comment, _issue_from_event(event["issue"]), _lookup)):
        gh.run(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
