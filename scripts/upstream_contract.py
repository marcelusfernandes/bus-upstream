"""Machine contract of the BUS upstream (spec/v1/04-github-contract.md).

Single source for label families and the line patterns that agents write and the
validator parses. tests/test_contract.py checks that templates/ agree with it.
"""
from dataclasses import dataclass

# ---------- Labels ----------


@dataclass(frozen=True)
class LabelFamily:
    prefix: str
    exclusive: bool
    color: str
    values: tuple  # ((value, description), ...)

    def names(self):
        return tuple(f"{self.prefix}{value}" for value, _ in self.values)


LABEL_FAMILIES = (
    LabelFamily("layer:", True, "5319E7", (
        ("business", "Business problem layer"),
        ("user", "User problem layer"),
        ("solution", "Solution layer"),
        ("prd", "PRD"),
    )),
    LabelFamily("state:", True, "0E8A16", (
        ("ready", "Created by intake, work not started"),
        ("in-progress", "Lead and subagents are working"),
        ("in-review", "Isolated reviewer is checking an answer or fit"),
        ("qa-failed", "Review rejected; back to work"),
        ("blocked", "Anti-loop triggered; always with human:pending"),
        ("done", "Answered enough for dependent layers; can reopen"),
    )),
    LabelFamily("type:", True, "C5DEF5", (
        ("question", "A key question being answered"),
        ("evidence", "An evidence-gathering task"),
        ("review", "An adversarial review"),
        ("hypothesis", "A registered hypothesis"),
    )),
    LabelFamily("hyp:", True, "FBCA04", (
        ("open", "Hypothesis not resolved yet"),
        ("validated", "Hypothesis supported by evidence"),
        ("invalidated", "Hypothesis refuted by evidence"),
        ("reframed", "Hypothesis evolved into another one"),
        ("merged", "Hypothesis merged into another one"),
        ("parked", "Hypothesis set aside, with a reason"),
    )),
    LabelFamily("human:", True, "B60205", (  # exactly one: pending while anything waits, else decided
        ("pending", "Waiting for the PM's /decide"),
        ("decided", "Decided by the PM (permanent)"),
    )),
    LabelFamily("agent:", True, "D4C5F9", (
        ("decided", "Decided by the agent in autonomous mode"),
    )),
    LabelFamily("mode:", True, "BFD4F2", (
        ("piloted", "Junior PM: every gate waits for the PM"),
        ("autonomous", "Senior PM: agent decides, reviewed at handoff"),
    )),
    LabelFamily("epic", False, "3E4B9E", (
        ("", "Layer epic (B, U, S or PRD)"),
    )),
)

EXCLUSIVE_PREFIXES = tuple(f.prefix for f in LABEL_FAMILIES if f.exclusive)
LAYER_CODE = {"layer:business": "B", "layer:user": "U", "layer:solution": "S"}

# ---------- IDs ----------

ANSWER_ID = r"[BUS]-\d{2}"
FIT_ID = r"(?:BU|US)-fit"
DECISION_ID = r"D-\d{3}"
EVIDENCE_ID = r"E-\d{3}"
HYPOTHESIS_ID = r"H-\d{2}"
# Check 1 covers answer, decision, evidence and hypothesis IDs. Bets (S-A) and fit
# reviews (BU-fit, US-fit) have no file of their own in v1, so they are not resolved.
CITABLE_ID = rf"\b(?:{ANSWER_ID}|{DECISION_ID}|{EVIDENCE_ID}|{HYPOTHESIS_ID})\b"

# ---------- Lines agents write ----------

SCORE_HEADER = (r"^> \*\*Definition:\*\* (?P<d>\d+) · \*\*Grounding:\*\* (?P<g>\d+)"
                r" · \*\*Spread:\*\* (?P<s>\d+)$")
ANSWER_TITLE = rf"^## Answer (?P<id>{ANSWER_ID}) · (?P<text>.+)$"
SCORE_TITLE = (r"^## Score · (?P<layer>[BUS]) · Definition (?P<d0>\d+|–) → (?P<d1>\d+)"
               r" · Grounding (?P<g0>\d+|–) → (?P<g1>\d+)$")
REVIEW_TITLE = rf"^## Review · (?P<id>{ANSWER_ID}|{FIT_ID}|PRD) · (?P<verdict>approved|rejected)$"
REOPEN_TITLE = rf"^## Reopened · (?P<id>{ANSWER_ID}) invalidated by (?P<by>{EVIDENCE_ID}|{DECISION_ID})$"
DECISION_TITLE = rf"^## Decision (?P<id>{DECISION_ID}) · (?P<ref>{ANSWER_ID}|{FIT_ID}) · (?P<text>.+)$"
DECISION_REQUEST_TITLE = (rf"^## Decision request (?P<id>{DECISION_ID}) · (?P<ref>{ANSWER_ID}|{FIT_ID})"
                          rf" · (?P<question>.+)$")
HYPOTHESIS_TITLE = (rf"^## Hypothesis (?P<id>{HYPOTHESIS_ID}) · "
                    rf"(?P<status>validated|invalidated|parked|(?:reframed|merged) → {HYPOTHESIS_ID})$")
DECIDE_COMMAND = rf"^/decide(?: (?P<target>{DECISION_ID}))? (?P<choice>[A-Z]|other: .+)$"

SCORE_MIN, SCORE_MAX = 0, 10

# ---------- Agent identity ----------
# Agents comment with the PM's GitHub account today, so every agent comment carries an
# invisible marker. A PM decision relayed from Codex carries the relay marker and never
# the agent marker.

AGENT_NAME = "Enceladus"
AGENT_MARKER = r"<!-- enceladus(?::(?P<role>[a-z_]+))? -->"
RELAY_MARKER = "<!-- relayed-from:codex -->"


def signature(role):
    return f"\n<!-- enceladus:{role} -->"


# ---------- Decision request limits (format, so a PM can read it in the issue) ----------

REQUEST_QUESTION_MAX = 120
REQUEST_OPTION_MAX = 140
REQUEST_CONTEXT_MAX = 700

# ---------- Commits ----------

CONVENTIONAL_TYPES = ("feat", "fix", "refactor", "docs", "test", "chore", "perf", "ci")
ANSWER_COMMIT_TITLE = rf"^(?P<id>{ANSWER_ID}): \S.*$"
CONVENTIONAL_TITLE = rf"^(?:{'|'.join(CONVENTIONAL_TYPES)})(?:\([^)]+\))?!?: \S.*$"
PASSTHROUGH_TITLE = r"^(?:Merge |Revert \")"
TRAILER_FORMATS = {
    "Layer": r"^(?:business|user|solution)$",
    "Definition": r"^\d+ -> \d+$",
    "Grounding": r"^\d+ -> \d+$",
    "Evidence": rf"^{EVIDENCE_ID}(?:, {EVIDENCE_ID})*$",
    "Decision": rf"^{DECISION_ID}$",
    "Invalidates": r"^[0-9a-f]{7,40}$",
}
REQUIRED_TRAILERS = ("Layer",)
