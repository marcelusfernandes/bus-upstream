"""Thin `gh` wrappers. The only GitHub write path for the scripts; commands are
argument lists, never shell strings, so issue text cannot inject commands."""
import json
import subprocess


class GhError(RuntimeError):
    pass


def run(cmd, stdin=None):
    result = subprocess.run(cmd, capture_output=True, text=True, input=stdin)
    if result.returncode != 0:
        raise GhError(f"{' '.join(cmd[:4])}…: {result.stderr.strip()}")
    return result.stdout


def current_repo():
    return json.loads(run(["gh", "repo", "view", "--json", "nameWithOwner"]))["nameWithOwner"]


def create_milestone(repo, title, description):
    out = run(["gh", "api", f"repos/{repo}/milestones", "-f", f"title={title}", "-f", f"description={description}"])
    return json.loads(out)["number"]




def comment(repo, number, body):
    run(["gh", "issue", "comment", str(number), "--repo", repo, "--body", body])


def add_sub_issue(repo, parent, child):
    child_id = json.loads(run(["gh", "api", f"repos/{repo}/issues/{child}"]))["id"]
    run(["gh", "api", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={child_id}"])


def create_issue_api(repo, title, body, labels, assignees, milestone):
    payload = json.dumps({"title": title, "body": body, "labels": labels, "assignees": assignees,
                          "milestone": milestone})
    out = run(["gh", "api", f"repos/{repo}/issues", "-X", "POST", "--input", "-"], stdin=payload)
    return json.loads(out)["number"]


def edit_body(repo, number, body):
    run(["gh", "issue", "edit", str(number), "--repo", repo, "--body", body])


def edit_labels(repo, number, add, remove):
    cmd = ["gh", "issue", "edit", str(number), "--repo", repo]
    for label in add:
        cmd += ["--add-label", label]
    for label in remove:
        cmd += ["--remove-label", label]
    run(cmd)


def close_issue(repo, number):
    run(["gh", "issue", "close", str(number), "--repo", repo])
