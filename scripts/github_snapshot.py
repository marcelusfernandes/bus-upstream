"""Load a validator snapshot from GitHub (one milestone) plus the initiative's files.

transform() is pure and tested; fetch() is the only network call. Pages hold up to
100 issues, comments and label events each. A larger milestone raises instead of
returning a partial snapshot: a drift check that sees part of the data is worse than none.
"""
import json
import re
from pathlib import Path

QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    milestone(number: $number) {
      number
      issues(first: 100) {
        pageInfo { hasNextPage }
        nodes {
          number title body state
          parent { number }
          labels(first: 50) { nodes { name } }
          assignees(first: 10) { nodes { login } }
          comments(first: 100) { pageInfo { hasNextPage } nodes { author { login } body createdAt } }
          timelineItems(first: 100, itemTypes: [LABELED_EVENT, UNLABELED_EVENT]) {
            pageInfo { hasNextPage }
            nodes {
              __typename
              ... on LabeledEvent { createdAt label { name } actor { login } }
              ... on UnlabeledEvent { createdAt label { name } actor { login } }
            }
          }
        }
      }
    }
  }
}
"""

_ACTION = {"LabeledEvent": "added", "UnlabeledEvent": "removed"}


def _login(node):
    return node["login"] if node else None


def _issue(node):
    return {
        "number": node["number"],
        "title": node["title"],
        "body": node.get("body") or "",
        "state": node["state"].lower(),
        "parent": node["parent"]["number"] if node.get("parent") else None,
        "labels": [l["name"] for l in node["labels"]["nodes"]],
        "assignees": [a["login"] for a in node["assignees"]["nodes"]],
        "comments": [{"author": _login(cm["author"]), "body": cm["body"], "created_at": cm["createdAt"]}
                     for cm in node["comments"]["nodes"]],
        "label_events": [{"label": e["label"]["name"], "action": _ACTION[e["__typename"]],
                          "created_at": e["createdAt"], "actor": _login(e.get("actor"))}
                         for e in node["timelineItems"]["nodes"] if e.get("__typename") in _ACTION],
    }


def _truncated(connection):
    return bool((connection.get("pageInfo") or {}).get("hasNextPage"))


def transform(payload, files):
    milestone = payload["data"]["repository"]["milestone"]
    if milestone is None:
        raise ValueError("milestone not found")
    nodes = milestone["issues"]["nodes"]
    if _truncated(milestone["issues"]) or any(
            _truncated(n["comments"]) or _truncated(n["timelineItems"]) for n in nodes):
        raise ValueError(f"milestone #{milestone['number']} needs pagination (more than 100 items)")
    return {"issues": [_issue(n) for n in milestone["issues"]["nodes"]], "files": dict(files)}


def milestone_from_readme(text):
    m = re.search(r"^Milestone: #(\d+)\s*$", text, re.MULTILINE)
    return int(m.group(1)) if m else None


def load_files(initiative_dir, root):
    base = Path(initiative_dir)
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8") for p in base.rglob("*.md")}


def fetch(repo, milestone):
    import gh_client as gh
    owner, name = repo.split("/", 1)
    out = gh.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={owner}",
                  "-F", f"name={name}", "-F", f"number={milestone}"])
    return json.loads(out)


def load_initiative(repo, initiative_dir, root):
    """Snapshot for one initiatives/<slug>/ folder, or None if it has no milestone yet."""
    readme = Path(initiative_dir) / "README.md"
    milestone = milestone_from_readme(readme.read_text(encoding="utf-8")) if readme.exists() else None
    if milestone is None:
        return None
    return transform(fetch(repo, milestone), load_files(initiative_dir, root))
