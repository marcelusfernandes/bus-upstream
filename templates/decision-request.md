<!-- A decision request is a COMMENT on the issue that needs the decision (usually the layer
epic), never a separate issue. Written by `upstream_ops decision-open`. The issue then tells
the whole story: request → the PM's /decide → the agent's record.
Limits: question ≤ 120 characters, context ≤ 700, each option text and trade-offs ≤ 140.
A PM reading only this comment must be able to decide. -->
## Decision request D-001 · B-01 · Which outcome does this demand serve first?

**Context:** The demand names faster purchase, lower interaction cost and conversion against the App, with no baseline for any of them (E-002, E-004). Which outcome we pursue first decides what B1 says and which data we look for next.

**Options**
- **A** — Conversion of the repurchase flow against the App · trade-offs: needs channel data · reversibility: easy
- **B** — Interaction cost per order · trade-offs: ignores recurrence · reversibility: easy

**Recommendation:** A — E-002 names conversion first
**What would change the recommendation:** cost data showing a larger gap
**Evidence:** E-002 · **Blocks:** B1 and gate 1

To decide, reply on this issue with `/decide A` (add `Why: <your reasoning>` on the next line) or `/decide other: <your option>`. If several decisions are waiting here, name this one: `/decide D-001 A`. Other comments keep it pending.
