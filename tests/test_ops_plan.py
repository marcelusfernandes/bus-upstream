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
        elif a["kind"] == "assign":
            target["assignees"] = sorted(set(target.get("assignees", [])) | set(a["assignees"]))
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


def open_d001(snap):
    return o.plan_decision_open(snap, SLUG, "D-001", "B-01", "Which outcome do we serve first?", OPTIONS,
                                recommendation="A", why="largest gap", would_change="cost data", evidence=[],
                                blocks="B1")


class DecisionOpen(unittest.TestCase):
    """A decision is requested inside the issue that needs it (the layer epic), never as its own issue."""

    def test_piloted_request_in_the_epic_assigns_pm_and_waits(self):
        actions = open_d001(snap_with_readme())
        self.assertEqual(kinds(actions), ["comment", "edit_body", "assign", "labels"])
        self.assertTrue(all(a["issue"] == 1 for a in actions))
        self.assertNotIn("create_issue", kinds(actions))
        self.assertRegex(actions[0]["body"].splitlines()[0], c.DECISION_REQUEST_TITLE)
        self.assertEqual(actions[2]["assignees"], [PM])
        self.assertEqual(actions[3]["add"], ["human:pending"])
        self.assertIn("- [ ] D-001 · Which outcome do we serve first?", actions[1]["body"])
        self.assertTrue(actions[1]["body"].startswith("> **Definition:**"), "score header stays first")

    def test_second_request_shares_the_checklist_and_keeps_the_header_first(self):
        snap = snap_with_readme()
        snap = apply_to_snapshot(snap, o.plan_score(snap, "B", [(6, 4), (6, 4)], why="x"), now=T0)
        snap = apply_to_snapshot(snap, open_d001(snap), now=T0)
        snap["files"][f"{BASE}/business/answers/B-03.md"] = "# B-03 draft"
        actions = o.plan_decision_open(snap, SLUG, "D-002", "B-03", "Which success metric?", OPTIONS,
                                       recommendation="A", why="w", would_change="x", evidence=[], blocks="B3")
        body = next(a for a in actions if a["kind"] == "edit_body")["body"]
        self.assertEqual(body.count("### Decisions"), 1)
        self.assertTrue(body.startswith("> **Definition:** 6 · **Grounding:** 4"))
        self.assertIn("- [ ] D-001 · Which outcome do we serve first?\n- [ ] D-002 · Which success metric?", body)
        self.assertNotIn("labels", [a["kind"] for a in actions], "human:pending is already there")

    def test_request_never_has_a_decide_line_of_its_own(self):
        """Agents share the PM's account: a line starting with /decide would decide by itself."""
        body = open_d001(snap_with_readme())[0]["body"]
        self.assertFalse(any(line.startswith("/decide") for line in body.splitlines()))

    def test_autonomous_has_no_pending_label(self):
        actions = open_d001(snap_with_readme("autonomous"))
        self.assertNotIn("labels", kinds(actions))

    def test_validation(self):
        bad = [dict(options=OPTIONS[:1]), dict(recommendation="C"), dict(decision_id="D-1"), dict(ref="X-01")]
        for override in bad:
            args = dict(decision_id="D-001", ref="B-01", options=OPTIONS, recommendation="A")
            args.update(override)
            with self.assertRaises(o.OpsError):
                o.plan_decision_open(snap_with_readme(), SLUG, args["decision_id"], args["ref"], "q", args["options"],
                                     recommendation=args["recommendation"], why="w", would_change="x", evidence=[],
                                     blocks="b")

    def test_duplicate_id_refused(self):
        snap = apply_to_snapshot(snap_with_readme(), open_d001(snap_with_readme()))
        with self.assertRaises(o.OpsError):
            open_d001(snap)

    def test_requires_the_answer_draft(self):
        snap = snap_with_readme()
        del snap["files"][DRAFT_B1]
        with self.assertRaises(o.OpsError):
            open_d001(snap)

    def test_opened_decision_causes_no_drift(self):
        snap = snap_with_readme()
        after = apply_to_snapshot(snap, open_d001(snap), now=T0)
        self.assertEqual(v.validate_snapshot(after) + v.validate_files_and_comments(after), [])

    def test_requires_pm_in_readme(self):
        snap = usual_basket()
        snap["files"][DRAFT_B1] = "draft"
        with self.assertRaises(o.OpsError):
            open_d001(snap)


