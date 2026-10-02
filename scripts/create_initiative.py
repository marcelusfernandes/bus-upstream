#!/usr/bin/env python3
"""Create an initiative from an intake JSON: milestone, B/U/S/PRD epics with the
first score comments, hypothesis sub-issues, and the initiatives/<slug>/ skeleton.

Dry-run by default. --apply writes to GitHub and to disk (existing files are kept).
"""
import argparse
import json
import sys
from pathlib import Path

import gh_client as gh
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
        numbers[epic["layer"]] = gh.create_issue(repo, epic["title"], epic["body"], epic["labels"], title)
        if epic["first_comment"]:
            gh.comment(repo, numbers[epic["layer"]], epic["first_comment"])
    for h in plan["hypotheses"]:
        child = gh.create_issue(repo, h["title"], h["body"], h["labels"], title)
        gh.add_sub_issue(repo, numbers[h["parent_layer"]], child)
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
        milestone, numbers = apply(plan, args.repo or gh.current_repo())
    except gh.GhError as err:
        print(f"GitHub error, initiative partially created: {err}", file=sys.stderr)
        return 1
    print(f"created milestone #{milestone}, epics {numbers}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
