<!-- A decision request is a COMMENT on the issue that needs the decision (usually the layer
epic), never a separate issue. Written by `upstream_ops decision-open`. The issue then tells
the whole story: request → the PM's /decide → the agent's record.
A PM reading only this comment must be able to decide: the context can take about three
paragraphs; never cut information to make it shorter. -->
## Decision request D-001 · B-01 · Which outcome does this demand serve first?

**Context:** The demand names lower support cost and fewer churned accounts, with a baseline only for support cost (E-002, E-004). Which outcome we pursue first decides what B1 says and which data we look for next.

**Options**
- **A** — Support cost per account · trade-offs: measurable now, but may miss churn · reversibility: easy
- **B** — Churn among accounts that called about billing · trade-offs: needs a churn baseline first · reversibility: easy

**Recommendation:** A — it has a baseline today (E-004)
**What would change the recommendation:** churn data showing billing calls predict churn
**Evidence:** E-002 · **Blocks:** B1 and gate 1

To decide, reply on this issue with `/decide A` (add `Why: <your reasoning>` on the next line) or `/decide other: <your option>`. If several decisions are waiting here, name this one: `/decide D-001 A`. Other comments keep it pending.
