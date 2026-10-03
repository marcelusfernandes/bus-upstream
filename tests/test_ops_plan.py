import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import ops_plan as o  # noqa: E402
import upstream_contract as c  # noqa: E402
import upstream_validate as v  # noqa: E402
from fixtures import PM, T0, T1, T2, by_number, comment, issue, usual_basket  # noqa: E402

SLUG = "usual-basket"
BASE = f"initiatives/{SLUG}"
README = f"# Faster repurchase flow\n\nMilestone: #7\nPM: @{PM}\nMode: piloted\n"


DRAFT_B1 = f"{BASE}/business/answers/B-01.md"


def snap_with_readme(mode="piloted"):
    snap = usual_basket()
    snap["files"][f"{BASE}/README.md"] = README.replace("piloted", mode)
    snap["files"][DRAFT_B1] = "# B-01\nState: open\nCandidates: conversion vs App; cost per order\n"
    return snap


def kinds(actions):
    return [a["kind"] for a in actions]


def apply_to_snapshot(snap, actions, now=T2):
    """Simulate the executor on the snapshot so the validator can judge the result."""
    for a in actions:
        target = next((i for i in snap["issues"] if i["number"] == a.get("issue")), None)
        if a["kind"] == "comment":
            target["comments"].append({"author": "agent", "body": a["body"], "created_at": now})
        elif a["kind"] == "edit_body":
            target["body"] = a["body"]
        elif a["kind"] == "labels":
            target["labels"] = [l for l in target["labels"] if l not in a["remove"]] + a["add"]
            target["label_events"] += [{"label": l, "action": "added", "created_at": now, "actor": "agent"}
                                       for l in a["add"]]
        elif a["kind"] == "close":
            target["state"] = "closed"
        elif a["kind"] == "write_file":
            snap["files"][a["path"]] = a["text"]
        elif a["kind"] == "create_issue":
            snap["issues"].append(issue(max(i["number"] for i in snap["issues"]) + 1, a["title"], a["labels"],
                                        a["body"], parent=a["parent"], assignees=a["assignees"]))
    return snap


class Route(unittest.TestCase):
    def test_moves_state_label(self):
        actions = o.plan_route(usual_basket(), "B", "in-progress")
        self.assertEqual(actions, [{"kind": "labels", "issue": 1, "add": ["state:in-progress"],
                                    "remove": ["state:ready"]}])

    def test_refuses_done_with_open_hypothesis(self):
        with self.assertRaises(o.OpsError):
            o.plan_route(usual_basket(), "B", "done")

    def test_refuses_review_while_decision_pending(self):
        snap = usual_basket()
        snap["issues"].append(issue(8, "D-001 · x", ["type:decision", "human:pending"], parent=1))
        with self.assertRaises(o.OpsError):
            o.plan_route(snap, "B", "in-review")

    def test_blocked_adds_human_pending_and_unblocking_removes_it(self):
        snap = usual_basket()
        actions = o.plan_route(snap, "B", "blocked")
        self.assertEqual(actions[0]["add"], ["state:blocked", "human:pending"])
        by_number(snap, 1)["labels"] = ["epic", "state:blocked", "human:pending", "mode:piloted", "layer:business"]
        actions = o.plan_route(snap, "B", "in-progress")
        self.assertEqual(sorted(actions[0]["remove"]), ["human:pending", "state:blocked"])

    def test_unknown_state(self):
        with self.assertRaises(o.OpsError):
            o.plan_route(usual_basket(), "B", "finished")