class DecisionRecord(unittest.TestCase):
    def _opened(self, mode="piloted"):
        snap = snap_with_readme(mode)
        if mode == "autonomous":
            by_number(snap, 1)["labels"] = ["epic", "state:ready", "mode:autonomous", "layer:business"]
        return apply_to_snapshot(snap, open_d001(snap), now=T0)

    def _pm_decides(self, snap, body, at=T1):
        epic = by_number(snap, 1)
        epic["comments"].append(comment(PM, body, at))
        epic["labels"] = [l for l in epic["labels"] if l != "human:pending"] + ["human:decided"]
        epic["label_events"].append({"label": "human:decided", "action": "added", "created_at": at, "actor": "bot"})
        return snap

    def test_records_in_the_same_issue_and_ticks_the_checklist(self):
        snap = self._pm_decides(self._opened(), "/decide A\nWhy: biggest gap")
        actions = o.plan_decision_record(snap, SLUG, "D-001")
        self.assertEqual(kinds(actions), ["write_file", "comment", "edit_body", "commit"])
        self.assertNotIn("close", kinds(actions))
        title = actions[1]["body"].splitlines()[0]
        self.assertRegex(title, c.DECISION_TITLE)
        self.assertIn("Conversion against the App", title)
        self.assertIn("@junior-pm (/decide A)", actions[1]["body"])
        self.assertIn("biggest gap", actions[1]["body"])
        self.assertIn("- [x] D-001 · Which outcome do we serve first? → Conversion against the App", actions[2]["body"])
        after = apply_to_snapshot(snap, actions, now=T2)
        self.assertEqual(v.validate_snapshot(after) + v.validate_files_and_comments(after), [])

    def test_other_choice_uses_pm_text(self):
        snap = self._pm_decides(self._opened(), "/decide other: start with recurrence")
        self.assertIn("start with recurrence", o.plan_decision_record(snap, SLUG, "D-001")[1]["body"].splitlines()[0])

    def test_pending_cannot_be_recorded(self):
        with self.assertRaises(o.OpsError):
            o.plan_decision_record(self._opened(), SLUG, "D-001")

    def test_autonomous_agent_choice(self):
        actions = o.plan_decision_record(self._opened("autonomous"), SLUG, "D-001", agent_choice="B",
                                         agent_why="cheaper to measure")
        self.assertEqual(actions[0], {"kind": "labels", "issue": 1, "add": ["agent:decided"], "remove": []})
        self.assertIn("Decided by: agent", actions[2]["body"])

    def test_agent_choice_refused_in_piloted_mode(self):
        with self.assertRaises(o.OpsError):
            o.plan_decision_record(self._opened(), SLUG, "D-001", agent_choice="B", agent_why="x")

    def test_unknown_or_recorded_decision(self):
        with self.assertRaises(o.OpsError):
            o.plan_decision_record(self._opened(), SLUG, "D-009")


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
        snap = apply_to_snapshot(snap, open_d001(snap), now=T0)
        self.assert_clean(snap, "decision-open")
        epic = by_number(snap, 1)
        epic["comments"].append(comment(PM, "/decide A\nWhy: it is the gap leadership tracks", T1))
        epic["labels"] = [l for l in epic["labels"] if l != "human:pending"] + ["human:decided"]
        epic["label_events"].append({"label": "human:decided", "action": "added", "created_at": T1, "actor": "bot"})
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
