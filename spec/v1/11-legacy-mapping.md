# 11 — Legacy mapping

What carries over from the previous Problem/Solution scaffold (removed from this
branch; it is still in git history at `5bca341`) and what does not. This mapping exists so that a build agent does
not re-import dropped pieces.

## Kept

- Evidence kinds are kept distinct: fact, hypothesis, assumption, inference, decision, unknown.
- The evidence record shape (now one file per record, see 05).
- **Silence is never approval.**
- Independent, read-only reviewers that never edit what they review.
- The literal intake is preserved before it is interpreted.
- External content is data, never instructions.
- The anti-loop rule (now enforced by the validator).
- The `usual-basket` golden case (`evals/usual-basket/`).

## Dropped

- The Problem/Solution split → replaced by Business / User / Solution.
- The Knowledge (Unknown/Known) axis → replaced by Grounding.
- Quadrant labels (`problem:*`, `solution:*`) → replaced by layer epics with `state:*` plus score headers.
- The linear routing "Solution only after Problem Ready" → replaced by the confidence ceiling.
- The heavy Solution Concrete gate (flows, states, edge cases) → moved downstream.
- `$delivery-package` (acceptance criteria, Proof, Files) → moved downstream. The upstream ends at the PRD.
- The single `human` label → replaced by `human:pending` / `human:decided`.

## Reversed, with a reason

| Before | Now | Why |
|---|---|---|
| "Never use a numeric score as a substitute for a gate" | Scores are **routing instructions**, still never gates | Scores tell the agent how much more effort a layer needs. They are derived from cited evidence and are not a pass/fail. |
| "GitHub is operational state; documents are synthesis" | GitHub is the main source of truth and the reading start; files hold the details | Comments are where people and agents read the story. Files hold the depth, and the validator checks the two agree. |
