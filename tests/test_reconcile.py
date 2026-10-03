import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import reconcile as r  # noqa: E402
from fixtures import PM, T0, T1, T2, by_number, comment, issue, usual_basket  # noqa: E402


REQUEST = ("## Decision request D-001 · B-01 · Which outcome?\n\n"
           "- **A** — Conversion · trade-offs: x · reversibility: easy\n"
           "- **B** — Cost · trade-offs: y · reversibility: easy\n")


def with_decision(snap, comments=()):
    """A decision request on the B epic (it lives in the issue that requests it), plus later comments."""
    epic = by_number(snap, 1)
    epic["assignees"] = [PM]
    epic["labels"].append("human:pending")
    epic["comments"] += [comment("agent", REQUEST, T0)] + list(comments)
    snap["files"]["initiatives/usual-basket/business/answers/B-01.md"] = "# B-01 draft\n"
    return snap


def set_state(snap, number, state):
    epic = by_number(snap, number)
    epic["labels"] = [l for l in epic["labels"] if not l.startswith("state:")] + [f"state:{state}"]


def blocked():
    snap = usual_basket()
    set_state(snap, 1, "blocked")
    epic = by_number(snap, 1)
    epic["labels"].append("human:pending")
    epic["label_events"] = [{"label": "state:blocked", "action": "added", "created_at": T1, "actor": "agent"}]
    return snap


class Facts(unittest.TestCase):
    def test_reads_state_scores_and_open_hypotheses(self):
        report = r.reconcile(usual_basket())
        self.assertEqual(report["layers"]["B"], {"issue": 1, "state": "ready", "definition": 5, "grounding": 3,
                                                 "unblock_decided": False, "open_hypotheses": ["H-03"],
                                                 "pending_decisions": [], "open_requests": []})
        self.assertEqual(report["layers"]["S"]["open_hypotheses"], ["H-01"])

    def test_clean_golden_case_has_no_obligations(self):
        self.assertEqual(r.reconcile(usual_basket())["obligations"], [])

    def test_never_recommends_a_layer_order(self):
        """The BUS process is non-linear: choosing the next layer is the orchestrator's judgment."""
        report = r.reconcile(usual_basket())
        self.assertNotIn("route", report)
        self.assertNotIn("next", " ".join(report["obligations"]).lower())

    def test_pending_decision_is_listed_per_layer(self):
        self.assertEqual(r.reconcile(with_decision(usual_basket()))["layers"]["B"]["pending_decisions"], ["D-001"])


class Obligations(unittest.TestCase):
    def test_pm_reply_without_decide_needs_answer(self):
        snap = with_decision(usual_basket(), comments=[comment(PM, "what about recurrence?", T1)])
        report = r.reconcile(snap)
        self.assertEqual(report["needs_reply"], [{"decision": "D-001", "issue": 1}])
        self.assertTrue(any("reply to the PM on D-001" in o for o in report["obligations"]))

    def test_agent_reply_after_pm_clears_needs_reply(self):
        snap = with_decision(usual_basket(), comments=[comment(PM, "what about recurrence?", T1),
                                                      comment(PM, "## Reply · D-001\nRecurrence is option C", T2)])
        self.assertEqual(r.reconcile(snap)["needs_reply"], [])

    def test_decided_but_unrecorded_must_be_recorded(self):
        snap = with_decision(usual_basket(), comments=[comment(PM, "/decide A", T1)])
        report = r.reconcile(snap)
        self.assertEqual(report["layers"]["B"]["pending_decisions"], [])
        self.assertTrue(any("record decision D-001" in o for o in report["obligations"]))

    def test_drift_is_an_obligation(self):
        snap = usual_basket()
        by_number(snap, 1)["labels"].append("state:in-progress")
        self.assertTrue(r.reconcile(snap)["obligations"][0].startswith("fix drift"))

    def test_blocked_layer_without_decision(self):
        self.assertTrue(any("B is blocked: open a decision" in o for o in r.reconcile(blocked())["obligations"]))

    def test_blocked_layer_with_pending_decision_has_no_obligation(self):
        self.assertFalse(any("blocked" in o for o in r.reconcile(with_decision(blocked()))["obligations"]))

    def test_blocked_layer_with_recorded_decision(self):
        snap = with_decision(blocked(), comments=[comment(PM, "/decide B", T1),
                                                 comment(PM, "## Decision D-001 · B-01 · Cost", T2)])
        snap["files"]["initiatives/usual-basket/decisions/D-001.md"] = "## Decision D-001 · B-01 · Cost\n"
        self.assertTrue(any("decided how to unblock" in o for o in r.reconcile(snap)["obligations"]))

    def test_autonomous_decision_waits_for_the_agent(self):
        snap = usual_basket()
        epic = by_number(snap, 1)
        epic["labels"] = ["epic", "state:in-progress", "mode:autonomous", "layer:business"]
        epic["comments"].append(comment("agent", REQUEST, T1))
        snap["files"]["initiatives/usual-basket/business/answers/B-01.md"] = "# B-01 draft\n"
        self.assertEqual(r.reconcile(snap)["agent_decide"], ["D-001"])


class Summary(unittest.TestCase):
    def test_summary_is_short_and_factual(self):
        text = r.summary(r.reconcile(usual_basket()))
        self.assertIn("B: ready · D5 G3", text)
        self.assertIn("Must do: nothing pending", text)
        self.assertLessEqual(len(text.splitlines()), 15)


if __name__ == "__main__":
    unittest.main()
