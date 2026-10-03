#!/usr/bin/env python3
"""/decide handler for the GitHub Action (spec/v1/04-github-contract.md).

Decisions live in the issue that requested them. A PM's `/decide` applies to a request
on the same issue: bare when exactly one is waiting, `/decide D-nnn X` otherwise. Only
the assigned PM can decide. A valid /decide adds human:decided (and removes
human:pending when nothing else waits for the PM) and acknowledges; the orchestrator
posts the record in the same issue afterwards. The comment body is untrusted: it is
never echoed in refusals and never reaches a shell.
"""
import json
import os
import re
import sys

import decisions as d
import upstream_contract as c

TRUSTED_ASSOCIATIONS = ("OWNER", "MEMBER", "COLLABORATOR")


def parse_decide(body):
    """(target D-id or None, choice) of the first /decide line, or None."""
    m = re.search(c.DECIDE_COMMAND, (body or "").replace("\r\n", "\n"), re.MULTILINE)
    return (m["target"], m["choice"]) if m else None


def _reply(issue, text):
    return [{"kind": "comment", "issue": issue["number"], "body": text}]


def _refusal(issue, target_id, choice, author):
    """Reason the /decide cannot apply, or None. `issue` holds only comments before it."""
    waiting = d.awaiting_pm(issue)
    if target_id is None:
        if not waiting:
            return "No decision is waiting for the PM on this issue. Nothing changed."
        if len(waiting) > 1:
            return f"Several decisions are waiting here ({', '.join(waiting)}). Name one: `/decide {waiting[0]} <option>`."
        target_id = waiting[0]
    if target_id not in waiting:
        if target_id in d.decided_unrecorded(issue):
            return f"{target_id} is already decided; its record will be posted here."
        if target_id in d.records(issue):
            return f"{target_id} is already recorded. Nothing changed."
        return f"No request for {target_id} on this issue. Nothing changed."
    if author not in issue.get("assignees", []):
        owners = ", ".join(f"@{a}" for a in issue.get("assignees", [])) or "the assigned PM"
        return f"Only {owners} can decide {target_id}. Nothing changed."
    options = d.requests(issue)[target_id]["options"]
    if not (choice.startswith("other: ") or choice in options):
        return f"{target_id} has options {', '.join(sorted(options))} (or `other: <your option>`). Nothing changed."
    return None


def plan(comment, issue):
    """comment: {author, body, url, association}; issue: the issue with the comments BEFORE this one."""
    if comment["author"].endswith("[bot]") or comment.get("association", "OWNER") not in TRUSTED_ASSOCIATIONS:
        return []
    if d.is_agent_comment(comment):  # agents share the PM's account; their comments start with "## "
        return []
    parsed = parse_decide(comment["body"])
    if parsed is None:
        return []
    target_id, choice = parsed
    refusal = _refusal(issue, target_id, choice, comment["author"])
    if refusal:
        return _reply(issue, refusal)
    waiting = d.awaiting_pm(issue)
    target_id = target_id or waiting[0]
    n = issue["number"]
    actions = [{"kind": "add_label", "issue": n, "label": "human:decided"}]
    if not [w for w in waiting if w != target_id]:
        actions.append({"kind": "remove_label", "issue": n, "label": "human:pending"})
    actions.append({"kind": "comment", "issue": n,
                    "body": f"{target_id} decided by @{comment['author']}: **{choice}** ({comment['url']}). "
                            "The orchestrator will post the decision record here."})
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


def _issue_before(event, comments):
    """The issue as it was before this comment, with its earlier comments."""
    issue, current = event["issue"], event["comment"]["id"]
    return {"number": issue["number"], "title": issue["title"],
            "labels": [l["name"] for l in issue.get("labels", [])],
            "assignees": [a["login"] for a in issue.get("assignees", [])],
            "comments": [{"author": (cm.get("user") or {}).get("login"), "body": cm.get("body") or "",
                          "created_at": cm["created_at"]} for cm in comments if cm.get("id") != current]}


def main(argv):
    import gh_client as gh
    with open(argv[1], encoding="utf-8") as f:
        event = json.load(f)
    repo = os.environ.get("GH_REPO") or event["repository"]["full_name"]
    out = gh.run(["gh", "api", "--paginate", f"repos/{repo}/issues/{event['issue']['number']}/comments", "--jq", ".[]"])
    comments = [json.loads(line) for line in out.splitlines() if line.strip()]  # one per line, across pages
    comment = {"author": event["comment"]["user"]["login"], "body": event["comment"]["body"],
               "url": event["comment"]["html_url"], "association": event["comment"].get("author_association", "NONE")}
    for cmd in to_gh_commands(plan(comment, _issue_before(event, comments))):
        gh.run(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
