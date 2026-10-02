# 05 — Folder contract

Files hold the **details** behind what GitHub summarizes. Reading follows zoom levels:
an agent starts at the top and goes deeper only when it needs to.

```
initiatives/<slug>/
  README.md               L1  reading order + the cross-layer story (orchestrator)
  intake.md               L1  literal demand + fragments per layer + initial scores (intake)
  business/
    README.md             L2  current distilled answer of the layer (lead)
    answers/B-01.md       L3  question · answer · reasoning · evidence IDs (lead)
    evidence/E-001.md     L4  one evidence record per file (collectors)
    review.md                 adversarial reviews, newest first (reviewer, read-only elsewhere)
  user/                       same shape
  solution/
    README.md
    answers/
    bets/S-A/README.md        one folder per bet from day one
    evidence/
    review.md
  decisions/D-001.md          mirror of the decision issue + the PM's words + link
  learnings.md                invalidated assumptions, errors, dead ends (append-only)
  prd/README.md               the PRD (PRD writer)
```

## Rules

- **Single writer per path.** Each agent writes only the paths listed for it in
  [03-agents.md](03-agents.md). Reviewers never edit what they review.
- **Review wins.** A layer `README.md` must not contradict its `review.md` unless newer
  evidence is cited.
- **Evidence record fields:** id, claim, kind (fact, hypothesis, assumption,
  inference, decision, unknown), source (type, uri, retrieved_at), scope (population,
  time window), freshness, relationship (supports, contradicts, does-not-resolve),
  limitations, and what it does **not** allow us to conclude.
- **learnings.md** is append-only. Each entry has: date, ID affected, what we believed,
  what invalidated it, what to do differently. Later it can be aggregated across
  initiatives to find recurring wrong assumptions and gaps in how agents are piloted.
- Cross-initiative indexes are **generated** by a script, never edited by hand, to
  avoid merge conflicts between parallel branches.
