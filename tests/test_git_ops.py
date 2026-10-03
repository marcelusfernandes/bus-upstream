import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import git_ops as g  # noqa: E402


class FakeGit:
    def __init__(self, current="main", dirty="", local="", remote=""):
        self.calls = []
        self.answers = {"status": dirty, "branch --show-current": current,
                        "branch --list": local, "ls-remote": remote}

    def __call__(self, args):
        self.calls.append(args)
        for key, value in self.answers.items():
            if " ".join(args).startswith(key):
                return value
        return ""


class EnsureBranch(unittest.TestCase):
    def test_creates_branch_from_updated_main(self):
        git = FakeGit()
        self.assertEqual(g.ensure_branch("usual-basket", git), "upstream/usual-basket")
        self.assertIn(["fetch", "origin", "main"], git.calls)
        self.assertIn(["switch", "-c", "upstream/usual-basket", "origin/main"], git.calls)

    def test_refuses_uncommitted_changes(self):
        with self.assertRaises(g.GitError):
            g.ensure_branch("usual-basket", FakeGit(dirty=" M AGENTS.md"))

    def test_already_on_branch_does_nothing_else(self):
        git = FakeGit(current="upstream/usual-basket")
        g.ensure_branch("usual-basket", git)
        self.assertNotIn(["fetch", "origin", "main"], git.calls)

    def test_resumes_existing_local_branch(self):
        git = FakeGit(local="  upstream/usual-basket")
        g.ensure_branch("usual-basket", git)
        self.assertIn(["switch", "upstream/usual-basket"], git.calls)

    def test_resumes_existing_remote_branch(self):
        git = FakeGit(remote="abc123\trefs/heads/upstream/usual-basket")
        g.ensure_branch("usual-basket", git)
        self.assertIn(["switch", "-c", "upstream/usual-basket", "--track", "origin/upstream/usual-basket"], git.calls)


class CommitAndPush(unittest.TestCase):
    def test_sequence(self):
        git = FakeGit(current="upstream/x")
        g.commit_and_push(["initiatives/x"], "chore: intake x", "upstream/x", git)
        self.assertEqual(git.calls, [["add", "--", "initiatives/x"], ["commit", "-m", "chore: intake x"],
                                     ["push", "-u", "origin", "upstream/x"]])

    def test_refuses_to_commit_on_main(self):
        with self.assertRaises(g.GitError):
            g.commit_and_push(["x"], "m", "main", FakeGit())


if __name__ == "__main__":
    unittest.main()
