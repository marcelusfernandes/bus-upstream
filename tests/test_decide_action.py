import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import decide_action as d  # noqa: E402

PM = "junior-pm"
REQ = ("## Decision request {id} · B-01 · Which outcome?\n\n"
       "- **A** — Conversion · trade-offs: x · reversibility: easy\n"
       "- **B** — Cost · trade-offs: y · reversibility: easy\n")


def epic(*request_ids, assignees=(PM,), extra=()):
    comments = [{"author": "agent", "body": REQ.format(id=rid), "created_at": f"2026-10-02T10:0{n}:00Z"}
                for n, rid in enumerate(request_ids)]
    return {"number": 1, "title": "B · Business problem", "labels": ["epic", "human:pending"],
            "assignees": list(assignees), "comments": comments + list(extra)}


def comment(body, author=PM, association="OWNER"):
    return {"author": author, "body": body, "url": "https://github.com/o/r/issues/1#c9", "association": association}


def kinds(actions):
    return [a["kind"] for a in actions]


class Parse(unittest.TestCase):
    def test_finds_command_on_any_line(self):
        self.assertEqual(d.parse_decide("thanks\n/decide B\nWhy: cost"), (None, "B"))

    def test_target_and_other(self):
        self.assertEqual(d.parse_decide("/decide D-004 other: start with cost"), ("D-004", "other: start with cost"))

    def test_no_command_and_crlf(self):
        self.assertIsNone(d.parse_decide("what about option C?"))
        self.assertEqual(d.parse_decide("/decide A\r\nWhy: x"), (None, "A"))


class Plan(unittest.TestCase):
    def test_no_command_does_nothing(self):
        self.assertEqual(d.plan(comment("can you clarify?"), epic("D-001")), [])

    def test_single_waiting_decision(self):
        actions = d.plan(comment("/decide A"), epic("D-001"))
        self.assertEqual(kinds(actions), ["remove_label", "add_label", "comment"])
        self.assertEqual((actions[0]["label"], actions[1]["label"]), ("human:pending", "human:decided"))
        self.assertIn("D-001 decided by @junior-pm: **A — Conversion**", actions[2]["body"])
        self.assertTrue(all(a["issue"] == 1 for a in actions))

    def test_blocked_layer_keeps_pending_after_a_decision(self):
        issue = epic("D-001")
        issue["labels"].append("state:blocked")
        self.assertEqual(kinds(d.plan(comment("/decide A"), issue)), ["comment"])

    def test_never_closes(self):
        self.assertNotIn("close", kinds(d.plan(comment("/decide A"), epic("D-001"))))

    def test_bare_decide_with_two_waiting_asks_to_name_one(self):
        actions = d.plan(comment("/decide A"), epic("D-001", "D-002"))
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("/decide D-001", actions[0]["body"])

    def test_several_decisions_in_one_comment(self):
        actions = d.plan(comment("/decide D-001 A\nWhy: x\n/decide D-002 B\nWhy: y"), epic("D-001", "D-002"))
        self.assertEqual(kinds(actions), ["remove_label", "add_label", "comment"])
        self.assertIn("D-001 decided by @junior-pm: **A — Conversion**", actions[2]["body"])
        self.assertIn("D-002 decided by @junior-pm: **B — Cost**", actions[2]["body"])

    def test_bare_line_among_several_is_refused(self):
        actions = d.plan(comment("/decide A\n/decide D-002 B"), epic("D-001", "D-002"))
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("must name each decision", actions[0]["body"])
        self.assertIn("D-002 decided", actions[0]["body"])

    def test_targeted_keeps_only_pending_while_another_waits(self):
        actions = d.plan(comment("/decide D-002 B"), epic("D-001", "D-002"))
        self.assertEqual(kinds(actions), ["comment"], "one human: label: pending stays, decided waits")

    def test_nothing_waiting(self):
        self.assertIn("No decision is waiting", d.plan(comment("/decide A"), epic())[0]["body"])

    def test_unknown_target(self):
        self.assertIn("No request for D-009", d.plan(comment("/decide D-009 A"), epic("D-001"))[0]["body"])

    def test_already_decided(self):
        issue = epic("D-001", extra=[{"author": PM, "body": "/decide A", "created_at": "2026-10-02T11:00:00Z"}])
        self.assertIn("already decided", d.plan(comment("/decide D-001 B"), issue)[0]["body"])

    def test_invalid_option(self):
        self.assertIn("options A, B", d.plan(comment("/decide C"), epic("D-001"))[0]["body"])

    def test_non_assignee_refused_without_echoing_body(self):
        actions = d.plan(comment("/decide other: ping @everyone", author="stranger"), epic("D-001"))
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("@junior-pm", actions[0]["body"])
        self.assertNotIn("@everyone", actions[0]["body"])

    def test_outsiders_and_bots_are_ignored(self):
        for association in ("NONE", "FIRST_TIME_CONTRIBUTOR", "CONTRIBUTOR"):
            self.assertEqual(d.plan(comment("/decide A", author="x", association=association), epic("D-001")), [])
        self.assertEqual(d.plan(comment("/decide A", author="github-actions[bot]"), epic("D-001")), [])

    def test_agent_comment_is_ignored_even_from_the_pm_account(self):
        self.assertEqual(d.plan(comment("## Decision request D-002 · B-03 · x\n/decide A"), epic("D-001")), [])

    def test_malformed_command_is_ignored(self):
        self.assertEqual(d.plan(comment("/decide A @everyone"), epic("D-001")), [])


class Commands(unittest.TestCase):
    def test_gh_commands_use_argument_lists(self):
        cmds = d.to_gh_commands([{"kind": "comment", "issue": 8, "body": "x; rm -rf /"},
                                 {"kind": "add_label", "issue": 8, "label": "human:decided"}])
        self.assertEqual(cmds[0][:4], ["gh", "issue", "comment", "8"])
        self.assertIn("x; rm -rf /", cmds[0])
        self.assertEqual(cmds[1], ["gh", "issue", "edit", "8", "--add-label", "human:decided"])


if __name__ == "__main__":
    unittest.main()
