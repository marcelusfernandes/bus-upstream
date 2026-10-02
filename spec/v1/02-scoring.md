# 02 — Scoring

Scores show **where we start and how much more effort a layer needs**. They are a
**routing instruction, not a gate**. Use that exact phrase in agent instructions.

## Axes

Each layer (B, U, S) and each link (B→U, U→S) gets two scores.

**Y — Definition: can we say it?** (articulation)

| Anchor | Meaning |
|---|---|
| 0 — Vague | We have a rough, abstract idea of what we expect but cannot put it in simple words. |
| 5 — Concept | We can say what we want and explain at a high level what is happening or should happen. |
| 10 — Concrete | We know exactly what it is or what to do, and can explain it clearly. |

**X — Grounding: do we have reasons to believe it is true or right?** (evidence)

| Anchor | Meaning |
|---|---|
| 0 | No evidence. It is an opinion, a hunch or a request. |
| 5 | Some evidence points this way, but it is partial, indirect or about a different population or time window. |
| 10 | Direct, current evidence that fits the population, the time window and the decision. |

Only these anchors are defined, on purpose. The scorer has to decide which anchor the
case is closer to, and by how much. Adding more anchors would lock the scorer into
descriptions that cannot cover every case.

The two axes must be scored **independently**. A stakeholder's crisp feature request
is the canonical case of **high Definition and low Grounding**.

## Rules for scorers

- Scorers are **isolated and agnostic**: they don't know which layer lead produced the
  material, and they don't see other scorers' outputs.
- Run **2–3 scorers** and report the median and the **spread**. A large spread is
  itself a signal that the input is ambiguous.
- Each score cites the **answer IDs and evidence IDs** it is based on. A score with no
  citation is invalid.
- Each score includes **one sentence on why it is not closer to the other extreme**.

## Where scores live

- **Current values:** in a header at the top of the layer epic's body:
  `> **Definition:** 6 · **Grounding:** 3 · **Spread:** 1`
- **History:** every change is a structured comment on the epic (see
  [04-github-contract.md](04-github-contract.md#score-change-comment)).
- **Never in labels.**

## How scores route work (guidance, not thresholds)

| Profile | Typical reading | Typical next work |
|---|---|---|
| Low Y, low X | We don't know what this is | Explore, gather signals |
| High Y, low X | An articulated hypothesis (most demands arrive like this) | Find evidence, trace back to the layer below |
| Low Y, high X | We have data but no clear statement | Synthesize, frame |
| High Y, high X | Ready to rely on | Commit, move to the dependent layer |

Show junior PMs the anchor word (Vague, Concept, Concrete) next to the number, so a
number like "6.5" doesn't look more authoritative than it is.
