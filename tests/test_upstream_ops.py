"""upstream_ops CLI with a fake gh, a fake git and an in-memory snapshot."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import gh_client  # noqa: E402
import git_ops  # noqa: E402
import upstream_ops as u  # noqa: E402
from fixtures import PM, usual_basket  # noqa: E402

README = f"# X\n\nMilestone: #7\nPM: @{PM}\nMode: piloted\n"


def loader(snap):
    snap["files"]["initiatives/usual-basket/README.md"] = README
    snap["files"]["initiatives/usual-basket/business/answers/B-01.md"] = "# B-01\nState: open\n"
    return lambda repo, folder, root: snap


class FakeGh:
    def __init__(self):
        self.calls = []

    def __call__(self, cmd, stdin=None):
        self.calls.append((cmd, stdin))
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/issues") and "POST" in cmd:
            return json.dumps({"number": 42})
        if cmd[:2] == ["gh", "api"] and "/issues/" in cmd[2] and not cmd[2].endswith("sub_issues"):
            return json.dumps({"id": 900})
        return ""


class FakeGit:
    """Models staging: a commit with nothing added since the last one fails unless --allow-empty."""

    def __init__(self, branch="upstream/usual-basket"):
        self.calls, self.branch, self.staged = [], branch, False

    def __call__(self, args):
        self.calls.append(args)
        if args[0] == "add":
            self.staged = True
        if args[0] == "commit":
            if not self.staged and "--allow-empty" not in args:
                raise git_ops.GitError("nothing to commit")
            self.staged = False
        return self.branch if args[:2] == ["branch", "--show-current"] else ""


def run(argv, snap, git=None):
    fake, git = FakeGh(), git or FakeGit()
    out, err = io.StringIO(), io.StringIO()
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gh_client, "run", fake), \
            mock.patch.object(git_ops, "run_git", git), mock.patch.object(u, "ROOT", Path(tmp)), \
            redirect_stdout(out), redirect_stderr(err):
        code = u.main(["usual-basket", "--repo", "o/r", *argv], load=loader(snap))
        written = {str(p.relative_to(tmp)): p.read_text(encoding="utf-8") for p in Path(tmp).rglob("*") if p.is_file()}
    return code, fake.calls, git.calls, written, out.getvalue() + err.getvalue()


class Cli(unittest.TestCase):
    def test_route_edits_labels_only(self):
        code, gh_calls, git_calls, _, _ = run(["route", "--layer", "B", "--state", "in-progress"], usual_basket())
        self.assertEqual(code, 0)
        self.assertEqual(gh_calls[0][0], ["gh", "issue", "edit", "1", "--repo", "o/r", "--add-label",
                                          "state:in-progress", "--remove-label", "state:ready"])
        self.assertEqual(git_calls, [])

    def test_score_edits_body_then_comments(self):
        code, gh_calls, _, _, _ = run(["score", "--layer", "B", "--panel", "6,4", "7,3", "--why", "baseline"],
                                      usual_basket())
        self.assertEqual(code, 0)
        self.assertEqual([c[0][:3] for c in gh_calls], [["gh", "issue", "edit"], ["gh", "issue", "comment"]])

    def test_review_writes_file_comments_and_commits(self):
        code, gh_calls, git_calls, written, _ = run(["review", "--target", "B-01", "--verdict", "rejected",
                                                     "--blocking", "names a feature"], usual_basket())
        self.assertEqual(code, 0)
        self.assertIn("initiatives/usual-basket/business/review.md", written)
        self.assertEqual(git_calls[-1], ["push", "-u", "origin", "upstream/usual-basket"])

    def test_local_commit_lands_before_any_github_write(self):
        order = []
        git = FakeGit()
        original = git.__call__

        def tracking_git(args):
            order.append(("git", args[0]))
            return original(args)
        fake = FakeGh()

        def tracking_gh(cmd, stdin=None):
            order.append(("gh", cmd[2]))
            return fake(cmd, stdin)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gh_client, "run", tracking_gh), \
                mock.patch.object(git_ops, "run_git", tracking_git), mock.patch.object(u, "ROOT", Path(tmp)), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = u.main(["usual-basket", "--repo", "o/r", "review", "--target", "B-01", "--verdict", "approved"],
                          load=loader(usual_basket()))
        self.assertEqual(code, 0)
        first_gh = next(n for n, (tool, _) in enumerate(order) if tool == "gh")
        self.assertLess(order.index(("git", "push")), first_gh)

    def test_writes_refused_off_the_initiative_branch(self):
        code, gh_calls, _, written, output = run(["review", "--target", "B-01", "--verdict", "approved"],
                                                 usual_basket(), git=FakeGit(branch="main"))
        self.assertEqual(code, 1)
        self.assertEqual((gh_calls, written), ([], {}))
        self.assertIn("switch to upstream/usual-basket", output)

    def test_decision_open_comments_in_the_epic_and_assigns_the_pm(self):
        spec = {"id": "D-001", "ref": "B-01", "question": "Which outcome first?",
                "options": [{"key": "A", "text": "Conversion"}, {"key": "B", "text": "Cost"}],
                "recommendation": "A", "why": "largest gap", "would_change": "cost data", "blocks": "B",
                "context": "Two outcomes named, no baseline yet."}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
        code, gh_calls, git_calls, _, _ = run(["decision-open", "--spec", f.name], usual_basket())
        self.assertEqual(code, 0)
        cmds = [c[0] for c in gh_calls]
        self.assertEqual(cmds[0][:4], ["gh", "issue", "comment", "1"])
        self.assertIn("## Decision request D-001 · B-01 · Which outcome first?", cmds[0][-1])
        self.assertIn(["gh", "issue", "edit", "1", "--repo", "o/r", "--add-assignee", PM], cmds)
        self.assertIn(["gh", "issue", "edit", "1", "--repo", "o/r", "--add-label", "human:pending"], cmds)
        self.assertFalse(any("POST" in c for c in cmds), "no separate decision issue")
        self.assertEqual(git_calls, [])

    def test_comments_are_signed_with_the_agent_role(self):
        code, gh_calls, _, _, _ = run(["--agent", "business_lead", "hypothesis-close", "--id", "H-01", "--status",
                                       "parked", "--why", "out of scope"], usual_basket())
        self.assertEqual(code, 0)
        comment_cmd = next(c[0] for c in gh_calls if c[0][:3] == ["gh", "issue", "comment"])
        self.assertTrue(comment_cmd[-1].endswith("<!-- enceladus:business_lead -->"))

    def test_agent_flag_works_after_the_subcommand(self):
        code, gh_calls, _, _, _ = run(["hypothesis-close", "--agent", "business_lead", "--id", "H-01", "--status",
                                       "parked", "--why", "out of scope"], usual_basket())
        self.assertEqual(code, 0)
        comment_cmd = next(c[0] for c in gh_calls if c[0][:3] == ["gh", "issue", "comment"])
        self.assertTrue(comment_cmd[-1].endswith("<!-- enceladus:business_lead -->"))

    def test_checkpoint_skips_when_clean(self):
        code, _, git_calls, _, _ = run(["checkpoint", "--reason", "waiting for D-002"], usual_basket())
        self.assertEqual(code, 0)
        self.assertNotIn("commit", [c[0] for c in git_calls])

    def test_rule_violation_is_reported_without_writes(self):
        code, gh_calls, _, _, output = run(["route", "--layer", "B", "--state", "done"], usual_basket())
        self.assertEqual((code, gh_calls), (1, []))
        self.assertIn("open hypotheses", output)

    def test_dry_run_prints_actions(self):
        code, gh_calls, _, _, output = run(["--dry-run", "hypothesis-close", "--id", "H-01", "--status", "parked",
                                            "--why", "out of scope"], usual_basket())
        self.assertEqual((code, gh_calls), (0, []))
        self.assertIn("## Hypothesis H-01 · parked", output)

    def test_hypothesis_close_and_decision_record_paths(self):
        code, _, git_calls, written, _ = run(["hypothesis-close", "--id", "H-01", "--status", "parked",
                                              "--why", "out of scope"], usual_basket())
        self.assertEqual(code, 0)
        self.assertIn("| parked |", written["initiatives/usual-basket/hypotheses.md"])
        code, _, _, _, output = run(["decision-record", "--id", "D-009"], usual_basket())
        self.assertEqual(code, 1)

    def test_answer_requires_review(self):
        snap = usual_basket()
        snap["files"]["initiatives/usual-basket/business/answers/B-02.md"] = "x"
        code, _, _, _, output = run(["answer", "--id", "B-02", "--text", "t", "--why", "w", "--reasoning", "r",
                                     "--learning", "l"], snap)
        self.assertEqual(code, 1)
        self.assertIn("approved review", output)


if __name__ == "__main__":
    unittest.main()