class Score(unittest.TestCase):
    def test_median_spread_header_and_comment_together(self):
        snap = usual_basket()
        actions = o.plan_score(snap, "B", [(6, 4), (7, 3), (6, 5)], why="baseline found")
        self.assertEqual(kinds(actions), ["edit_body", "comment"])
        self.assertIn("**Definition:** 6 · **Grounding:** 4 · **Spread:** 2", actions[0]["body"])
        self.assertRegex(actions[1]["body"].splitlines()[0], c.SCORE_TITLE)
        self.assertIn("Definition 5 → 6 · Grounding 3 → 4", actions[1]["body"])
        self.assertEqual(v.check_score_header(apply_to_snapshot(snap, actions)), [])

    def test_grounding_cap_when_mostly_bets(self):
        actions = o.plan_score(usual_basket(), "B", [(8, 8), (8, 9)], why="x", mostly_bets=True)
        self.assertIn("**Grounding:** 5", actions[0]["body"])

    def test_panel_must_have_two_or_three_scorers(self):
        for panel in ([(5, 5)], [(5, 5)] * 4):
            with self.assertRaises(o.OpsError):
                o.plan_score(usual_basket(), "B", panel, why="x")

    def test_rejects_out_of_range(self):
        with self.assertRaises(o.OpsError):
            o.plan_score(usual_basket(), "B", [(5, 11), (5, 5)], why="x")


class Review(unittest.TestCase):
    def test_comment_and_file_agree(self):
        snap = snap_with_readme()
        actions = o.plan_review(snap, SLUG, "B-01", "rejected", blocking="statement names a feature", return_to="B-01")
        self.assertEqual(kinds(actions), ["write_file", "comment", "commit"])
        self.assertEqual(actions[0]["path"], f"{BASE}/business/review.md")
        after = apply_to_snapshot(snap, actions)
        self.assertEqual(v.check_verdicts_match(after), [])

    def test_newest_review_goes_first_in_file(self):
        snap = snap_with_readme()
        snap["files"][f"{BASE}/business/review.md"] = "## Review · B-01 · rejected\n\nBlocking: x\n"
        actions = o.plan_review(snap, SLUG, "B-01", "approved")
        self.assertTrue(actions[0]["text"].startswith("## Review · B-01 · approved"))

    def test_review_requires_the_draft_and_commits_only_its_files(self):
        with self.assertRaises(o.OpsError):
            o.plan_review(usual_basket(), SLUG, "B-01", "approved")
        actions = o.plan_review(snap_with_readme(), SLUG, "B-01", "approved")
        self.assertEqual(actions[-1]["paths"], sorted([f"{BASE}/business/review.md", DRAFT_B1]))

    def test_fit_review_goes_to_dependent_layer(self):
        actions = o.plan_review(usual_basket(), SLUG, "BU-fit", "approved")
        self.assertEqual(actions[0]["path"], f"{BASE}/user/review.md")
        self.assertEqual(actions[1]["issue"], 2)


