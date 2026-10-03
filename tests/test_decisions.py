"""Decisions live inside the issue that requested them: a request comment, the PM's
/decide comment and the agent's record comment, in that order, on the same issue."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import decisions as d  # noqa: E402
from fixtures import PM, T0, T1, T2, T3, comment  # noqa: E402

REQ1 = ("## Decision request D-001 · B-01 · Which outcome do we serve first?\n\n"
        "- **A** — Conversion against the App · trade-offs: x · reversibility: easy\n"
        "- **B** — Cost per order · trade-offs: y · reversibility: easy\n")
REQ2 = ("## Decision request D-002 · B-03 · Which success metric?\n\n"
        "- **A** — Repurchase conversion · trade-offs: x · reversibility: easy\n"
        "- **B** — Time to order · trade-offs: y · reversibility: easy\n")


def epic(comments, assignees=(PM,)):
    return {"number": 1, "title": "B · Business problem", "labels": ["epic"], "assignees": list(assignees),
            "comments": list(comments)}


class Requests(unittest.TestCase):
    def test_parses_request_with_options(self):
        reqs = d.requests(epic([comment("agent", REQ1, T0)]))
        self.assertEqual(list(reqs), ["D-001"])
        self.assertEqual(reqs["D-001"]["ref"], "B-01")
        self.assertEqual(reqs["D-001"]["options"], {"A": "Conversion against the App", "B": "Cost per order"})

    def test_record_closes_a_request(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A", T1),
                      comment("agent", "## Decision D-001 · B-01 · Conversion against the App", T2)])
        self.assertEqual(d.open_requests(issue), [])
        self.assertEqual(d.awaiting_pm(issue), [])


class Decides(unittest.TestCase):
    def test_bare_decide_counts_when_one_is_waiting(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A\nWhy: biggest gap", T1)])
        self.assertEqual(d.pm_decision(issue, "D-001"),
                         {"author": PM, "choice": "A", "why": "biggest gap", "created_at": T1})
        self.assertEqual(d.awaiting_pm(issue), [])
        self.assertEqual(d.decided_unrecorded(issue), ["D-001"])

    def test_bare_decide_is_ambiguous_with_two_waiting(self):
        issue = epic([comment("agent", REQ1, T0), comment("agent", REQ2, T0), comment(PM, "/decide A", T1)])
        self.assertIsNone(d.pm_decision(issue, "D-001"))
        self.assertEqual(d.awaiting_pm(issue), ["D-001", "D-002"])

    def test_targeted_decide(self):
        issue = epic([comment("agent", REQ1, T0), comment("agent", REQ2, T0), comment(PM, "/decide D-002 B", T1)])
        self.assertEqual(d.pm_decision(issue, "D-002")["choice"], "B")
        self.assertEqual(d.awaiting_pm(issue), ["D-001"])

    def test_non_assignee_and_decide_before_request_do_not_count(self):
        issue = epic([comment(PM, "/decide A", T0), comment("agent", REQ1, T1), comment("someone", "/decide A", T2)])
        self.assertIsNone(d.pm_decision(issue, "D-001"))

    def test_invalid_choice_does_not_count(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide C", T1)])
        self.assertIsNone(d.pm_decision(issue, "D-001"))

    def test_other_choice(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide other: recurrence first", T1)])
        self.assertEqual(d.answer_text(issue, "D-001", d.pm_decision(issue, "D-001")["choice"]), "recurrence first")

    def test_bare_decide_after_first_record_targets_the_remaining_one(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide D-001 A", T1),
                      comment("agent", "## Decision D-001 · B-01 · Conversion against the App", T2),
                      comment("agent", REQ2, T2), comment(PM, "/decide B", T3)])
        self.assertEqual(d.pm_decision(issue, "D-002")["choice"], "B")


class SeveralAtOnce(unittest.TestCase):
    """Like Apollo: the PM can answer several decisions in one comment, one line each."""

    def test_two_named_decisions_in_one_comment(self):
        issue = epic([comment("agent", REQ1, T0), comment("agent", REQ2, T0),
                      comment(PM, "/decide D-001 A\nWhy: conversion first\n/decide D-002 B\nWhy: time matters", T1)])
        self.assertEqual(d.pm_decision(issue, "D-001")["why"], "conversion first")
        self.assertEqual(d.pm_decision(issue, "D-002")["choice"], "B")
        self.assertEqual(d.pm_decision(issue, "D-002")["why"], "time matters")
        self.assertEqual(d.awaiting_pm(issue), [])

    def test_bare_decide_is_not_valid_among_several_lines(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A\n/decide D-009 B", T1)])
        self.assertIsNone(d.pm_decision(issue, "D-001"))

    def test_record_names_who_decided_in_apollo_style(self):
        rec = "## Decision D-001 · B-01 · Conversion\n\nDecision (@junior-pm, 2026-10-03, recorded by Enceladus) — **D-001 → A: x.**"
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A", T1), comment("agent", rec, T2)])
        self.assertEqual(d.recorded_by(issue, "D-001"), "junior-pm")


class AgentComments(unittest.TestCase):
    def test_agent_comment_with_decide_line_never_counts(self):
        """Agents use the PM's account: a request quoting `/decide A` must not decide itself."""
        req = REQ1 + "\n/decide A\n"
        issue = epic([comment(PM, req, T0)])
        self.assertTrue(d.is_agent_comment(issue["comments"][0]))
        self.assertEqual(d.awaiting_pm(issue), ["D-001"])


