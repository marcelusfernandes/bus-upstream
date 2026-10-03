import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import upstream_validate as v  # noqa: E402
from fixtures import (PM, T0, T1, T2, T3, by_number, comment, event, header,  # noqa: E402
                      issue, usual_basket)


def checks(errors):
    return sorted({e.check for e in errors})


class GoldenCase(unittest.TestCase):
    def test_usual_basket_intake_passes_all_snapshot_checks(self):
        self.assertEqual(v.validate_snapshot(usual_basket()), [])

    def test_usual_basket_intake_passes_drift_checks(self):
        self.assertEqual(v.validate_files_and_comments(usual_basket()), [])

    def test_crlf_text_is_parsed(self):
        snap = usual_basket()
        epic = by_number(snap, 1)
        epic["body"] = header(5, 3) + "\r\nmore\r\n"
        epic["comments"] = [comment("agent", "## Score · B · Definition – → 5 · Grounding – → 3\r\nWhy: x", T0)]
        self.assertEqual(v.validate_snapshot(snap), [])


class ExclusiveFamilies(unittest.TestCase):  # check 3
    def test_two_states_on_one_issue_fail(self):
        snap = usual_basket()
        by_number(snap, 1)["labels"].append("state:in-progress")
        self.assertEqual(checks(v.validate_snapshot(snap)), [3])

    def test_different_families_combine(self):
        snap = usual_basket()
        self.assertEqual(v.check_exclusive_families(snap), [])


class BlockedNeedsHuman(unittest.TestCase):  # check 4
    def test_blocked_without_human_pending_fails(self):
        snap = usual_basket()
        epic = by_number(snap, 2)
        epic["labels"] = [l for l in epic["labels"] if not l.startswith("state:")] + ["state:blocked"]
        self.assertEqual(checks(v.validate_snapshot(snap)), [4])

    def test_blocked_with_human_pending_passes(self):
        snap = usual_basket()
        epic = by_number(snap, 2)
        epic["labels"] = [l for l in epic["labels"] if not l.startswith("state:")] + [
            "state:blocked", "human:pending"]
        self.assertEqual(v.check_blocked_needs_human(snap), [])


class NoAdvanceWhilePending(unittest.TestCase):  # check 5
    def _with_pending_decision(self):
        snap = usual_basket()
        snap["issues"].append(issue(
            8, "D-001 · Which outcome does this demand serve?",
            ["type:decision", "human:pending", "layer:business"], parent=1,
            assignees=[PM], label_events=[event("human:pending", "added", T1)]))
        return snap

    def test_state_advanced_after_pending_fails(self):
        snap = self._with_pending_decision()
        epic = by_number(snap, 1)
        epic["labels"] = ["epic", "state:in-review", "mode:piloted", "layer:business"]
        epic["label_events"] = [event("state:in-review", "added", T2)]
        self.assertEqual(checks(v.validate_snapshot(snap)), [5])

    def test_second_request_after_a_recorded_one_does_not_backdate_pending(self):
        """B1 decided and recorded, then the epic moved to in-review, then B3 was requested."""
        snap = usual_basket()
        epic = by_number(snap, 1)
        epic["assignees"] = [PM]
        epic["labels"] = ["epic", "state:in-review", "mode:piloted", "layer:business", "human:pending"]
        epic["comments"] += [comment("agent", REQUEST, T0), comment(PM, "/decide A", T0),
                             comment("agent", "## Decision D-001 · B-01 · Conversion\nDecided by: @junior-pm", T1),
                             comment("agent", REQUEST.replace("D-001", "D-002"), T3)]
        epic["label_events"] = [event("human:pending", "added", T0), event("state:in-review", "added", T2)]
        self.assertEqual(v.check_no_advance_while_pending(snap), [])

    def test_state_change_before_pending_passes(self):
        snap = self._with_pending_decision()
        epic = by_number(snap, 1)
        epic["labels"] = ["epic", "state:in-progress", "mode:piloted", "layer:business"]
        epic["label_events"] = [event("state:in-progress", "added", T0)]
        self.assertEqual(v.check_no_advance_while_pending(snap), [])


