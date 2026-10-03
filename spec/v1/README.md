# BUS Upstream — Spec v1

Status: **draft** · Branch: `redesign/bus-upstream` · Started: 2026-10-02

This folder specifies the redesigned product upstream: an AI-agent-run process that
takes a demand from stakeholders to a clear **Business problem**, **User problem** and
**Solution** direction, packaged as a PRD the Product Designer uses to design.

> **Legacy notice.** The previous Problem/Solution scaffold (skills, agents, docs,
> templates, scripts and issue templates) was removed from this branch. Git history keeps
> it. See [11-legacy-mapping.md](11-legacy-mapping.md) for what carried over.

## Who it is for

- **Junior PM** — pilots the agents and makes every high-impact decision.
- **Senior PM** — may run it in autonomous mode and review the conclusions.
- **Product Designer** — partners on the User layer and receives the PRD.
- **Agents** — do the research, synthesis, scoring and review.

## Reading order

1. [01-process.md](01-process.md) — the BUS model, how work moves, human gates.
2. [02-scoring.md](02-scoring.md) — Definition × Grounding, how scores route work.
3. [03-agents.md](03-agents.md) — agent roles and how they hand over.
4. [04-github-contract.md](04-github-contract.md) — milestones, epics, labels, lifecycle, comments.
5. [05-folder-contract.md](05-folder-contract.md) — where details live in the repo.
6. [06-commit-contract.md](06-commit-contract.md) — commits as answer checkpoints.
7. [07-branching-and-handoff.md](07-branching-and-handoff.md) — branches, PR, PRD handoff.
8. [08-validator-and-hooks.md](08-validator-and-hooks.md) — how drift is detected.
9. [09-worked-example.md](09-worked-example.md) — `usual-basket` through the new model.
10. [10-open-questions.md](10-open-questions.md) — not decided yet.
11. [11-legacy-mapping.md](11-legacy-mapping.md) — what is kept, dropped or reversed.
12. [12-key-questions.md](12-key-questions.md) — key questions per layer and the hypothesis register.

## Decision register

| ID | Decision | Status |
|---|---|---|
| R-01 | Three layers: Business problem, User problem, Solution (BUS). Non-linear. | agreed |
| R-02 | The intake can arrive at any layer; the PM traces it back to B and U. | agreed |
| R-03 | B is the desired outcome plus how we know the problem exists and how we know we succeeded. A KPI is not forced. | agreed |
| R-04 | Two axes: Y = Definition, X = Grounding. Anchors only at 0/5/10. Scores are routing instructions, not gates. | agreed |
| R-05 | The links B→U and U→S are first-class; their causality and probability are made explicit. | agreed |
| R-06 | Agents run the process. The PM decides high-impact questions after receiving a recommendation, the reasoning and the trade-offs. | agreed |
| R-07 | Two modes: piloted (junior, all gates human) and autonomous (senior, the whole process runs; decisions are labeled `agent:decided` and reviewed at handoff). | agreed |
| R-08 | Phase leads use collector/explorer subagents. A thin cross-phase orchestrator owns routing. | agreed |
| R-09 | Isolated adversarial reviews are triggered by commits of answers and fits, not by phases. | agreed |
| R-10 | GitHub issues, comments and labels are the main source of truth. Files hold the details. No YAML state file. | agreed |
| R-11 | v1 structure: a milestone plus B/U/S/PRD epics, no hub issue. | agreed |
| R-12 | Scores live in the epic body header; each change is a structured comment. Scores are never labels. | agreed |
| R-13 | `human:pending` → `human:decided` on the issue holding the decision, one `human:` label at most (see R-39), plus decision comment title patterns. | agreed |
| R-14 | One commit per decided answer, carrying the reasoning, the learnings and trailers. | agreed |
| R-15 | One branch per intake, `upstream/<slug>`, created from an updated main. | agreed |
| R-16 | The PRD is an epic in the demand's milestone in v1. Bets get their own IDs and folders from day one. | agreed |
| R-17 | Adopt from Apollo: a README reading order; evidence → review → distilled with "review wins"; short single-target returns. | agreed |
| R-18 | Reuse the lohra/Apollo `state:*` names with upstream semantics and a reopen rule. | proposed |
| R-19 | One validator script, run from a `commit-msg` hook and a GitHub Action. | proposed |
| R-20 | The PR at handoff serves as the final review and the PM gate; merging puts it into the main knowledge base. | agreed |
| R-21 | Language: the spec is in English; templates and comments are in the PMs' language. | agreed |
| R-22 | The PM decides with `/decide`; a GitHub Action swaps the labels and ignores other comments and non-assignees. | agreed |
| R-23 | U often starts with no answer: either a hypothesis to test or discovery. Gate 2 fires when candidates exist. | agreed |
| R-24 | B1, U1 and S2 are each one sentence; the detail goes in the answer file. | agreed |
| R-25 | Hypothesis register: hypotheses are registered with their origin, routed to a layer, and closed explicitly. A layer cannot be done with open hypotheses. | agreed |
| R-26 | B4 asks "Why is it relevant now?" | agreed |
| R-27 | A non-product solution still produces a PRD. | agreed |
| R-29 | A bet picked up downstream gets its own milestone, linked back to the demand's milestone. | agreed |
| R-30 | Codex hooks (repo-level) run the validator: PreToolUse blocks rule-breaking label changes, Stop runs drift checks. Format verified against the Codex docs. | agreed |
| R-31 | Model routing: authors and reviewers on different models; mixed scorer panel. | proposed |
| R-32 | Intake evidence: every cited E-id is recorded and every recorded one is cited. Intake scores are a single-agent baseline (Spread 0). | agreed |
| R-33 | `scripts/upstream_ops.py` is the only write path for contract lines after intake. | agreed |
| R-34 | The initiative branch is created automatically by `create_initiative.py --apply`. | agreed |
| R-35 | Reviewers and scorers are read-only; the orchestrator records their verdicts through `upstream_ops`. | agreed |
| R-36 | An open decision needs no `decisions/D-nnn.md` until it is recorded. | agreed |
| R-37 | Scripts handle mechanics only. Routing and process judgment live in skill text; `reconcile.py` reports facts and obligations, never a layer order. One-sentence checks are left to the reviewer. | agreed |
| R-38 | A decision lives in the issue that requested it: request comment → the PM's `/decide` → record comment, plus a Decisions checklist in the issue body. No decision issues. Agent comments start with a `## ` title. | agreed |
| R-39 | One `human:` label per issue (pending while anything waits, otherwise decided); `fix-labels` repairs disagreements from the comments and says so. | agreed |
| R-40 | Agents are **Enceladus**: every agent comment carries the invisible `<!-- enceladus:<role> -->` marker. A PM answer typed in Codex is relayed verbatim (`relay-decide`) without it. | agreed |
| R-41 | The issue is self-contained: drafts are reviewed before the PM decides; requests carry a Context and short options; `summary` keeps the epic body current; `checkpoint` pushes work before stopping. | agreed |
| R-28 | Grounding is capped at 5 when a layer rests mostly on bets. | agreed |

## Out of scope for v1

- The Product Designer's own process, to be added later.
- Downstream work: design refinement, edge cases and development.
- A hub initiative issue (deferred to v2).
- The implementation of agents, skills, scripts and Actions. This spec comes first.
