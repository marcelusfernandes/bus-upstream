import copy
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import initiative_plan as p  # noqa: E402
import upstream_contract as c  # noqa: E402
import upstream_validate as v  # noqa: E402


def usual_basket_intake():
    return {
        "slug": "usual-basket",
        "title": "Faster repurchase flow",
        "demand": "Se o fluxo for mais rápido ele pode converter mais que o App, e o custo de interação é menor.",
        "context": "App, compared with another channel (unclear)",
        "mode": "piloted",
        "layers": {
            "B": {"statement": None, "definition": 5, "grounding": 3, "why": "outcomes named, no baseline"},
            "U": {"statement": None, "definition": 1, "grounding": 2, "why": "no user problem stated"},
            "S": {"statement": "a faster flow", "definition": 5, "grounding": 0, "why": "articulated, ungrounded"},
        },
        "hypotheses": [
            {"id": "H-01", "statement": "a faster flow", "kind": "solution", "origin": "business demand",
             "basis": "intake", "raised_at": "B", "routed_to": "S"},
            {"id": "H-02", "statement": "if it is faster, it converts more than the App", "kind": "causal",
             "origin": "business demand", "basis": "intake", "raised_at": "B", "routed_to": "U"},
        ],
    }


class Validation(unittest.TestCase):
    def test_valid_intake_has_no_errors(self):
        self.assertEqual(p.validate_intake(usual_basket_intake()), [])

    def test_bad_slug(self):
        data = usual_basket_intake()
        data["slug"] = "Usual Basket"
        self.assertTrue(any("slug" in e for e in p.validate_intake(data)))

    def test_score_out_of_range(self):
        data = usual_basket_intake()
        data["layers"]["B"]["grounding"] = 12
        self.assertTrue(any("grounding" in e for e in p.validate_intake(data)))

    def test_missing_layer(self):
        data = usual_basket_intake()
        del data["layers"]["U"]
        self.assertTrue(any("U" in e for e in p.validate_intake(data)))

    def test_agent_hypothesis_needs_basis(self):
        data = usual_basket_intake()
        data["hypotheses"].append({"id": "H-03", "statement": "x", "kind": "user-problem", "origin": "agent",
                                   "basis": "", "raised_at": "U", "routed_to": "U"})
        self.assertTrue(any("basis" in e for e in p.validate_intake(data)))

    def test_bad_hypothesis_id_and_duplicates(self):
        data = usual_basket_intake()
        data["hypotheses"][1]["id"] = "H-01"
        data["hypotheses"].append(dict(data["hypotheses"][0], id="H1"))
        errors = p.validate_intake(data)
        self.assertTrue(any("duplicate" in e for e in errors))
        self.assertTrue(any("H1" in e for e in errors))

    def test_cited_evidence_must_be_recorded(self):
        data = usual_basket_intake()
        data["layers"]["B"]["why"] = "E-002 names the outcomes"
        self.assertTrue(any("E-002" in e for e in p.validate_intake(data)))
        data["evidence"] = [{"id": "E-002", "layer": "B", "kind": "decision", "claim": "outcomes", "source": "PM"}]
        self.assertEqual(p.validate_intake(data), [])
        data["evidence"].append({"id": "E-009", "layer": "U", "kind": "fact", "claim": "x", "source": "y"})
        self.assertTrue(any("E-009" in e for e in p.validate_intake(data)))

    def test_multi_sentence_statement_rejected(self):
        data = usual_basket_intake()
        data["layers"]["S"]["statement"] = "A faster flow. Also a new button."
        self.assertTrue(any("one sentence" in e for e in p.validate_intake(data)))


class ExampleTemplate(unittest.TestCase):
    def test_intake_example_is_valid_and_plans_cleanly(self):
        import json
        data = json.loads((ROOT / "templates" / "intake.example.json").read_text(encoding="utf-8"))
        self.assertEqual(p.validate_intake(data), [])
        snap = p.plan_to_snapshot(p.plan_initiative(data))
        self.assertEqual(v.validate_snapshot(snap) + v.validate_files_and_comments(snap), [])


class Plan(unittest.TestCase):
    def setUp(self):
        self.plan = p.plan_initiative(usual_basket_intake())

    def test_milestone_holds_literal_demand(self):
        self.assertIn(usual_basket_intake()["demand"], self.plan["milestone"]["description"])

    def test_four_epics_with_layer_state_mode_labels(self):
        layers = [e["layer"] for e in self.plan["epics"]]
        self.assertEqual(layers, ["B", "U", "S", "PRD"])
        for epic in self.plan["epics"]:
            self.assertIn("epic", epic["labels"])
            self.assertIn("state:ready", epic["labels"])
            self.assertIn("mode:piloted", epic["labels"])

    def test_layer_epics_have_header_and_first_score_comment(self):
        for epic in self.plan["epics"][:3]:
            self.assertRegex(epic["body"], re.compile(c.SCORE_HEADER, re.MULTILINE))
            self.assertRegex(epic["first_comment"], re.compile(c.SCORE_TITLE, re.MULTILINE))
        self.assertIsNone(self.plan["epics"][3]["first_comment"])

    def test_hypotheses_routed_to_parent_layer(self):
        routed = {h["id"]: h["parent_layer"] for h in self.plan["hypotheses"]}
        self.assertEqual(routed, {"H-01": "S", "H-02": "U"})
        for h in self.plan["hypotheses"]:
            self.assertIn("type:hypothesis", h["labels"])
            self.assertIn("hyp:open", h["labels"])

    def test_files_skeleton(self):
        files = self.plan["files"]
        for path in ("README.md", "intake.md", "hypotheses.md", "learnings.md",
                     "business/README.md", "user/README.md", "solution/README.md", "prd/README.md"):
            self.assertIn(f"initiatives/usual-basket/{path}", files)

    def test_plan_passes_validator_when_turned_into_a_snapshot(self):
        snap = p.plan_to_snapshot(self.plan)
        self.assertEqual(v.validate_snapshot(snap), [])
        self.assertEqual(v.validate_files_and_comments(snap), [])

    def test_plan_does_not_mutate_input(self):
        data = usual_basket_intake()
        before = copy.deepcopy(data)
        p.plan_initiative(data)
        self.assertEqual(data, before)


if __name__ == "__main__":
    unittest.main()
