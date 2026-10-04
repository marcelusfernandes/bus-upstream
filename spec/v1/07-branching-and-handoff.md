# 07 — Branching and handoff

## Branches

- Each intake gets its own branch, `upstream/<slug>`, created from an **updated
  main**. `create_initiative.py --apply` creates it automatically (or resumes it if it
  already exists), and commits and pushes the intake; PMs never create branches.
- Intake also opens a **draft PR** from `upstream/<slug>` into `main`, with `Closes #N` for
  every issue it created. That links the branch and the PR to each issue in GitHub's
  **Development** panel, and it is the PR used for the final review at handoff. The slug names the outcome or the demand in a few words, for example
  `upstream/invoice-clarity`.
- All of the initiative's files live under `initiatives/<slug>/`, so parallel
  branches don't conflict with each other.

## Handoff

1. The PRD writer compiles `prd/README.md` from the committed layers.
2. A **PR from `upstream/<slug>` to main** is opened. The PRD review runs as the PR
   review: the isolated reviewer comments and gives a verdict.
3. **PM approval of the PR is the handoff gate.** Merging puts the initiative into main
   as part of the knowledge base, so learnings can be aggregated across initiatives.
4. The PRD epic links the Designer to the PRD.


## PRD content

| Section | From |
|---|---|
| Business problem (one sentence), baseline, success signal, why it is relevant now | B |
| User problem (one sentence), who, situation, evidence (root, not surface) | U |
| B→U link and its confidence | link |
| Solution (one sentence), alternatives considered, high-level How | S / bet |
| Derived hypotheses to validate in design, each with how it could be tested | S4 |
| Stakeholder hypotheses and what happened to them | hypothesis register |
| U→S link: confidence and what would prove us wrong | link |
| Named bets / accepted risks, and who accepted them | decisions |
| Open questions handed to design | everything not closed |

There are **no acceptance criteria, no files and no edge-case catalog**. Those belong downstream.

A non-product solution (a process, operations or communication change) still produces
a PRD, describing what will be done and why.

## Several bets, roadmaps and journeys

- The milestone holds the shared **why** (B, U and the links).
- Each bet has an ID and a folder from day one (`solution/bets/S-A/`).
- In v1, a single bet means a single PRD epic. With parallel bets, each bet that
  proceeds gets its own PRD. A journey-level change becomes a sequenced set of bets:
  the first gets the PRD, and the rest stay as linked hypotheses.
- When a team picks up a bet downstream, it **gets its own milestone**, which links back to
  the demand's milestone (R-29).
- When the solution grows from a feature into a journey, that triggers human gate 5
  (material scope expansion).
