#!/usr/bin/env python3
"""Create an initiative from an intake JSON: milestone, B/U/S/PRD epics with the
first score comments, hypothesis sub-issues, and the initiatives/<slug>/ skeleton.

Dry-run by default. --apply first switches to the initiative's own branch
(upstream/<slug>, created from an updated main), then writes to GitHub and to disk
(existing files are kept), then commits and pushes the branch, and opens a draft PR into
main whose `Closes #N` lines link the branch to every issue (it becomes the handoff PR).
"""
import argparse
import json
import sys
from pathlib import Path

import gh_client as gh
import git_ops
import initiative_plan as p

ROOT = Path(__file__).resolve().parents[1]


def _print_plan(plan):
    print(f"milestone: {plan['milestone']['title']}")
    for epic in plan["epics"]:
        print(f"  epic {epic['title']}  labels={','.join(epic['labels'])}")
    for h in plan["hypotheses"]:
        print(f"    hypothesis {h['title']}  -> {h['parent_layer']}")
    for path in plan["files"]:
        print(f"  file {path}")


def apply(plan, repo):
    title = plan["milestone"]["title"]
    milestone = gh.create_milestone(repo, title, plan["milestone"]["description"])
    numbers = {}
    for epic in plan["epics"]:
        numbers[epic["layer"]] = gh.create_issue_api(repo, epic["title"], epic["body"], epic["labels"], [], milestone)
        if epic["first_comment"]:
            gh.comment(repo, numbers[epic["layer"]], epic["first_comment"])
    hypotheses = []
    for h in plan["hypotheses"]:
        child = gh.create_issue_api(repo, h["title"], h["body"], h["labels"], [], milestone)
        gh.add_sub_issue(repo, numbers[h["parent_layer"]], child)
        hypotheses.append(child)
    numbers["hypotheses"] = hypotheses
    for rel, text in plan["files"].items():
        path = ROOT / rel
        if path.exists():
            print(f"kept existing {rel}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace("{milestone}", str(milestone)), encoding="utf-8")
    return milestone, numbers


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intake", help="path to the intake JSON")
    parser.add_argument("--repo", help="owner/name (default: current repository)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    data = json.loads(Path(args.intake).read_text(encoding="utf-8"))
    errors = p.validate_intake(data)
    if errors:
        for e in errors:
            print(f"invalid intake: {e}", file=sys.stderr)
        return 1
    plan = p.plan_initiative(data)
    if not args.apply:
        _print_plan(plan)
        return 0
    try:
        branch = git_ops.ensure_branch(data["slug"], git_ops.run_git)
    except git_ops.GitError as err:
        print(f"cannot start the initiative branch: {err}", file=sys.stderr)
        return 1
    try:
        milestone, numbers = apply(plan, args.repo or gh.current_repo())
        git_ops.commit_and_push([f"initiatives/{data['slug']}"], f"chore: intake {data['slug']}", branch,
                                git_ops.run_git)
        pr = gh.create_draft_pr(args.repo or gh.current_repo(), branch, "main", f"upstream: {data['title']}",
                                draft_pr_body(data, milestone, numbers))
    except (gh.GhError, git_ops.GitError) as err:
        print(f"initiative partially created on {branch}: {err}", file=sys.stderr)
        return 1
    print(f"created milestone #{milestone}, epics {numbers}, branch {branch} pushed, draft PR {pr}")
    return 0


def draft_pr_body(data, milestone, numbers):
    issues = [numbers[k] for k in ("B", "U", "S", "PRD") if k in numbers] + numbers.get("hypotheses", [])
    return (f"Upstream for **{data['title']}** (milestone #{milestone}).\n\n"
            f"> {data['demand']}\n\n"
            "Draft until handoff: the final PRD review happens here, and merging it closes the upstream.\n\n"
            + "\n".join(f"Closes #{n}" for n in issues) + "\n")


if __name__ == "__main__":
    sys.exit(main())
