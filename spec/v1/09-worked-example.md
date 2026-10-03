# 09 — Worked example: `usual-basket`

Source: `evals/usual-basket/input.md` and `evidence.md`. This example **stops where
those files stop**. It shows the intake and the first routing only. Everything after
that is not in the eval and is not invented here.

## Literal demand

> Se o fluxo for mais rápido ele pode converter mais que o App, e o custo de
> interação é menor. Objetivo: agilizar a compra e reduzir custo. Também queremos
> entender se ajuda na recorrência ou mexe no AOV.

## Fragments per layer

| Layer | Fragment | Kind |
|---|---|---|
| S | "fluxo mais rápido" | Solution suggested by the stakeholder |
| B | "converter mais que o App", "reduzir custo" | Desired outcomes (E-002) |
| B | "recorrência ou AOV" | Open outcome question |
| B→U / U→S | "se for mais rápido ele pode converter mais" | Causal hypothesis: speed → conversion. The eval warns not to assume it. |
| U | (none stated) | User problem missing |

## Hypothesis register at intake

| ID | Hypothesis | Kind | Origin | Routed to |
|---|---|---|---|---|
| H-01 | "a faster flow" | solution | business demand | S |
| H-02 | "if it is faster, it converts more than the App" | causal | business demand | U (B→U) |
| H-03 | "it helps recurrence or changes AOV" | causal, open | business demand | B (in scope?) |

None of these can be dropped. If speed turns out not to be the user's problem, H-01 is
closed as `invalidated` with the evidence, so it is never silently ignored.

## Initial scores (illustrative reasoning, scored against the anchors)

| Layer | Definition | Grounding | Why not closer to the other extreme |
|---|---|---|---|
| B | ~5 (Concept) | ~3 | The outcomes are named but there's no baseline or target. E-002 is a decision about what is wanted, not evidence that the problem exists. |
| U | ~1 (Vague) | ~2 | No user or situation is stated. E-001 shows recurrent repurchase exists but says nothing about a struggle. |
| S | ~5 (Concept) | ~0 | "A faster flow" is articulated, but nothing defines it (E-003), and no evidence connects speed to conversion. |

These numbers show the scoring method. They are not eval ground truth.

## Expected routing

- The profile is a solution-shaped demand: S articulated but ungrounded, U vague, B partial.
- Trace back: the **Business lead** first, to establish the baseline and the success
  signal for conversion and cost, and to settle whether recurrence or AOV is in scope.
- In parallel or right after, the **User lead** looks for the user problem behind
  recurring repurchase (E-001), which is a candidate starting point.
- Solution may explore "faster flow" only as a probe. Under the confidence ceiling it
  cannot commit.

## Epics the intake agent creates

`B · Business problem`, `U · User problem`, `S · Solution`, `PRD`. All start at
`state:ready` and `mode:piloted`, with score headers filled from the table above.

## First question to the PM (gate 1, illustrative)

Posted as a comment on the **B epic**, not as a separate issue:

```
## Decision request D-001 · B-01 · Which outcome does this demand serve first?
- **A** — Conversion of the repurchase flow against the App · trade-offs: … · reversibility: easy
- **B** — Interaction cost per order · trade-offs: … · reversibility: easy
**Recommendation:** A — <agent fills after the B lead's first pass>
To decide, reply on this issue with `/decide A` …
```

## Key-question pass (Q-10)

Only `input.md` and `evidence.md` (E-001 to E-003) were used. "Who" follows
[12-key-questions.md](12-key-questions.md).

| ID | State at intake | What we can say | Next |
|---|---|---|---|
| B1 | open | The one-sentence business problem can't be written. Desired outcomes are known (E-002), but what is going wrong is not. | 🗣 PM homework, then gate 1 |
| B2 | open | No baseline exists for conversion, cost or time to order. E-002 records what is wanted, not that a problem exists. | 🔎 get data |
| B3 | bet (partial) | The directions are known (less time to order, lower interaction cost, conversion compared with the App). There are no targets. Recurrence and AOV may be guardrails rather than goals. | 🔎 propose, 🗣 PM validates |
| B4 | open | Nothing in the intake says why this is relevant now. | 🗣 |
| B5 | evidenced | H-01 to H-03 are registered with their origin. | done |
| U1 | open | No user problem is stated. | discovery |
| U2 | open | E-001 shows that recurrent repurchase exists, not that users struggle with anything. | 🔎 |
| U3 | open | Depends on H-02 (speed → conversion). | 🔎 |
| U4 | open | H-02 is routed to U. | 🔎 |
| S1 | open | H-01 (faster flow) must be among the options. Other mechanisms may be explored as probes only. | 🔎 |
| S2–S4 | blocked | The confidence ceiling applies: U is not grounded. | — |

An agent may register a new hypothesis from E-001. For example, H-04: "recurrent
buyers spend effort rebuilding the same basket", with origin `agent` and routed to U.
It must stay a **hypothesis**. The eval explicitly warns against assuming a
"last order" problem or a "recurrent basket" solution. The register is what keeps that
idea visible without turning it into U1.

### What the pass shows

**Holds:**
- The register captured all three stakeholder hypotheses without losing any.
- The one-sentence rule made it visible that B1 can't be written yet. That is a low
  Definition score, and it routes the work to the PM.
- Almost everything is `open` at intake. That is expected, and none of it is asked of
  the PM up front except PM homework.

**PM load at the start:** three items, B1 (what is going wrong), B4 (why it is relevant
now) and whether H-03 is in scope. Each comes as proposed options with a
recommendation, not as an open question. The channel is asked about only if the
comparison with the App is ambiguous. This is acceptable compared with the first
version of the process.

**Gaps found:**
- **Product or channel context is missing.** "Converts more than the App" implies a
  comparison with another channel or flow. **Resolved:** the intake agent gathers context
  (product, journey step, comparisons). This is not a required field; it defaults to the
  App, and the agent asks only when the context is ambiguous.
- **B3 needs primary versus guardrail metrics.** With several outcomes (conversion,
  cost, recurrence, AOV), B3 should name **one primary** success metric plus the
  **guardrails** that must not get worse. **Resolved:** the agent proposes options and
  the PM picks one or proposes another.
- **Hypotheses generated by agents need a basis.** **Resolved:** the register has a
  `Basis` field (evidence IDs or `guess`). It is required when the origin is `agent`, and
  a guess is allowed as long as it is labeled as one.
