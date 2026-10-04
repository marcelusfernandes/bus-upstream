#!/usr/bin/env python3
"""The only way agents write contract lines after intake (spec/v1/04, templates/README.md).

    upstream_ops.py <slug> route --layer B --state in-progress
    upstream_ops.py <slug> score --layer B --panel 6,4 7,3 6,5 --why "..." [--mostly-bets]
    upstream_ops.py <slug> review --target B-01 --verdict approved|rejected [--blocking ..] [--return-to ..]
    upstream_ops.py <slug> answer --id B-02 --text .. --why .. --reasoning .. --learning .. [--evidence E-004 ..] [--decision D-001]
    upstream_ops.py <slug> decision-open --spec decision.json
    upstream_ops.py <slug> decision-record --id D-001 [--agent-choice B --agent-why ..]
    upstream_ops.py <slug> hypothesis-close --id H-01 --status invalidated --why .. [--evidence E-007 ..] [--into H-04]
    upstream_ops.py <slug> hypothesis-add --statement .. --kind user-problem --origin .. --basis .. --raised-at U --routed-to U --test ..
    upstream_ops.py <slug> hypothesis-update --id H-01 [--test ..] [--origin ..] [--basis ..]
    upstream_ops.py <slug> fix-labels
    upstream_ops.py <slug> reply --decision D-001 --text "<options and a recommendation>"
    upstream_ops.py <slug> relay-decide --decision D-001 --choice B --why "<the PM's words, typed in Codex>"
    upstream_ops.py <slug> checkpoint --reason "<why we stop here>"
    upstream_ops.py <slug> summary --layer B

Every comment carries the invisible Enceladus marker for the role given with
--agent (default: orchestrator), except a relayed PM decision.

Add --dry-run to print the actions without executing them. Writes and commits happen
only on the initiative's own branch (upstream/<slug>).
"""
import argparse
import json
import sys
from pathlib import Path

import gh_client as gh
import git_ops
import github_snapshot
import ops_plan as o

ROOT = Path(__file__).resolve().parents[1]


def _pair(text):
    d, g = text.split(",")
    return int(d), int(g)


def _parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--repo")
    p.add_argument("--agent", default="orchestrator", help="role signed on every comment")
    sub = p.add_subparsers(dest="command", required=True)
    # --agent is accepted before or after the subcommand
    sub_add = sub.add_parser

    def add_parser(name, **kw):
        sp = sub_add(name, **kw)
        sp.add_argument("--agent", dest="agent_sub", default=None, help="role signed on every comment")
        return sp
    sub.add_parser = add_parser
    sub.add_parser("fix-labels")
    s = sub.add_parser("reply")
    s.add_argument("--decision", required=True)
    s.add_argument("--text", required=True)
    s = sub.add_parser("relay-decide")
    s.add_argument("--decision", required=True)
    s.add_argument("--choice", required=True)
    s.add_argument("--why")
    s = sub.add_parser("hypothesis-add")
    for name in ("--statement", "--kind", "--origin", "--basis", "--raised-at", "--routed-to", "--test"):
        s.add_argument(name, required=True)
    s = sub.add_parser("hypothesis-update")
    s.add_argument("--id", required=True)
    s.add_argument("--test")
    s.add_argument("--origin")
    s.add_argument("--basis")
    s = sub.add_parser("checkpoint")
    s.add_argument("--reason", required=True)
    s = sub.add_parser("summary")
    s.add_argument("--layer", required=True, choices=["B", "U", "S"])
    s = sub.add_parser("route")
    s.add_argument("--layer", required=True, choices=["B", "U", "S", "PRD"])
    s.add_argument("--state", required=True)
    s = sub.add_parser("score")
    s.add_argument("--layer", required=True, choices=["B", "U", "S"])
    s.add_argument("--panel", required=True, nargs="+", type=_pair)
    s.add_argument("--why", required=True)
    s.add_argument("--mostly-bets", action="store_true")
    s = sub.add_parser("review")
    s.add_argument("--target", required=True)
    s.add_argument("--verdict", required=True)
    s.add_argument("--blocking", default="none")
    s.add_argument("--return-to", default="none")
    s.add_argument("--limitations", help="what this review did not check")
    s = sub.add_parser("answer")
    for name in ("--id", "--text", "--why", "--reasoning", "--learning"):
        s.add_argument(name, required=True)
    s.add_argument("--evidence", nargs="*", default=[])
    s.add_argument("--decision")
    s = sub.add_parser("decision-open")
    s.add_argument("--spec", required=True, help="JSON: id, ref, question, options, recommendation, why, "
                                                 "would_change, evidence, blocks")
    s = sub.add_parser("decision-record")
    s.add_argument("--id", required=True)
    s.add_argument("--agent-choice")
    s.add_argument("--agent-why")
    s = sub.add_parser("hypothesis-close")
    s.add_argument("--id", required=True)
    s.add_argument("--status", required=True)
    s.add_argument("--why", required=True)
    s.add_argument("--evidence", nargs="*", default=[])
    s.add_argument("--into")
    return p