class ScoreHeader(unittest.TestCase):  # check 7
    def test_missing_header_on_layer_epic_fails(self):
        snap = usual_basket()
        by_number(snap, 1)["body"] = "no header"
        self.assertEqual(checks(v.validate_snapshot(snap)), [7])

    def test_out_of_range_fails(self):
        snap = usual_basket()
        by_number(snap, 1)["body"] = header(11, 3)
        self.assertEqual(checks(v.validate_snapshot(snap)), [7])

    def test_layer_epic_without_score_comment_fails(self):
        snap = usual_basket()
        by_number(snap, 1)["comments"] = []
        self.assertEqual(checks(v.validate_snapshot(snap)), [7])

    def test_header_must_match_latest_score_comment(self):
        snap = usual_basket()
        epic = by_number(snap, 2)
        epic["comments"] = [comment("agent", "## Score · U · Definition 1 → 4 · Grounding 2 → 3\nWhy: x", T1)]
        self.assertEqual(checks(v.validate_snapshot(snap)), [7])
        epic["body"] = header(4, 3)
        self.assertEqual(v.check_score_header(snap), [])


REQUEST = ("## Decision request D-001 · B-01 · Which outcome?\n\n"
           "- **A** — Conversion · trade-offs: x · reversibility: easy\n"
           "- **B** — Cost · trade-offs: y · reversibility: easy\n")


class DecisionAuthorship(unittest.TestCase):  # check 9
    """Decisions live in the requesting issue: request, the PM's /decide, record."""

    def _decided(self, pm_comments, assignees=(PM,)):
        snap = usual_basket()
        epic = by_number(snap, 1)
        epic["labels"].append("human:decided")
        epic["assignees"] = list(assignees)
        epic["comments"] += [comment("agent", REQUEST, T0)] + list(pm_comments)
        epic["label_events"] = [event("human:decided", "added", T2)]
        return snap

    def test_decided_without_pm_decide_fails(self):
        snap = self._decided([comment("agent", "## Decision D-001 · B-01 · Conversion", T2)])
        self.assertEqual(checks(v.validate_snapshot(snap)), [9])

    def test_decide_from_non_assignee_fails(self):
        snap = self._decided([comment("someone-else", "/decide A", T1)])
        self.assertEqual(checks(v.validate_snapshot(snap)), [9])

    def test_decide_from_assignee_before_label_passes(self):
        snap = self._decided([comment(PM, "/decide A\nWhy: cost matters most", T1)])
        self.assertEqual(v.check_decision_authorship(snap), [])

    def test_targeted_and_other_pass(self):
        for body in ("/decide D-001 B", "/decide other: start with cost per order"):
            self.assertEqual(v.check_decision_authorship(self._decided([comment(PM, body, T1)])), [])

    def test_decide_on_another_issue_does_not_count(self):
        snap = self._decided([])
        by_number(snap, 2)["comments"].append(comment(PM, "/decide D-001 A", T1))
        self.assertEqual(checks(v.validate_snapshot(snap)), [9])

    def test_every_record_needs_its_own_decide(self):
        """Two decisions on one epic: D-002's record without the PM's /decide for D-002 fails."""
        snap = self._decided([comment(PM, "/decide A", T1),
                              comment("agent", "## Decision D-001 · B-01 · Conversion\nDecided by: @junior-pm (/decide A)", T2),
                              comment("agent", REQUEST.replace("D-001", "D-002"), T2),
                              comment("agent", "## Decision D-002 · B-01 · Cost\nDecided by: @junior-pm (/decide B)", T3)])
        snap["files"]["initiatives/usual-basket/decisions/D-001.md"] = "x"
        snap["files"]["initiatives/usual-basket/decisions/D-002.md"] = "x"
        snap["files"]["initiatives/usual-basket/business/answers/B-01.md"] = "x"
        errors = v.check_decision_authorship(snap)
        self.assertEqual([e.message for e in errors], ["D-002 record names @junior-pm but there is no matching /decide"])

    def test_agent_record_needs_agent_label(self):
        snap = usual_basket()
        by_number(snap, 1)["comments"] += [comment("agent", REQUEST, T0),
                                          comment("agent", "## Decision D-001 · B-01 · Cost\nDecided by: agent (autonomous mode)", T1)]
        self.assertEqual(checks(v.validate_snapshot(snap)), [9])
        by_number(snap, 1)["labels"].append("agent:decided")
        self.assertEqual(v.check_decision_authorship(snap), [])

    def test_agent_decided_needs_no_pm(self):
        snap = usual_basket()
        by_number(snap, 1)["labels"].append("agent:decided")
        self.assertEqual(v.check_decision_authorship(snap), [])


