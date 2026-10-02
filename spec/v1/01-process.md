# 01 — Process

## The model

```
        ┌───────────┐
        │  Solution │  What we will do (+ high-level How)
        ├───────────┤        ↑ U→S link: does this solve the user problem?
        │   User    │  Which user problem drives the business problem
        ├───────────┤        ↑ B→U link: does solving it move the outcome?
        │ Business  │  Why it matters to the company
        └───────────┘
```

- **Business problem (B).** The desired outcome, how we know the problem exists (the
  baseline signal), and how we will know we succeeded (the target). A KPI is not
  forced. B may also be a business consequence such as revenue, cost, risk, an
  obligation or a strategic position.
- **User problem (U).** Who is affected, in what situation, and what they struggle
  with. It must be the root problem, not a surface complaint, backed by evidence.
- **Solution (S).** What we will do and a high-level How. One or more **bets**, each
  with an ID. The How is refined downstream through flows, screens and edge cases.
- **Links.** B→U ("solving this user problem moves that outcome") and U→S ("this
  solution solves that user problem") are explicit claims, each with its own
  confidence. Most failures happen at the links.

The pyramid shows dependency, **not order**. Work can start at any layer.

## Flow

```
Intake ──► fragments per layer (B / U / S) + scores
   │
   ▼
Orchestrator routes to the layer whose gap most limits the next commit
   │
   ├─► Business lead ─┐
   ├─► User lead ─────┼─► answers ─► isolated review ─► commit ─► re-route ↺
   └─► Solution lead ─┘
   │
   ├─► B↔U fit review  (before Solution commits a direction)
   ├─► U↔S fit review  (before the PRD is final)
   └─► PRD review      (before designer handoff)
   │
   ▼
PRD epic ──► Designer (downstream)
```

## Intake

1. Preserve the demand **literally**.
2. Split it into **fragments per layer**. A single sentence often contains all three:
   a solution, a business outcome and an open question.
3. Score each layer's Definition and Grounding (see [02-scoring.md](02-scoring.md)).
4. Create the milestone and the B/U/S/PRD epics (see [04-github-contract.md](04-github-contract.md)).

A solution-shaped demand typically scores **high Definition and low Grounding** on S,
and low on B and U. That profile means "trace back to B and U". It does not mean
"build it".

## Routing rules

- **Confidence ceiling (invariant).** A layer cannot be committed with more confidence
  than the layer below it supports. Solution work may *explore* at any time, because
  sketches are good probes for the user problem. It may only *commit* a direction up
  to what U and B justify. Any gap that remains is inherited as a named risk.
- **B first by default.** Start from the business problem unless the PM decides on a
  **U-first override** (for example harm, safety or urgency). The override is a human
  decision.
- **Pick one gap.** The orchestrator routes to the single gap that most limits the
  next commit. The scores tell it whether to gather more information or move on.
- **~70% rule.** Proceed when the critical questions of a layer are answered or
  deliberately bet on. Write the bets down. 10 is not a goal.
- **Anti-loop.** If the same question fails twice without new evidence, mark it
  `state:blocked` + `human:pending`, record why, and stop repeating the approach.

## Key questions per layer (seed set)

These questions are the core product, for both the agent and the junior PM. Each
answer gets an ID (`B-01`, `U-02`, …).

**Business**
- What outcome does the business want? Is the request a solution standing in for it?
- How do we know the problem exists (numbers, feedback, incidents)? What is the baseline?
- How will we know we succeeded? Propose a metric or a success description; the PM validates it.
- Why now? What does inaction cost?

**User**
- Who is affected, and in what situation?
- What do they struggle with? Is it the root problem or a surface complaint?
- How do we know (interviews, behavior data, support, research)?
- **B→U:** does solving this move the business outcome? How confident are we, and what would prove us wrong?

**Solution**
- What are the genuinely different options (different mechanisms, not variations)?
- **U→S:** which option solves the user problem, and therefore the business problem?
- How confident are we that it will work? What would make us stop?
- What is the high-level How, and what are its main risks?

## Human decisions

The agent asks and the PM decides. Every question carries: a **recommendation**, the
**why**, the **trade-offs**, the **reversibility**, and **what would change the
recommendation**.

Gates (kept few on purpose):

1. Which **business problem/outcome** we serve, including pushback on the demand's framing.
2. Which **user problem** we bet on (the U pivot).
3. Which **solution direction / bet(s)** go to design.
4. **Accepting a gap as risk** (the missing ~30%).
5. **Material scope expansion**, for example when a feature turns out to be a journey redesign.

Silence is never approval. A decision exists only as the PM's own comment.

## Modes

- **Piloted** (default, junior PM): all five gates stop and wait for the PM.
- **Autonomous** (senior PM, opt-in per milestone): gates 2 and 3 become recorded
  recommendations, reviewed with the final conclusions. **Gates 1, 4 and 5 always
  stay human**, because they accept business risk or change what was asked.

## End of upstream

The upstream ends when the PRD epic passes the PRD review and the PM approves the
handoff. Parallel bets, or a roadmap of bets, are allowed: each bet that proceeds
gets its own PRD (see [07-branching-and-handoff.md](07-branching-and-handoff.md)).
