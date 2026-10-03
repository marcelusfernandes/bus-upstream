"""Executors and CLIs with `gh` replaced by a fake: no network, no writes to GitHub."""
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

import codex_hooks  # noqa: E402
import create_initiative  # noqa: E402
import decide_action  # noqa: E402
import gh_client  # noqa: E402
import git_ops  # noqa: E402
import github_snapshot  # noqa: E402
import initiative_plan  # noqa: E402

EXAMPLE = ROOT / "templates" / "intake.example.json"


class FakeGit:
    def __init__(self, dirty=""):
        self.calls, self.dirty = [], dirty

    def __call__(self, args):
        self.calls.append(args)
        if args[0] == "status":
            return self.dirty
        if args[:2] == ["branch", "--show-current"]:
            return "main"
        return ""


class FakeGh:
    """Records gh commands and answers the few whose output the scripts parse."""

    def __init__(self):
        self.calls, self.next_issue = [], 100

    def __call__(self, cmd, stdin=None):
        self.calls.append(cmd)
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/milestones"):
            return json.dumps({"number": 7})
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/issues") and "POST" in cmd:
            self.next_issue += 1
            assert json.loads(stdin)["milestone"] == 7
            return json.dumps({"number": self.next_issue})
        if cmd[:3] == ["gh", "issue", "create"]:
            self.next_issue += 1
            return f"https://github.com/o/r/issues/{self.next_issue}\n"
        if cmd[:2] == ["gh", "api"] and "/issues/" in cmd[2] and not cmd[2].endswith("sub_issues"):
            return json.dumps({"id": 555})
        if cmd[:3] == ["gh", "repo", "view"]:
            return json.dumps({"nameWithOwner": "o/r"})
        if cmd[:3] == ["gh", "issue", "list"]:
            return json.dumps([{"number": 8, "title": "D-001 · outcome", "labels": [{"name": "type:decision"},
                               {"name": "human:pending"}], "assignees": [{"login": "junior-pm"}]}])
        return ""


class CreateInitiative(unittest.TestCase):
    def test_dry_run_prints_plan(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(create_initiative.main([str(EXAMPLE)]), 0)
        self.assertIn("epic B · Business problem", out.getvalue())

    def test_invalid_intake_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"slug": "Bad Slug"}, f)
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(create_initiative.main([f.name]), 1)
        self.assertIn("invalid intake", err.getvalue())

    def test_apply_creates_everything_and_writes_files(self):
        fake = FakeGh()
        plan = initiative_plan.plan_initiative(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gh_client, "run", fake), \
                mock.patch.object(create_initiative, "ROOT", Path(tmp)), redirect_stdout(io.StringIO()):
            milestone, numbers = create_initiative.apply(plan, "o/r")
            readme = (Path(tmp) / "initiatives/usual-basket/README.md").read_text(encoding="utf-8")
        self.assertEqual(milestone, 7)
        self.assertEqual(set(numbers), {"B", "U", "S", "PRD"})
        self.assertIn("Milestone: #7", readme)
        creates = [c for c in fake.calls if c[:2] == ["gh", "api"] and c[2].endswith("/issues") and "POST" in c]
        self.assertEqual(len(creates), 4 + 3)
        self.assertEqual(len([c for c in fake.calls if c[2:3] and str(c[2]).endswith("sub_issues")]), 3)
        self.assertEqual(len([c for c in fake.calls if c[:3] == ["gh", "issue", "comment"]]), 3)

    def test_apply_keeps_existing_files(self):
        plan = initiative_plan.plan_initiative(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gh_client, "run", FakeGh()), \
                mock.patch.object(create_initiative, "ROOT", Path(tmp)), redirect_stdout(io.StringIO()):
            existing = Path(tmp) / "initiatives/usual-basket/learnings.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("mine", encoding="utf-8")
            create_initiative.apply(plan, "o/r")
            self.assertEqual(existing.read_text(encoding="utf-8"), "mine")

    def test_gh_error_is_reported(self):
        def boom(cmd):
            raise gh_client.GhError("nope")
        err = io.StringIO()
        with mock.patch.object(gh_client, "run", boom), mock.patch.object(git_ops, "run_git", FakeGit()), \
                redirect_stderr(err):
            self.assertEqual(create_initiative.main([str(EXAMPLE), "--apply", "--repo", "o/r"]), 1)
        self.assertIn("partially created on upstream/usual-basket", err.getvalue())

    def test_apply_switches_branch_first_then_commits_and_pushes(self):
        git = FakeGit()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gh_client, "run", FakeGh()), \
                mock.patch.object(git_ops, "run_git", git), mock.patch.object(create_initiative, "ROOT", Path(tmp)), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(create_initiative.main([str(EXAMPLE), "--apply", "--repo", "o/r"]), 0)
        self.assertIn(["switch", "-c", "upstream/usual-basket", "origin/main"], git.calls)
        self.assertEqual(git.calls[-2:], [["commit", "-m", "chore: intake usual-basket"],
                                          ["push", "-u", "origin", "upstream/usual-basket"]])

    def test_dirty_tree_stops_before_github(self):
        fake, err = FakeGh(), io.StringIO()
        with mock.patch.object(gh_client, "run", fake), mock.patch.object(git_ops, "run_git", FakeGit(dirty=" M x")), \
                redirect_stderr(err):
            self.assertEqual(create_initiative.main([str(EXAMPLE), "--apply", "--repo", "o/r"]), 1)
        self.assertEqual(fake.calls, [])
        self.assertIn("uncommitted", err.getvalue())