class NoSilentHypotheses(unittest.TestCase):  # check 10
    def test_done_layer_with_open_hypothesis_fails(self):
        snap = usual_basket()
        epic = by_number(snap, 3)
        epic["labels"] = ["epic", "state:done", "mode:piloted", "layer:solution"]
        self.assertEqual(checks(v.validate_snapshot(snap)), [10])

    def test_closed_hypothesis_without_reason_fails(self):
        snap = usual_basket()
        h = by_number(snap, 5)
        h["state"] = "closed"
        h["labels"] = ["type:hypothesis", "hyp:invalidated", "layer:solution"]
        self.assertEqual(checks(v.validate_snapshot(snap)), [10])

    def test_closed_hypothesis_with_status_comment_passes(self):
        snap = usual_basket()
        h = by_number(snap, 5)
        h["state"] = "closed"
        h["labels"] = ["type:hypothesis", "hyp:invalidated", "layer:solution"]
        h["comments"] = [comment("agent", "## Hypothesis H-01 · invalidated\nWhy: no latency evidence\nEvidence: E-007")]
        self.assertEqual(v.check_no_silent_hypotheses(snap), [])

    def test_closing_comment_must_agree_with_label(self):
        snap = usual_basket()
        h = by_number(snap, 5)
        h["state"] = "closed"
        h["labels"] = ["type:hypothesis", "hyp:validated", "layer:solution"]
        h["comments"] = [comment("agent", "## Hypothesis H-01 · invalidated\nWhy: x")]
        self.assertEqual(checks(v.validate_snapshot(snap)), [10])


