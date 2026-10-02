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

```
## Decision D-001 · B-01 · Which outcome does this demand serve?
Question: The demand names conversion vs. the App, interaction cost, recurrence
and AOV. Which outcome do we optimize first?
Recommendation: <agent fills after the B lead's first pass>
Why / Trade-offs / Reversibility / What would change it / Evidence: E-001, E-002
Blocks: B epic cannot reach done; S cannot commit.
```
