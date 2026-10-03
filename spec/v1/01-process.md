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

The intake agent is a separate, initial agent. It does not run the Business layer.

1. Preserve the demand **literally**.
2. **Gather context**: the product, the journey step, and any comparison the demand
   makes (for example with CRM channels). Context is gathered, not required as a field:
   in most cases the work is about the App, and the agent records that as context
   unless the demand signals otherwise. It asks the PM only when the context is ambiguous.
3. **Record the evidence it cites** (`E-nnn`, with a source). Every cited ID must be
   recorded, and every recorded ID must be cited; `scripts/create_initiative.py` refuses
   the intake otherwise.
4. Split it into **fragments per layer**. A single sentence often contains all three:
   a solution, a business outcome and an open question.
5. Score each layer's Definition and Grounding (see [02-scoring.md](02-scoring.md)).
6. Create the milestone and the B/U/S/PRD epics (see [04-github-contract.md](04-github-contract.md)).

A solution-shaped demand typically scores **high Definition and low Grounding** on S,
and low on B and U. That profile means "trace back to B and U". It does not mean
"build it".

## Routing rules

- **Confidence ceiling (invariant, judged).** A layer cannot be committed with more
  confidence than the layer below it supports. Reviewers and the fit reviews judge this;
  it is not computed. Solution work may *explore* at any time, because
  sketches are good probes for the user problem. It may only *commit* a direction up
  to what U and B justify. Any gap that remains is inherited as a named risk.
- **No fixed order.** Work can start at any layer and move back and forth between
  layers. The PM's direction wins. Otherwise the orchestrator judges where the demand
  is weakest relative to what it claims, and which gap blocks the next decision.
- **Routing is judgment, not code.** The guidance lives in the orchestrator's skill
  (`.agents/skills/orchestrator/SKILL.md`), as text PMs can edit. `scripts/reconcile.py`
  only reports facts and contract obligations; it never decides which layer comes next.
  Scores inform the choice, they do not make it.
- **~70% rule.** Proceed when the critical questions of a layer are answered or
  deliberately bet on. Write the bets down. 10 is not a goal.
- **Anti-loop.** If the same question fails twice without new evidence, mark it
  `state:blocked` + `human:pending`, record why, and stop repeating the approach.

## Key questions and hypotheses

The key questions per layer, the one-sentence rule for B1, U1 and S2, and the
hypothesis register are defined in [12-key-questions.md](12-key-questions.md).

**How the user layer starts.** A hypothesis may arrive with the intake, scored as low
Grounding; the work then tests it. If there is no hypothesis, discovery is needed to
find candidate problems, often led by the Product Designer. Either way, U usually has
no answer at the start. B can progress and S can explore probes while U is in
discovery, but under the confidence ceiling S cannot commit until U is grounded or
the gap is accepted as risk (gate 4).

**Hypotheses from the business are never ignored.** Every user-problem or solution
hypothesis that comes with the demand is registered with its origin and routed to the
layer that can test it. That layer must close it explicitly: validated, invalidated,
reframed, merged or parked, always with a reason.

## Human decisions

The agent asks and the PM decides. Every question carries: a **recommendation**, the
**why**, the **trade-offs**, the **reversibility**, and **what would change the
recommendation**.

Gates (kept few on purpose):

1. Which **business problem/outcome** we serve, including pushback on the demand's framing.
2. Which **user problem** we bet on (the U pivot). This gate fires when discovery or
   hypothesis testing has produced candidates, not at intake.
3. Which **solution direction / bet(s)** go to design.
4. **Accepting a gap as risk** (the missing ~30%).
5. **Material scope expansion**, for example when a feature turns out to be a journey redesign.

Silence is never approval. A decision exists only as the PM's own comment.

## Modes

- **Piloted** (default, junior PM): all five gates stop and wait for the PM.
- **Autonomous** (senior PM, opt-in per milestone): the whole process runs without
  stopping. At each gate the agent still opens the decision sub-issue with the full
  recommendation, decides, and marks it `agent:decided`. The senior PM reviews all
  agent decisions together with the conclusions at the handoff PR, and can roll back
  to any answer commit. The exception is `state:blocked` (anti-loop): it still needs a
  human, because the process cannot continue on its own.

## End of upstream

The upstream ends when the PRD epic passes the PRD review and the PM approves the
handoff. Parallel bets, or a roadmap of bets, are allowed: each bet that proceeds
gets its own PRD (see [07-branching-and-handoff.md](07-branching-and-handoff.md)).
