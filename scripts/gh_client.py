"""Thin `gh` wrappers. The only GitHub write path for the scripts; commands are
argument lists, never shell strings, so issue text cannot inject commands."""
import json
import subprocess


class GhError(RuntimeError):
    pass


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GhError(f"{' '.join(cmd[:4])}…: {result.stderr.strip()}")
    return result.stdout


def current_repo():
    return json.loads(run(["gh", "repo", "view", "--json", "nameWithOwner"]))["nameWithOwner"]


def create_milestone(repo, title, description):
    out = run(["gh", "api", f"repos/{repo}/milestones", "-f", f"title={title}", "-f", f"description={description}"])
    return json.loads(out)["number"]


def create_issue(repo, title, body, labels, milestone_title):
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body, "--milestone", milestone_title]
    for label in labels:
        cmd += ["--label", label]
    url = run(cmd).strip().splitlines()[-1]
    return int(url.rstrip("/").split("/")[-1])


def comment(repo, number, body):
    run(["gh", "issue", "comment", str(number), "--repo", repo, "--body", body])


def add_sub_issue(repo, parent, child):
    child_id = json.loads(run(["gh", "api", f"repos/{repo}/issues/{child}"]))["id"]
    run(["gh", "api", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={child_id}"])