class GhClient(unittest.TestCase):
    def test_run_raises_on_failure(self):
        failed = mock.Mock(returncode=1, stdout="", stderr="bad")
        with mock.patch("subprocess.run", return_value=failed):
            with self.assertRaises(gh_client.GhError):
                gh_client.run(["gh", "x"])

    def test_create_issue_sends_json_not_shell(self):
        seen = {}

        def fake(cmd, stdin=None):
            seen["cmd"], seen["stdin"] = cmd, stdin
            return json.dumps({"number": 5})
        with mock.patch.object(gh_client, "run", fake):
            n = gh_client.create_issue_api("o/r", "t; rm -rf /", "b", ["epic"], ["pm"], 7)
        self.assertEqual(n, 5)
        self.assertEqual(json.loads(seen["stdin"])["title"], "t; rm -rf /")
        self.assertNotIn("t; rm -rf /", seen["cmd"])


class DecideMain(unittest.TestCase):
    def test_event_and_issue_comments_drive_gh_commands(self):
        request = ("## Decision request D-001 · B-01 · Which outcome?\n\n"
                   "- **A** — Conversion · trade-offs: x · reversibility: easy\n"
                   "- **B** — Cost · trade-offs: y · reversibility: easy\n")
        event = {"comment": {"id": 2, "user": {"login": "junior-pm"}, "body": "/decide A", "html_url": "u",
                             "author_association": "COLLABORATOR"},
                 "issue": {"number": 1, "title": "B · Business problem", "labels": [{"name": "human:pending"}],
                           "assignees": [{"login": "junior-pm"}]},
                 "repository": {"full_name": "o/r"}}
        api_comments = [{"id": 1, "user": {"login": "junior-pm"}, "body": request, "created_at": "2026-10-02T10:00:00Z"},
                        {"id": 2, "user": {"login": "junior-pm"}, "body": "/decide A", "created_at": "2026-10-02T11:00:00Z"}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(event, f)
        calls = []

        def fake(cmd, stdin=None):
            calls.append(cmd)
            return "\n".join(json.dumps(c) for c in api_comments) if cmd[:3] == ["gh", "api", "--paginate"] else ""
        with mock.patch.object(gh_client, "run", fake), mock.patch.dict("os.environ", {"GH_REPO": "o/r"}):
            self.assertEqual(decide_action.main(["decide_action.py", f.name]), 0)
        self.assertEqual(calls[0], ["gh", "api", "--paginate", "repos/o/r/issues/1/comments", "--jq", ".[]"])
        edits = [c for c in calls if c[:3] == ["gh", "issue", "edit"]]
        self.assertEqual(edits, [["gh", "issue", "edit", "1", "--remove-label", "human:pending"],
                                 ["gh", "issue", "edit", "1", "--add-label", "human:decided"]])


class HooksMain(unittest.TestCase):
    def _run(self, mode, payload):
        err, out = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))), redirect_stderr(err), redirect_stdout(out):
            code = codex_hooks.main(["codex_hooks.py", mode])
        return code, err.getvalue()

    def test_blocks_human_decided(self):
        code, err = self._run("pre-tool-use", {"tool_name": "Bash",
                                               "tool_input": {"command": "gh issue edit 1 --add-label human:decided"}})
        self.assertEqual(code, 2)
        self.assertIn("human:decided", err)

    def test_fails_open_when_github_is_unreachable(self):
        def boom(cmd):
            raise gh_client.GhError("offline")
        with mock.patch.object(gh_client, "run", boom), mock.patch.object(codex_hooks, "_initiative_dirs",
                                                                          return_value=[ROOT]):
            code, err = self._run("pre-tool-use", {"tool_name": "Bash",
                                                   "tool_input": {"command": "gh issue edit 3 --add-label state:done"}})
        self.assertEqual(code, 0)
        self.assertIn("skipped", err)

    def test_stop_without_initiatives_passes(self):
        with mock.patch.object(codex_hooks, "_initiative_dirs", return_value=[]), \
                mock.patch.object(gh_client, "run", FakeGh()):
            self.assertEqual(self._run("stop", {"stop_hook_active": False})[0], 0)

    def test_unknown_mode_is_harmless(self):
        self.assertEqual(self._run("nope", {})[0], 0)


class SnapshotLoading(unittest.TestCase):
    def test_load_initiative_reads_milestone_and_files(self):
        payload = {"data": {"repository": {"milestone": {"number": 7, "issues": {"nodes": []}}}}}
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "initiatives" / "x"
            d.mkdir(parents=True)
            (d / "README.md").write_text("# X\n\nMilestone: #7\n", encoding="utf-8")
            with mock.patch.object(gh_client, "run", return_value=json.dumps(payload)):
                snap = github_snapshot.load_initiative("o/r", d, Path(tmp))
        self.assertEqual(snap["issues"], [])
        self.assertIn("initiatives/x/README.md", snap["files"])

    def test_no_milestone_yet_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(github_snapshot.load_initiative("o/r", Path(tmp), Path(tmp)))


if __name__ == "__main__":
    unittest.main()