class Answer(unittest.TestCase):
    def _ready(self, review="approved"):
        snap = usual_basket()
        snap["files"][f"{BASE}/business/answers/B-02.md"] = "# B-02\n"
        snap["files"][f"{BASE}/business/evidence/E-004.md"] = "id: E-004\n"
        snap["files"][f"{BASE}/business/review.md"] = f"## Review · B-02 · {review}\n"
        return snap

    def test_answer_commit_is_scoped_and_may_be_empty(self):
        actions = o.plan_answer(self._ready(), SLUG, "B-02", "x", why="y", evidence=["E-004"], reasoning="r",
                                learning="l")
        self.assertEqual(actions[0]["paths"], [f"{BASE}/business/answers/B-02.md", f"{BASE}/business/evidence/E-004.md"])
        self.assertTrue(actions[0]["allow_empty"])

    def test_commit_then_comment(self):
        actions = o.plan_answer(self._ready(), SLUG, "B-02", "Conversion is 12% below the App", why="baseline",
                                evidence=["E-004"], reasoning="dashboard pull", learning="none")
        self.assertEqual(kinds(actions), ["commit", "comment"])
        self.assertEqual(v.check_commit_message(actions[0]["message"]), [])
        self.assertTrue(actions[0]["message"].startswith("B-02: Conversion is 12% below the App"))
        self.assertIn("Layer: business", actions[0]["message"])
        self.assertRegex(actions[1]["body"].splitlines()[0], c.ANSWER_TITLE)

    def test_requires_approved_review(self):
        for review_text in ("rejected", None):
            snap = self._ready(review_text or "approved")
            if review_text is None:
                del snap["files"][f"{BASE}/business/review.md"]
            with self.assertRaises(o.OpsError):
                o.plan_answer(snap, SLUG, "B-02", "x", why="y", evidence=["E-004"], reasoning="r", learning="l")

    def test_requires_answer_file_and_recorded_evidence(self):
        snap = self._ready()
        with self.assertRaises(o.OpsError):
            o.plan_answer(snap, SLUG, "B-02", "x", why="y", evidence=["E-099"], reasoning="r", learning="l")
        del snap["files"][f"{BASE}/business/answers/B-02.md"]
        with self.assertRaises(o.OpsError):
            o.plan_answer(snap, SLUG, "B-02", "x", why="y", evidence=["E-004"], reasoning="r", learning="l")

    def test_answer_must_be_a_single_line(self):
        with self.assertRaises(o.OpsError):
            o.plan_answer(self._ready(), SLUG, "B-02", "First.\nSecond.", why="y", evidence=["E-004"],
                          reasoning="r", learning="l")

    def test_decision_must_be_decided(self):
        snap = self._ready()
        snap["issues"].append(issue(8, "D-001 · x", ["type:decision", "human:pending"], parent=1))
        with self.assertRaises(o.OpsError):
            o.plan_answer(snap, SLUG, "B-02", "x", why="y", evidence=["E-004"], reasoning="r", learning="l",
                          decision="D-001")


OPTIONS = [{"key": "A", "text": "Conversion against the App", "tradeoffs": "needs channel data", "reversibility": "easy"},
           {"key": "B", "text": "Cost per order", "tradeoffs": "ignores recurrence", "reversibility": "easy"}]


class DecisionOpen(unittest.TestCase):
    def test_piloted_assigns_pm_and_waits(self):
        actions = o.plan_decision_open(snap_with_readme(), SLUG, "D-001", "B-01", "Which outcome do we serve first?",
                                       OPTIONS, recommendation="A", why="largest gap", would_change="cost data",
                                       evidence=[], blocks="B cannot be done")
        a = actions[0]
        self.assertEqual(a["kind"], "create_issue")
        self.assertEqual(a["assignees"], [PM])
        self.assertEqual(a["parent"], 1)
        self.assertIn("human:pending", a["labels"])
        self.assertTrue(a["title"].startswith("D-001 · "))
        for line in [l for l in a["body"].splitlines() if l.startswith("/decide")]:
            self.assertRegex(line, c.DECIDE_COMMAND)
        self.assertIn("**Ref:** B-01", a["body"])

    def test_autonomous_has_no_pending_label(self):
        actions = o.plan_decision_open(snap_with_readme("autonomous"), SLUG, "D-001", "B-01", "q", OPTIONS,
                                       recommendation="A", why="w", would_change="x", evidence=[], blocks="b")
        self.assertNotIn("human:pending", actions[0]["labels"])

    def test_validation(self):
        bad = [dict(options=OPTIONS[:1]), dict(recommendation="C"), dict(decision_id="D-1"), dict(ref="X-01")]
        for override in bad:
            args = dict(decision_id="D-001", ref="B-01", options=OPTIONS, recommendation="A")
            args.update(override)
            with self.assertRaises(o.OpsError):
                o.plan_decision_open(snap_with_readme(), SLUG, args["decision_id"], args["ref"], "q", args["options"],
                                     recommendation=args["recommendation"], why="w", would_change="x", evidence=[],
                                     blocks="b")

    def test_requires_the_answer_draft(self):
        snap = snap_with_readme()
        del snap["files"][DRAFT_B1]
        with self.assertRaises(o.OpsError):
            o.plan_decision_open(snap, SLUG, "D-001", "B-01", "q", OPTIONS, recommendation="A", why="w",
                                 would_change="x", evidence=[], blocks="b")

    def test_opened_decision_causes_no_drift(self):
        snap = snap_with_readme()
        actions = o.plan_decision_open(snap, SLUG, "D-001", "B-01", "q", OPTIONS, recommendation="A", why="w",
                                       would_change="x", evidence=[], blocks="b")
        after = apply_to_snapshot(snap, actions)
        self.assertEqual(v.validate_snapshot(after) + v.validate_files_and_comments(after), [])

    def test_requires_pm_in_readme(self):
        snap = usual_basket()
        snap["files"][DRAFT_B1] = "draft"
        with self.assertRaises(o.OpsError):
            o.plan_decision_open(snap, SLUG, "D-001", "B-01", "q", OPTIONS, recommendation="A", why="w",
                                 would_change="x", evidence=[], blocks="b")


