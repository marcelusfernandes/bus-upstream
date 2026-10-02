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
| `type:` | `question`, `evidence`, `decision`, `review` | yes | sub-issues |
| `human:` | `pending`, `decided` | yes | decision sub-issues |
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

## Human decisions

1. The agent opens a **decision sub-issue** with `type:decision` and `human:pending`,
   assigned to the PM. Its body: Question / Recommendation / Why / Trade-offs /
   Reversibility / What would change the recommendation / Evidence IDs / Blocks.
2. The **PM answers in their own comment**. An agent transcribing a decision made
   elsewhere does not count.
3. The agent posts the decision record, swaps the label to `human:decided` (it stays
   permanently), and closes the issue.

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
| `S-A`, `S-B`… | Solution bets |
| `D-nnn` | Human decision |
| `E-nnn` | Evidence record |

IDs are unique within a milestone and are used verbatim in comments, files and commits.