class IdsResolve(unittest.TestCase):  # check 1
    def test_id_cited_in_comment_without_file_fails(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [comment("agent", "## Answer U-02 · Buyers rebuild baskets\nEvidence: E-005")]
        errors = v.check_ids_resolve(snap)
        self.assertEqual({e.check for e in errors}, {1})
        self.assertTrue(any("U-02" in e.message for e in errors))

    def test_id_defined_in_file_but_never_cited_fails(self):
        snap = usual_basket()
        snap["files"]["initiatives/usual-basket/user/answers/U-02.md"] = "# U-02"
        self.assertEqual(v.check_ids_resolve(snap), [])  # a draft mid-process is fine
        self.assertTrue(any("U-02" in e.message for e in v.check_ids_resolve(snap, final=True)))

    def test_id_cited_only_in_issue_body_counts(self):
        snap = usual_basket()
        snap["files"]["initiatives/usual-basket/business/evidence/E-001.md"] = "id: E-001"
        by_number(snap, 7)["body"] = "| Basis | E-001 |"
        self.assertEqual(v.check_ids_resolve(snap), [])

    def test_open_decision_request_needs_no_file_until_recorded(self):
        snap = usual_basket()
        snap["files"]["initiatives/usual-basket/business/answers/B-01.md"] = "# B-01 draft"
        by_number(snap, 1)["comments"].append(comment("agent", REQUEST, T1))
        self.assertEqual(v.check_ids_resolve(snap), [])
        by_number(snap, 1)["comments"].append(comment("agent", "## Decision D-001 · B-01 · Conversion", T2))
        self.assertTrue(any("D-001" in e.message for e in v.check_ids_resolve(snap)))

    def test_matching_ids_pass(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [comment("agent", "## Answer U-02 · Buyers rebuild baskets\nEvidence: E-005")]
        snap["files"]["initiatives/usual-basket/user/answers/U-02.md"] = "# U-02"
        snap["files"]["initiatives/usual-basket/user/evidence/E-005.md"] = "id: E-005"
        self.assertEqual(v.check_ids_resolve(snap), [])


class VerdictsMatch(unittest.TestCase):  # check 2
    def test_review_verdict_differs_from_file_fails(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [comment("agent", "## Review · U-02 · approved\nBlocking: none")]
        snap["files"]["initiatives/usual-basket/user/review.md"] = "## Review · U-02 · rejected\n"
        self.assertEqual({e.check for e in v.check_verdicts_match(snap)}, {2})

    def test_hypothesis_status_differs_from_register_fails(self):
        snap = usual_basket()
        h = by_number(snap, 5)
        h["comments"] = [comment("agent", "## Hypothesis H-01 · invalidated\nWhy: x")]
        self.assertEqual({e.check for e in v.check_verdicts_match(snap)}, {2})

    def test_rejected_then_approved_compares_latest(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [
            comment("agent", "## Review · U-02 · rejected\nBlocking: x", T1),
            comment("agent", "## Review · U-02 · approved\nBlocking: none", T2),
        ]
        snap["files"]["initiatives/usual-basket/user/review.md"] = (
            "## Review · U-02 · approved\n\n## Review · U-02 · rejected\n")
        self.assertEqual(v.check_verdicts_match(snap), [])

    def test_register_status_read_by_column_not_position(self):
        snap = usual_basket()
        h = by_number(snap, 5)
        h["comments"] = [comment("agent", "## Hypothesis H-01 · invalidated\nWhy: x")]
        snap["files"]["initiatives/usual-basket/hypotheses.md"] = snap["files"][
            "initiatives/usual-basket/hypotheses.md"].replace(
            "| S | open | — |", "| S | invalidated | E-007 contradicts |")
        self.assertEqual(v.check_verdicts_match(snap), [])

    def test_matching_verdicts_pass(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [comment("agent", "## Review · U-02 · approved\nBlocking: none")]
        snap["files"]["initiatives/usual-basket/user/review.md"] = "## Review · U-02 · approved\n"
        self.assertEqual(v.check_verdicts_match(snap), [])


class AntiLoop(unittest.TestCase):  # check 6
    def _rejections(self, between):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [
            comment("agent", "## Review · U-01 · rejected\nBlocking: no evidence", T1),
            comment("agent", between, T2),
            comment("agent", "## Review · U-01 · rejected\nBlocking: still none", T3),
        ]
        return snap

    def test_two_failures_without_new_evidence_need_blocked(self):
        snap = self._rejections("## Answer U-01 · same answer again")
        self.assertEqual({e.check for e in v.check_anti_loop(snap)}, {6})

    def test_new_evidence_between_failures_passes(self):
        snap = self._rejections("## Answer U-01 · new answer\nEvidence: E-009")
        self.assertEqual(v.check_anti_loop(snap), [])

    def test_evidence_cited_inside_a_rejection_does_not_reset(self):
        snap = usual_basket()
        by_number(snap, 2)["comments"] = [
            comment("agent", "## Review · U-01 · rejected\nBlocking: contradicted by E-020", T1),
            comment("agent", "## Review · U-01 · rejected\nBlocking: still E-021", T3),
        ]
        self.assertEqual({e.check for e in v.check_anti_loop(snap)}, {6})

    def test_blocked_with_human_satisfies_anti_loop(self):
        snap = self._rejections("## Answer U-01 · same answer again")
        epic = by_number(snap, 2)
        epic["labels"] = ["epic", "state:blocked", "human:pending", "mode:piloted", "layer:user"]
        self.assertEqual(v.check_anti_loop(snap), [])


class CommitFormat(unittest.TestCase):  # check 8
    def test_answer_commit_with_trailers_passes(self):
        msg = ("U-02: Recurring buyers rebuild the same basket manually each week\n\n"
               "Reasoning: x\nLearning: y\n\n"
               "Layer: user\nDefinition: 4 -> 7\nGrounding: 3 -> 6\nEvidence: E-005, E-007\nDecision: D-004\n")
        self.assertEqual(v.check_commit_message(msg), [])

    def test_answer_commit_without_layer_fails(self):
        msg = "U-02: Recurring buyers rebuild the same basket\n\nReasoning: x\n\nEvidence: E-005\n"
        self.assertEqual({e.check for e in v.check_commit_message(msg)}, {8})

    def test_bad_trailer_value_fails(self):
        msg = "U-02: answer\n\nLayer: user\nDefinition: four -> 7\n"
        self.assertEqual({e.check for e in v.check_commit_message(msg)}, {8})

    def test_conventional_commit_skips_trailers(self):
        self.assertEqual(v.check_commit_message("docs: add spec\n\nbody\n"), [])

    def test_unknown_title_fails(self):
        self.assertEqual({e.check for e in v.check_commit_message("did some stuff\n")}, {8})

    def test_merge_and_revert_are_allowed(self):
        self.assertEqual(v.check_commit_message("Merge branch 'main'\n"), [])
        self.assertEqual(v.check_commit_message('Revert "U-02: answer"\n'), [])


class SnapshotIsNotMutated(unittest.TestCase):
    def test_validate_does_not_mutate_input(self):
        snap = usual_basket()
        before = copy.deepcopy(snap)
        v.validate_snapshot(snap)
        v.validate_files_and_comments(snap)
        self.assertEqual(snap, before)


if __name__ == "__main__":
    unittest.main()
