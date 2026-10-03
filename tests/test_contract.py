"""Ties the human-readable templates to the machine contract.

Every example line in templates/ must match the regex the validator uses, so the
templates and the validator cannot drift apart silently.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import upstream_contract as c  # noqa: E402


def lines_starting(path, prefix):
    text = (ROOT / "templates" / path).read_text(encoding="utf-8")
    return [l for l in text.splitlines() if l.startswith(prefix)]


class TemplatesMatchContract(unittest.TestCase):
    def assert_all_match(self, pattern, lines):
        self.assertTrue(lines, "template has no example lines")
        for line in lines:
            self.assertRegex(line, pattern)

    def test_epic_body_header(self):
        self.assert_all_match(c.SCORE_HEADER, lines_starting("epic-body.md", "> **Definition:**"))

    def test_comment_titles(self):
        titles = lines_starting("comments.md", "## ")
        kinds = {
            "## Decision request": c.DECISION_REQUEST_TITLE,
            "## Answer": c.ANSWER_TITLE,
            "## Score": c.SCORE_TITLE,
            "## Review": c.REVIEW_TITLE,
            "## Reopened": c.REOPEN_TITLE,
            "## Decision": c.DECISION_TITLE,
            "## Hypothesis": c.HYPOTHESIS_TITLE,
        }
        seen = set()
        for title in titles:
            for prefix in sorted(kinds, key=len, reverse=True):  # "## Decision request" before "## Decision"
                if title.startswith(prefix + " "):
                    self.assertRegex(title, kinds[prefix])
                    seen.add(prefix)
                    break
        self.assertEqual(seen, set(kinds))

    def test_decision_request_template(self):
        self.assert_all_match(c.DECISION_REQUEST_TITLE, lines_starting("decision-request.md", "## Decision request"))

    def test_review_file_example(self):
        self.assert_all_match(c.REVIEW_TITLE, lines_starting("review-file.md", "## Review"))

    def test_register_has_status_column_and_valid_ids(self):
        rows = lines_starting("hypotheses-register.md", "| ")
        header = [x.strip() for x in rows[0].strip("|").split("|")]
        self.assertIn("Status", header)
        for row in rows[2:]:
            self.assertRegex(row, r"^\| " + c.HYPOTHESIS_ID + r" \|")

    def test_answer_template_has_the_summary_lines(self):
        text = (ROOT / "templates" / "answer.md").read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(rf"^# {c.ANSWER_ID} · .+$", re.M))
        self.assertRegex(text, re.compile(r"^\*\*Answer:\*\* .+$", re.M))
        self.assertRegex(text, re.compile(r"^\*\*State:\*\* (evidenced|bet|open)$", re.M))

    def test_decide_examples_are_inline_and_valid(self):
        text = (ROOT / "templates" / "decision-request.md").read_text(encoding="utf-8")
        self.assertFalse([l for l in text.splitlines() if l.startswith("/decide")],
                         "a line starting with /decide in an agent comment would decide by itself")
        examples = re.findall(r"`(/decide [^`]+)`", text)
        self.assertTrue(examples)
        for example in examples:
            if "<" not in example:
                self.assertRegex(example, c.DECIDE_COMMAND)

    def test_regexes_compile(self):
        for name in dir(c):
            if name.isupper() and isinstance(getattr(c, name), str):
                re.compile(getattr(c, name), re.MULTILINE)


class LabelFamilies(unittest.TestCase):
    def test_families_match_spec(self):
        spec = (ROOT / "spec" / "v1" / "04-github-contract.md").read_text(encoding="utf-8")
        for family in c.LABEL_FAMILIES:
            self.assertIn(f"`{family.prefix}`", spec)

    def test_every_label_has_description(self):
        for family in c.LABEL_FAMILIES:
            for value, description in family.values:
                self.assertTrue(description, f"{family.prefix}{value}")


if __name__ == "__main__":
    unittest.main()