class DecisionRecord(unittest.TestCase):
    def _opened(self, mode="piloted"):
        snap = snap_with_readme(mode)
        actions = o.plan_decision_open(snap, SLUG, "D-001", "B-01", "Which outcome do we serve first?", OPTIONS,
                                       recommendation="A", why="w", would_change="x", evidence=[], blocks="b")
        snap = apply_to_snapshot(snap, actions, now=T0)
        d = by_number(snap, 8)
        d["label_events"] = [{"label": l, "action": "added", "created_at": T0, "actor": "agent"} for l in d["labels"]]
        return snap, d

    def test_records_pm_choice_and_closes(self):
        snap, d = self._opened()
        d["comments"].append(comment(PM, "/decide A\nWhy: biggest gap", T1))
        d["labels"] = [l for l in d["labels"] if l != "human:pending"] + ["human:decided"]
        d["label_events"].append({"label": "human:decided", "action": "added", "created_at": T1, "actor": "bot"})
        actions = o.plan_decision_record(snap, SLUG, "D-001")
        self.assertEqual(kinds(actions), ["write_file", "comment", "close", "commit"])
        title = actions[1]["body"].splitlines()[0]
        self.assertRegex(title, c.DECISION_TITLE)
        self.assertIn("Conversion against the App", title)
        self.assertIn("biggest gap", actions[1]["body"])
        after = apply_to_snapshot(snap, actions)
        self.assertEqual(v.check_decision_authorship(after), [])

    def test_other_choice_uses_pm_text(self):
        snap, d = self._opened()
        d["comments"].append(comment(PM, "/decide other: start with recurrence", T1))
        d["labels"] = [l for l in d["labels"] if l != "human:pending"] + ["human:decided"]
        actions = o.plan_decision_record(snap, SLUG, "D-001")
        self.assertIn("start with recurrence", actions[1]["body"].splitlines()[0])

    def test_pending_cannot_be_recorded(self):
        snap, _ = self._opened()
        with self.assertRaises(o.OpsError):
            o.plan_decision_record(snap, SLUG, "D-001")

    def test_autonomous_agent_choice(self):
        snap, _ = self._opened("autonomous")
        by_number(snap, 1)["labels"] = ["epic", "state:ready", "mode:autonomous", "layer:business"]
        actions = o.plan_decision_record(snap, SLUG, "D-001", agent_choice="B", agent_why="cheaper to measure")
        self.assertIn({"kind": "labels", "issue": 8, "add": ["agent:decided"], "remove": []}, actions)
        self.assertIn("Decided by: agent", actions[2]["body"])

    def test_agent_choice_refused_in_piloted_mode(self):
        snap, _ = self._opened()
        with self.assertRaises(o.OpsError):
            o.plan_decision_record(snap, SLUG, "D-001", agent_choice="B", agent_why="x")


