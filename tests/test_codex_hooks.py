import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import codex_hooks as h  # noqa: E402
from fixtures import by_number, usual_basket  # noqa: E402


def bash(command):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}


class ParseLabelEdits(unittest.TestCase):
    def test_add_label_forms(self):
        self.assertEqual(h.label_edits("gh issue edit 3 --add-label state:done"), [(3, ["state:done"], [])])
        self.assertEqual(h.label_edits('gh issue edit 3 --add-label "state:done,epic" --remove-label state:ready'),
                         [(3, ["state:done", "epic"], ["state:ready"])])

    def test_quoted_semicolon_in_body_is_still_seen(self):
        self.assertEqual(h.label_edits('gh issue edit 3 --add-label state:done --body "Done; all good"'),
                         [(3, ["state:done"], [])])

    def test_repo_flag_before_number(self):
        self.assertEqual(h.label_edits("gh issue edit --repo o/r 3 --add-label state:done"),
                         [(3, ["state:done"], [])])

    def test_chained_commands(self):
        self.assertEqual(h.label_edits("echo hi && gh issue edit 4 --remove-label hyp:open; ls"),
                         [(4, [], ["hyp:open"])])

    def test_ignores_other_commands(self):
        self.assertEqual(h.label_edits("gh issue view 3"), [])
        self.assertEqual(h.label_edits("echo gh issue edit"), [])


class PreToolUse(unittest.TestCase):
    def test_agents_cannot_add_human_decided(self):
        reason = h.pre_tool_use(bash("gh issue edit 8 --add-label human:decided"), load=lambda n: usual_basket())
        self.assertIn("human:decided", reason)

    def test_blocks_done_with_open_hypothesis(self):
        reason = h.pre_tool_use(bash("gh issue edit 3 --add-label state:done --remove-label state:ready"),
                                load=lambda n: usual_basket())
        self.assertIn("check 10", reason)

    def test_allows_valid_change(self):
        reason = h.pre_tool_use(bash("gh issue edit 3 --add-label state:in-progress --remove-label state:ready"),
                                load=lambda n: usual_basket())
        self.assertIsNone(reason)

    def test_only_new_errors_block(self):
        snap = usual_basket()
        by_number(snap, 1)["labels"].append("state:in-progress")  # pre-existing check-3 error
        reason = h.pre_tool_use(bash("gh issue edit 2 --add-label state:in-progress --remove-label state:ready"),
                                load=lambda n: snap)
        self.assertIsNone(reason)

    def test_non_bash_tools_pass(self):
        self.assertIsNone(h.pre_tool_use({"tool_name": "Edit", "tool_input": {}}, load=lambda n: usual_basket()))

    def test_unknown_issue_passes(self):
        self.assertIsNone(h.pre_tool_use(bash("gh issue edit 999 --add-label state:done"), load=lambda n: usual_basket()))


class Stop(unittest.TestCase):
    def test_blocks_on_drift(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"].append({"author": "agent", "body": "## Answer U-02 · x", "created_at": "Z"})
        self.assertIn("U-02", h.stop({"stop_hook_active": False}, snapshots=[snap]))

    def test_does_not_loop(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"].append({"author": "agent", "body": "## Answer U-02 · x", "created_at": "Z"})
        self.assertIsNone(h.stop({"stop_hook_active": True}, snapshots=[snap]))

    def test_uncommitted_initiative_work_blocks_once(self):
        reason = h.stop({"stop_hook_active": False}, snapshots=[usual_basket()],
                        uncommitted="?? initiatives/x/business/answers/B-01.md")
        self.assertIn("checkpoint", reason)
        self.assertIsNone(h.stop({"stop_hook_active": True}, snapshots=[usual_basket()],
                                 uncommitted="?? initiatives/x/business/answers/B-01.md"))

    def test_clean_passes(self):
        self.assertIsNone(h.stop({"stop_hook_active": False}, snapshots=[usual_basket()]))


if __name__ == "__main__":
    unittest.main()
