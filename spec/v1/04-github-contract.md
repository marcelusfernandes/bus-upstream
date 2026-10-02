# 04 — GitHub contract

GitHub issues, comments and labels are the **main source of truth** and the
**reading starting point**. Files hold the details (see [05-folder-contract.md](05-folder-contract.md)).
If a file and a comment disagree, a drift has happened (see [08-validator-and-hooks.md](08-validator-and-hooks.md)).

## Structure (v1)

```
Milestone  <demand title>          description = static intake snapshot
├─ Epic  B · Business problem      layer state + score header
│   └─ sub-issues: questions (B-nn), evidence tasks, decisions (D-nnn)
├─ Epic  U · User problem
├─ Epic  S · Solution              bets as sub-issues later (S-A, S-B…)
└─ Epic  PRD
```

- **Milestones have no comments and no labels.** The milestone description holds the
  intake snapshot and is never edited after intake. It serves as the baseline for comparison.
- There is no hub issue in v1. The cross-layer story is the initiative `README.md`
  reading order, linked from the milestone description.

## Labels

At most **one value per exclusive family**. Different families can combine freely.

| Family | Values | Exclusive | On |
|---|---|---|---|
| `layer:` | `business`, `user`, `solution`, `prd` | yes | epics and their sub-issues |
| `state:` | `ready`, `in-progress`, `in-review`, `qa-failed`, `blocked`, `done` | yes | epics and sub-issues |
| `type:` | `question`, `evidence`, `decision`, `review`, `hypothesis` | yes | sub-issues |
| `hyp:` | `open`, `validated`, `invalidated`, `reframed`, `merged`, `parked` | yes | hypothesis sub-issues |
| `human:` | `pending`, `decided` | yes | decision sub-issues (piloted mode) |
| `agent:` | `decided` | — | decision sub-issues decided by the agent (autonomous mode) |
| `mode:` | `piloted`, `autonomous` | yes | epics (same on all epics of a milestone) |
| `epic` | — | — | the four epics |

## Layer lifecycle

The `state:*` names are reused from lohra-ts and Apollo so people and tooling carry
over. Their meaning is adapted for upstream:

| State | Meaning |
|---|---|
| `state:ready` | Created by intake, work not started |
| `state:in-progress` | The lead and its subagents are working |
| `state:in-review` | The isolated reviewer is checking an answer or a fit |
| `state:qa-failed` | The review rejected it; back to work, with the reasons in a comment |
| `state:blocked` | Anti-loop triggered. **Always** together with `human:pending`. |
| `state:done` | Answered well enough for dependent layers to rely on. **Can be reopened.** |

**Reopen rule:** `done` → `in-progress` is allowed when an answer is invalidated. The
reopening comment cites the invalidated ID and the evidence or decision that
invalidated it. These comments are the trail of wrong assumptions.

No state may advance while the issue has an open `human:pending` decision.

A layer epic cannot reach `state:done` while a hypothesis routed to it has `hyp:open`.

## Hypotheses

Each hypothesis is a sub-issue labeled `type:hypothesis` + `hyp:open`, placed under the
epic of the layer it is **routed to**. Its body holds the register fields (see
[12-key-questions.md](12-key-questions.md#hypothesis-register)). It is closed with a comment:

```
## Hypothesis H-03 · invalidated | validated | reframed → H-07 | merged → H-02 | parked
Why: <one line>
Evidence: E-… · Decision: D-… (if any)
```

Filtering `type:hypothesis` with `hyp:open` shows which stakeholder ideas are still
waiting for an answer.

## Human decisions

1. The agent opens a **decision sub-issue** with `type:decision` and `human:pending`,
   assigned to the PM. Its body: Question / Recommendation / Why / Trade-offs /
   Reversibility / What would change the recommendation / Evidence IDs / Blocks.
2. The **PM decides with a `/decide` command in their own comment**. An agent
   transcribing a decision made elsewhere does not count.

   ```
   /decide A
   Why: <PM's reasoning, optional but encouraged>
   ```

   From another issue (for example the epic): `/decide D-004 A`.
   To propose something not on the list: `/decide other: <the PM's own option>`.
3. A **GitHub Action** handles the comment:
   - `/decide` from the assigned PM → swaps `human:pending` → `human:decided` (permanent)
     and triggers the orchestrator, which posts the decision record and closes the issue.
     A `/decide D-nnn` posted elsewhere is applied to D-nnn, with a link back.
   - Any other comment from the PM on a pending decision (a clarification, a new
     option) → the Action does nothing; the label stays pending. The orchestrator runs
     locally, so the Action cannot trigger it: the orchestrator's reconcile finds PM
     comments newer than its last reply on a pending decision and answers them.
   - `/decide` from anyone other than the assignee → ignored, with a reply explaining why.

In **autonomous mode** the agent decides, posts the same record, and labels the issue
`agent:decided`. Filtering `human:decided` vs `agent:decided` shows who made each decision.

Decision comment title, which must be matchable by regex:

```
## Decision D-004 · U-02 · <answer in one line>
```

Regex: `^## Decision D-\d{3} · (?:[BUS]-\d{2}|BU-fit|US-fit) · .+$`

## Comment patterns

All agent comments start with a title line. The title is what lets a reader skim the
issue as a story.

### Answer comment

```
## Answer U-02 · <answer in one line>
Why: <one line>
Evidence: E-005, E-007 · Decision: D-004 (if any)
Detail: <link to file>
```

### Score change comment

The orchestrator updates the epic's score header **and** posts this comment in the same
action. Intake posts the first one (`Definition – → n`). The header always equals the
latest score comment.

```
## Score · U · Definition 4 → 7 · Grounding 3 → 6
Why: <one line per axis, including why not closer to the other extreme>
Based on: U-02, E-005, E-007 · Spread: 1
```

### Review verdict comment

```
## Review · U-02 · approved | rejected
Blocking: <list or none>
Return to: <layer/question or none>
Detail: <link to review.md>
```

### Reopen comment

```
## Reopened · U-02 invalidated by E-012
What changed: <one line>
```

**Content rule:** the comment holds the answer or decision, a one-line why, the IDs
and a link. The file holds the detail. The IDs and verdicts must match between the two.

## IDs

| Prefix | Object |
|---|---|
| `B-nn`, `U-nn`, `S-nn` | Answered question in a layer |
| `BU-fit`, `US-fit` | Link fit reviews |
| `PRD` | Target of the final PRD review (`## Review · PRD · …`) |
| `S-A`, `S-B`… | Solution bets |
| `D-nnn` | Human decision |
| `E-nnn` | Evidence record |
| `H-nn` | Hypothesis (sub-issue under the epic of the layer it is routed to) |

IDs are unique within a milestone and are used verbatim in comments, files and commits.