class HypothesisClose(unittest.TestCase):
    def test_comment_label_register_close_agree(self):
        snap = usual_basket()
        snap["files"][f"{BASE}/solution/evidence/E-007.md"] = "id: E-007\n"
        actions = o.plan_hypothesis_close(snap, SLUG, "H-01", "invalidated", why="no latency evidence",
                                          evidence=["E-007"])
        self.assertEqual(kinds(actions), ["write_file", "comment", "labels", "close", "commit"])
        after = apply_to_snapshot(snap, actions)
        self.assertEqual(v.check_no_silent_hypotheses(after), [])
        self.assertEqual(v.check_verdicts_match(after), [])
        self.assertIn("| invalidated | E-007 · no latency evidence |", actions[0]["text"])

    def test_reframed_needs_target(self):
        with self.assertRaises(o.OpsError):
            o.plan_hypothesis_close(usual_basket(), SLUG, "H-02", "reframed", why="x", evidence=[])
        actions = o.plan_hypothesis_close(usual_basket(), SLUG, "H-02", "reframed", why="x", evidence=[], into="H-04")
        self.assertRegex(actions[1]["body"].splitlines()[0], c.HYPOTHESIS_TITLE)

    def test_validated_needs_evidence(self):
        with self.assertRaises(o.OpsError):
            o.plan_hypothesis_close(usual_basket(), SLUG, "H-01", "validated", why="x", evidence=[])

    def test_unknown_or_closed_hypothesis(self):
        with self.assertRaises(o.OpsError):
            o.plan_hypothesis_close(usual_basket(), SLUG, "H-09", "parked", why="x", evidence=[])


class GoldenPath(unittest.TestCase):
    """Walks the Business layer of usual-basket through every operation. The validator
    must stay clean after each step: proof that the contracts compose."""

    def assert_clean(self, snap, step):
        errors = v.validate_snapshot(snap) + v.validate_files_and_comments(snap)
        self.assertEqual(errors, [], f"after {step}")

    def test_business_layer_end_to_end(self):
        snap = snap_with_readme()
        self.assert_clean(snap, "intake")
        snap = apply_to_snapshot(snap, o.plan_route(snap, "B", "in-progress"), now=T0)
        self.assert_clean(snap, "route")
        snap = apply_to_snapshot(snap, o.plan_decision_open(
            snap, SLUG, "D-001", "B-01", "Which outcome do we serve first?", OPTIONS, recommendation="A",
            why="largest gap", would_change="cost data", evidence=[], blocks="B1"), now=T0)
        self.assert_clean(snap, "decision-open")
        d = by_number(snap, 8)
        d["comments"].append(comment(PM, "/decide A\nWhy: it is the gap leadership tracks", T1))
        d["labels"] = [l for l in d["labels"] if l != "human:pending"] + ["human:decided"]
        d["label_events"].append({"label": "human:decided", "action": "added", "created_at": T1, "actor": "bot"})
        self.assert_clean(snap, "/decide")
        snap = apply_to_snapshot(snap, o.plan_decision_record(snap, SLUG, "D-001"))
        self.assert_clean(snap, "decision-record")
        snap["files"][f"{BASE}/business/evidence/E-002.md"] = "id: E-002\n"
        snap = apply_to_snapshot(snap, o.plan_review(snap, SLUG, "B-01", "approved"))
        self.assert_clean(snap, "review")
        snap = apply_to_snapshot(snap, o.plan_answer(
            snap, SLUG, "B-01", "The repurchase flow converts below the App", why="decided in D-001",
            evidence=["E-002"], reasoning="PM chose conversion", learning="cost is a guardrail", decision="D-001"))
        self.assert_clean(snap, "answer")
        snap = apply_to_snapshot(snap, o.plan_score(snap, "B", [(7, 4), (7, 5), (6, 4)], why="B1 decided"))
        self.assert_clean(snap, "score")
        snap = apply_to_snapshot(snap, o.plan_hypothesis_close(
            snap, SLUG, "H-03", "parked", why="AOV out of scope per D-001", evidence=[]))
        self.assert_clean(snap, "hypothesis-close")
        snap = apply_to_snapshot(snap, o.plan_route(snap, "B", "done"))
        self.assert_clean(snap, "done")
        self.assertEqual(v.check_ids_resolve(snap, final=True), [], "no orphan files at the end")


if __name__ == "__main__":
    unittest.main()
