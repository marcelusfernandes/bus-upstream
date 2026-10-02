# 06 — Commit contract

Commits are **checkpoints**. Future agents read them to learn what happened and avoid
repeating failed approaches. A PM can roll back to one to try a different approach
from that point.

## One commit per decided answer

- **Title:** the answer ID and the answer in one line.
- **Body:** a short summary of the reasoning (how we got there) and the learnings
  (errors and discarded assumptions).
- **Trailers:** machine-readable lines at the end of the message, so agents can filter
  the history with `git log`.

```
U-02: Recurring buyers rebuild the same basket manually each week

Reasoning: three interview patterns plus reorder data; discarded "the app is
slow" (no latency evidence, E-007 contradicts it).
Learning: the initial framing assumed speed causes conversion; unsupported.

Layer: user
Definition: 4 -> 7
Grounding: 3 -> 6
Evidence: E-005, E-007
Decision: D-004
Invalidates: a1b2c3d
```

(The example is illustrative and not real data.)

## Rules

- A **high-impact answer** is committed only **after** the PM's decision, and the
  commit carries the `Decision:` trailer.
- An **invalidation** is a new commit with an `Invalidates: <sha>` trailer. History is
  never rewritten.
- Required trailers: `Layer`. Required when applicable: `Definition`, `Grounding`
  (when the scores changed), `Evidence`, `Decision`, `Invalidates`.
- Scaffolding and housekeeping commits that are not answers use `chore:` and skip the
  trailers.