class Signature(unittest.TestCase):
    def test_invisible_enceladus_marker_marks_an_agent_comment(self):
        body = "Recurrence is option C" + d.c.signature("orchestrator")
        self.assertEqual(body, "Recurrence is option C\n<!-- enceladus:orchestrator -->")
        self.assertTrue(d.is_agent_comment(comment(PM, body, T1)))

    def test_quoting_an_agent_comment_keeps_the_pm_a_pm(self):
        quoted = "> Recurrence is option C\n> <!-- enceladus:orchestrator -->\n\n/decide A"
        issue = epic([comment("agent", REQ1, T0), comment(PM, quoted, T1)])
        self.assertFalse(d.is_agent_comment(issue["comments"][1]))
        self.assertEqual(d.pm_decision(issue, "D-001")["choice"], "A")

    def test_relayed_decision_counts_as_the_pm(self):
        relayed = "/decide A\nWhy: typed in Codex\n" + d.c.RELAY_MARKER
        issue = epic([comment("agent", REQ1, T0), comment(PM, relayed, T1)])
        self.assertEqual(d.pm_decision(issue, "D-001")["choice"], "A")


class ExpectedLabels(unittest.TestCase):
    """One human: label at most: pending while anything waits, otherwise decided."""

    def test_new_request_after_a_decision_means_pending_only(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A", T1),
                      comment("agent", "## Decision D-001 · B-01 · Conversion\nDecided by: @junior-pm", T2),
                      comment("agent", REQ2, T3)])
        self.assertEqual(d.expected_labels(issue), {"human:pending": True, "human:decided": False,
                                                    "agent:decided": None})

    def test_all_decided_means_decided_only(self):
        issue = epic([comment("agent", REQ1, T0), comment(PM, "/decide A", T1)])
        self.assertEqual(d.expected_labels(issue)["human:pending"], False)
        self.assertEqual(d.expected_labels(issue)["human:decided"], True)

    def test_nothing_decided_means_no_human_label(self):
        self.assertEqual(d.expected_labels(epic([])), {"human:pending": False, "human:decided": False,
                                                       "agent:decided": None})

    def test_blocked_layer_needs_pending(self):
        self.assertTrue(d.expected_labels(epic([]), blocked=True)["human:pending"])


class Ids(unittest.TestCase):
    def test_all_request_ids_across_issues(self):
        snap = {"issues": [epic([comment("agent", REQ1, T0)]), dict(epic([comment("agent", REQ2, T0)]), number=2)]}
        self.assertEqual(d.open_request_ids(snap), {"D-001", "D-002"})


if __name__ == "__main__":
    unittest.main()
