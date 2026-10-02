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
import github_snapshot  # noqa: E402
import initiative_plan  # noqa: E402

EXAMPLE = ROOT / "templates" / "intake.example.json"


class FakeGh:
    """Records gh commands and answers the few whose output the scripts parse."""

    def __init__(self):
        self.calls, self.next_issue = [], 100

    def __call__(self, cmd):
        self.calls.append(cmd)
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/milestones"):
            return json.dumps({"number": 7})
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
        creates = [c for c in fake.calls if c[:3] == ["gh", "issue", "create"]]
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
        with mock.patch.object(gh_client, "run", boom), redirect_stderr(err):
            self.assertEqual(create_initiative.main([str(EXAMPLE), "--apply", "--repo", "o/r"]), 1)
        self.assertIn("partially created", err.getvalue())


class GhClient(unittest.TestCase):
    def test_run_raises_on_failure(self):
        failed = mock.Mock(returncode=1, stdout="", stderr="bad")
        with mock.patch("subprocess.run", return_value=failed):
            with self.assertRaises(gh_client.GhError):
                gh_client.run(["gh", "x"])

    def test_create_issue_passes_labels_as_arguments(self):
        fake = FakeGh()
        with mock.patch.object(gh_client, "run", fake):
            n = gh_client.create_issue("o/r", "t; rm -rf /", "b", ["epic", "layer:user"], "M")
        self.assertEqual(n, 101)
        self.assertIn("t; rm -rf /", fake.calls[0])
        self.assertEqual(fake.calls[0].count("--label"), 2)


class DecideMain(unittest.TestCase):
    def test_event_file_drives_gh_commands(self):
        event = {"comment": {"user": {"login": "junior-pm"}, "body": "/decide D-001 A", "html_url": "u",
                             "author_association": "COLLABORATOR"},
                 "issue": {"number": 1, "title": "B · Business problem", "labels": [{"name": "epic"}], "assignees": []}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(event, f)
        fake = FakeGh()
        with mock.patch.object(gh_client, "run", fake):
            self.assertEqual(decide_action.main(["decide_action.py", f.name]), 0)
        edits = [c for c in fake.calls if c[:3] == ["gh", "issue", "edit"]]
        self.assertEqual(edits, [["gh", "issue", "edit", "8", "--remove-label", "human:pending"],
                                 ["gh", "issue", "edit", "8", "--add-label", "human:decided"]])


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
