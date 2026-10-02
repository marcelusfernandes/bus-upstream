import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import decide_action as d  # noqa: E402

PM = "junior-pm"


def decision(number=8, labels=("type:decision", "human:pending"), assignees=(PM,), title="D-001 · outcome"):
    return {"number": number, "title": title, "labels": list(labels), "assignees": list(assignees)}


def epic():
    return {"number": 1, "title": "B · Business problem", "labels": ["epic", "layer:business"], "assignees": []}


def comment(body, author=PM):
    return {"author": author, "body": body, "url": "https://github.com/o/r/issues/8#c1"}


def kinds(actions):
    return [a["kind"] for a in actions]


class Parse(unittest.TestCase):
    def test_finds_command_on_any_line(self):
        self.assertEqual(d.parse_decide("thanks\n/decide B\nWhy: cost"), (None, "B"))

    def test_target_and_other(self):
        self.assertEqual(d.parse_decide("/decide D-004 other: start with cost"), ("D-004", "other: start with cost"))

    def test_no_command(self):
        self.assertIsNone(d.parse_decide("what about option C?"))

    def test_crlf(self):
        self.assertEqual(d.parse_decide("/decide A\r\nWhy: x"), (None, "A"))


class Plan(unittest.TestCase):
    def test_no_command_does_nothing(self):
        self.assertEqual(d.plan(comment("can you clarify?"), decision(), lambda _: None), [])

    def test_assignee_decides_on_decision_issue(self):
        actions = d.plan(comment("/decide A"), decision(), lambda _: None)
        self.assertEqual(kinds(actions), ["remove_label", "add_label", "comment"])
        self.assertEqual(actions[0]["label"], "human:pending")
        self.assertEqual(actions[1]["label"], "human:decided")
        self.assertTrue(all(a["issue"] == 8 for a in actions))

    def test_never_closes_the_issue(self):
        actions = d.plan(comment("/decide A"), decision(), lambda _: None)
        self.assertNotIn("close", kinds(actions))

    def test_targeted_decide_from_another_issue(self):
        target = decision()
        actions = d.plan(comment("/decide D-001 B"), epic(), lambda did: target if did == "D-001" else None)
        self.assertEqual(kinds(actions), ["remove_label", "add_label", "comment", "comment"])
        self.assertEqual(actions[3]["issue"], 1)

    def test_bare_decide_on_non_decision_issue_replies(self):
        actions = d.plan(comment("/decide A"), epic(), lambda _: None)
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("not a decision", actions[0]["body"])

    def test_unknown_target_replies(self):
        actions = d.plan(comment("/decide D-099 A"), epic(), lambda _: None)
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("D-099", actions[0]["body"])

    def test_non_assignee_is_refused_without_echoing_body(self):
        actions = d.plan(comment("/decide other: ping @everyone", author="stranger"), decision(), lambda _: None)
        self.assertEqual(kinds(actions), ["comment"])
        self.assertIn("@junior-pm", actions[0]["body"])
        self.assertNotIn("@everyone", actions[0]["body"])

    def test_already_decided_is_refused(self):
        for label in ("human:decided", "agent:decided"):
            actions = d.plan(comment("/decide A"), decision(labels=("type:decision", label)), lambda _: None)
            self.assertEqual(kinds(actions), ["comment"])

    def test_not_pending_is_refused(self):
        actions = d.plan(comment("/decide A"), decision(labels=("type:decision",)), lambda _: None)
        self.assertEqual(kinds(actions), ["comment"])

    def test_malformed_command_is_ignored(self):
        self.assertEqual(d.plan(comment("/decide A @everyone"), decision(), lambda _: None), [])

    def test_outsiders_are_ignored_silently(self):
        for association in ("NONE", "FIRST_TIME_CONTRIBUTOR", "CONTRIBUTOR"):
            c = dict(comment("/decide A", author="stranger"), association=association)
            self.assertEqual(d.plan(c, decision(), lambda _: None), [])

    def test_targeted_decide_on_the_decision_itself_does_not_double_post(self):
        here = decision()
        actions = d.plan(comment("/decide D-001 A"), here, lambda did: dict(here))
        self.assertEqual(kinds(actions), ["remove_label", "add_label", "comment"])

    def test_ignores_bot_comments(self):
        self.assertEqual(d.plan(comment("/decide A", author="github-actions[bot]"), decision(), lambda _: None), [])


class Commands(unittest.TestCase):
    def test_gh_commands_use_argument_lists(self):
        cmds = d.to_gh_commands([{"kind": "comment", "issue": 8, "body": "x; rm -rf /"},
                                 {"kind": "add_label", "issue": 8, "label": "human:decided"}])
        self.assertEqual(cmds[0][:4], ["gh", "issue", "comment", "8"])
        self.assertIn("x; rm -rf /", cmds[0])
        self.assertEqual(cmds[1], ["gh", "issue", "edit", "8", "--add-label", "human:decided"])


if __name__ == "__main__":
    unittest.main()
