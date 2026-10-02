# 07 — Branching and handoff

## Branches

- Each intake gets its own branch, `upstream/<slug>`, created from an **updated
  main**. The slug names the outcome or the demand in a few words, for example
  `upstream/basket-repurchase`.
- All of the initiative's files live under `initiatives/<slug>/`, so parallel
  branches don't conflict with each other.

## Handoff

1. The PRD writer compiles `prd/README.md` from the committed layers.
2. A **PR from `upstream/<slug>` to main** is opened. The PRD review runs as the PR
   review: the isolated reviewer comments and gives a verdict.
3. **PM approval of the PR is the handoff gate.** Merging puts the initiative into main
   as part of the knowledge base, so learnings can be aggregated across initiatives.
4. The PRD epic links the Designer to the PRD.

(R-20 is still **proposed**. See [10-open-questions.md](10-open-questions.md).)

## PRD content

| Section | From |
|---|---|
| Business problem, baseline, success signal, why now | B |
| User problem: who, situation, evidence (root, not surface) | U |
| B→U link and its confidence | link |
| Solution direction (What) + alternatives considered + high-level How | S / bet |
| U→S link: confidence and what would prove us wrong | link |
| Named bets / accepted risks, and who accepted them | decisions |
| Open questions handed to design | everything not closed |

There are **no acceptance criteria, no files and no edge-case catalog**. Those belong downstream.

## Several bets, roadmaps and journeys

- The milestone holds the shared **why** (B, U and the links).
- Each bet has an ID and a folder from day one (`solution/bets/S-A/`).
- In v1, a single bet means a single PRD epic. With parallel bets, each bet that
  proceeds gets its own PRD. A journey-level change becomes a sequenced set of bets:
  the first gets the PRD, and the rest stay as linked hypotheses.
- When a team picks up a bet downstream, it may become its own milestone that links
  back to this one. This is deferred (see [10-open-questions.md](10-open-questions.md)).
- When the solution grows from a feature into a journey, that triggers human gate 5
  (material scope expansion).