def plan(args, snap, repo=None):
    if args.command == "fix-labels":
        return o.plan_fix_labels(snap)
    if args.command == "reply":
        return o.plan_reply(snap, args.decision, args.text)
    if args.command == "relay-decide":
        return o.plan_relay_decide(snap, args.slug, args.decision, args.choice, args.why)
    if args.command == "hypothesis-add":
        return o.plan_hypothesis_add(snap, args.slug, args.statement, args.kind, args.origin, args.basis,
                                     args.raised_at, args.routed_to, args.test)
    if args.command == "hypothesis-update":
        fields = {k: v for k, v in (("Test", args.test), ("Origin", args.origin), ("Basis", args.basis)) if v}
        return o.plan_hypothesis_update(snap, args.slug, args.id, fields)
    if args.command == "checkpoint":
        return o.plan_checkpoint(args.slug, args.reason)
    if args.command == "summary":
        return o.plan_summary(snap, args.slug, args.layer, repo)
    if args.command == "route":
        return o.plan_route(snap, args.layer, args.state)
    if args.command == "score":
        return o.plan_score(snap, args.layer, args.panel, args.why, args.mostly_bets)
    if args.command == "review":
        return o.plan_review(snap, args.slug, args.target, args.verdict, args.blocking, args.return_to,
                             args.limitations)
    if args.command == "answer":
        return o.plan_answer(snap, args.slug, args.id, args.text, args.why, args.evidence, args.reasoning,
                             args.learning, args.decision)
    if args.command == "decision-open":
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        return o.plan_decision_open(snap, args.slug, spec["id"], spec["ref"], spec["question"], spec["options"],
                                    spec["recommendation"], spec["why"], spec["would_change"],
                                    spec.get("evidence", []), spec["blocks"], spec.get("context"))
    if args.command == "decision-record":
        return o.plan_decision_record(snap, args.slug, args.id, args.agent_choice, args.agent_why)
    return o.plan_hypothesis_close(snap, args.slug, args.id, args.status, args.why, args.evidence, args.into)


LOCAL_FIRST = {"write_file": 0, "commit": 1}


def local_first(actions):
    """Files and the commit land before any GitHub write: a git failure (for example a sandbox
    refusing .git) then leaves nothing half-applied on GitHub. GitHub writes keep their order."""
    return sorted(actions, key=lambda a: LOCAL_FIRST.get(a["kind"], 2))


def execute(actions, repo, slug, milestone, git=None):
    git = git or git_ops.run_git
    actions = local_first(actions)
    branch = git_ops.branch_name(slug)
    if any(a["kind"] in ("write_file", "commit") for a in actions):
        current = git(["branch", "--show-current"]).strip()
        if current != branch:
            raise git_ops.GitError(f"switch to {branch} first (now on {current or 'detached HEAD'})")
    for a in actions:
        kind = a["kind"]
        if kind == "comment":
            gh.comment(repo, a["issue"], a["body"])
        elif kind == "edit_body":
            gh.edit_body(repo, a["issue"], a["body"])
        elif kind == "labels":
            gh.edit_labels(repo, a["issue"], a["add"], a["remove"])
        elif kind == "assign":
            gh.add_assignees(repo, a["issue"], a["assignees"])
        elif kind == "close":
            gh.close_issue(repo, a["issue"])
        elif kind == "create_issue":
            number = gh.create_issue_api(repo, a["title"], a["body"], a["labels"], a["assignees"], milestone)
            gh.add_sub_issue(repo, a["parent"], number)
        elif kind == "write_file":
            path = ROOT / a["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(a["text"], encoding="utf-8")
        elif kind == "commit":
            if a.get("skip_if_clean") and not git(["status", "--porcelain", "--", *a["paths"]]).strip():
                continue
            git_ops.commit_and_push(a["paths"], a["message"], branch, git, a.get("allow_empty", False))


def main(argv=None, load=None):
    args = _parser().parse_args(argv)
    try:
        repo = args.repo or gh.current_repo()
        folder = ROOT / "initiatives" / args.slug
        snap = (load or github_snapshot.load_initiative)(repo, folder, ROOT)
        if snap is None:
            raise o.OpsError(f"initiatives/{args.slug} has no milestone yet")
        actions = o.sign(plan(args, snap, repo), getattr(args, "agent_sub", None) or args.agent)
        if args.dry_run:
            print(json.dumps(actions, indent=2, ensure_ascii=False))
            return 0
        readme = snap["files"].get(f"initiatives/{args.slug}/README.md", "")
        execute(actions, repo, args.slug, github_snapshot.milestone_from_readme(readme))
    except (o.OpsError, gh.GhError, git_ops.GitError, ValueError) as err:
        print(f"upstream_ops {args.command}: {err}", file=sys.stderr)
        return 1
    print(f"upstream_ops {args.command}: {len(actions)} action(s) applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
