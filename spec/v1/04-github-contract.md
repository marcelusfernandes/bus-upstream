# 04 — GitHub contract

GitHub issues, comments and labels are the **main source of truth** and the
**reading starting point**. Files hold the details (see [05-folder-contract.md](05-folder-contract.md)).
If a file and a comment disagree, a drift has happened (see [08-validator-and-hooks.md](08-validator-and-hooks.md)).

## Structure (v1)

```
Milestone  <demand title>          description = static intake snapshot
├─ Epic  B · Business problem      layer state + score header
│   └─ sub-issues: questions (B-nn), evidence tasks, hypotheses (H-nn); decisions live as comments here
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
| `type:` | `question`, `evidence`, `review`, `hypothesis` | yes | sub-issues |
| `hyp:` | `open`, `validated`, `invalidated`, `reframed`, `merged`, `parked` | yes | hypothesis sub-issues |
| `human:` | `pending`, `decided` | yes, **one at most** | `pending` while a decision on the issue waits for the PM; otherwise `decided` once the PM decided there |
| `agent:` | `decided` | — | the issue holding a decision the agent made (autonomous mode) |
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
| `state:blocked` | Anti-loop triggered. **Always** together with `human:pending`; `upstream_ops route` adds it, and leaving `blocked` removes it. |
| `state:done` | Answered well enough for dependent layers to rely on. **Can be reopened.** |

**Reopen rule:** `done` → `in-progress` is allowed when an answer is invalidated. The
reopening comment cites the invalidated ID and the evidence or decision that
invalidated it. These comments are the trail of wrong assumptions.

No state may advance while a decision on the issue waits for the PM.

A layer epic cannot reach `state:done` while a hypothesis routed to it has `hyp:open`.

## Hypotheses

The hypothesis issue is self-contained (see `templates/hypothesis-body.md`): the hypothesis
as raised and who raised it, how it gets tested, its status and resolution, and its basis
with each evidence ID followed by its claim. `upstream_ops summary` refreshes these bodies
from the register and the evidence files.

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

**A decision lives inside the issue that requested it**, never in a separate issue, so
that issue tells the whole story in order (the same pattern as lohra-ts and Apollo):

```
## Decision request D-001 · B-01 · <question>      agent: options, recommendation, trade-offs
/decide A                                          the assigned PM, in their own comment
Why: <the PM's reasoning>
D-001 decided by @pm: A                            the /decide Action acknowledges
## Decision D-001 · B-01 · <answer>                agent: the record, quoting the PM
```

1. **Request.** `upstream_ops decision-open` posts the request comment on the issue that
   needs it (usually the layer epic), assigns the PM to that issue, adds `human:pending`
   (piloted mode), and adds `- [ ] D-001 · <question>` to the issue body's **Decisions**
   checklist. The answer it is about must already be drafted.
2. **The PM decides in their own comment:** `/decide A` (with `Why: …` on the next line),
   or `/decide other: <the PM's own option>`. When several decisions are waiting on the
   same issue, the PM names one: `/decide D-001 A`. Several can be answered in one comment
   (as in Apollo), one `/decide D-nnn <option>` line each, each followed by its own `Why:`.
3. **The `/decide` Action** (runs from `main`, reads the issue's comments):
   - A valid `/decide` from the assigned PM acknowledges. When it was the last decision
     waiting, it swaps `human:pending` for `human:decided`; while another still waits,
     `human:pending` stays (one `human:` label per issue). It never closes the issue.
   - A bare `/decide` with several decisions waiting, an unknown or already decided
     D-id, or an option that does not exist all get a reply, and nothing changes.
   - `/decide` from anyone other than the assignee gets a reply naming the assignee. Bots and
     non-collaborators are ignored silently.
   - Any other PM comment changes nothing. The orchestrator's reconcile finds it and
     replies with a `## Reply · D-nnn` comment (options and a recommendation, never an
     open question).
4. **Record** (Apollo's pattern). `upstream_ops decision-record` posts
   `## Decision D-001 · <ref> · <answer>` followed by one line that says it all:
   `Decision (@pm, <date>, recorded by Enceladus) — **D-001 → A: <option text>.** <the PM's why>. Unlocks: <what it was blocking>`.
   It ticks the checklist line (`- [x] D-001 · <question> → A: <option text> (@pm, <date>)`)
   and commits `decisions/D-001.md`.

**Agents are Enceladus, and every agent comment is signed.** Agents comment with the
PM's GitHub account today, so authorship cannot tell them apart. Every agent comment
carries the invisible marker `<!-- enceladus:<role> -->`, added by
`upstream_ops --agent <role>`. A comment with that marker (outside a quote) never counts
as a PM decision, so a PM who quote-replies an agent comment is still the PM. Comments
written before the marker existed are recognized by their `## ` title. Agent comments
never put `/decide` at the start of a line.

**One `human:` label per issue, and a guard.** An issue carries `human:pending` while any
decision on it waits for the PM, and `human:decided` once nothing waits and the PM has
decided there. A new request on a decided issue swaps it back to `pending`. The labels
follow the comments: if they disagree (for example, both labels present, or `pending`
after the PM decided everything), `upstream_ops fix-labels` sets the correct one in the
agent's next action and posts `## Labels fixed` saying what changed and why. The history
of decisions stays in the comments, the records and GitHub's label timeline.

**Deciding from Codex.** When the PM pilots the process in Codex, the agent shows the same
request there. If the PM types the answer in Codex, the agent posts it verbatim with
`upstream_ops relay-decide` as `/decide D-nnn <option>` plus `Why:`, the chosen option
written out (`Choice: <option> — <text>`), and the invisible `<!-- relayed-from:codex -->` note, with no Enceladus marker, because it is the PM's
decision. The agent never turns a PM's GitHub comment, or its own reading of the PM's
intent, into a `/decide`.

**The issue is self-contained.** A PM reading only GitHub must be able to decide. Each
request has its own **Context** (up to about three paragraphs: never cut what the PM
needs), a clear question, and options of a sentence or two each. Every epic (B, U and S) is self-contained from creation, and `upstream_ops summary`
keeps it current: statement, a link to the files on the branch, key questions with a
one-line answer and state, the hypotheses raised in or routed to the layer, and the
Decisions checklist. Before stopping, the agent runs
`summary` and `checkpoint`, so the drafts are pushed too.

In **autonomous mode** the agent decides with `decision-record --agent-choice`, posts the
same record, and labels the issue `agent:decided`. Filtering `human:decided` vs
`agent:decided` shows who decided where.

Regexes: request `^## Decision request D-\d{3} · (?:[BUS]-\d{2}|BU-fit|US-fit) · .+$`,
record `^## Decision D-\d{3} · (?:[BUS]-\d{2}|BU-fit|US-fit) · .+$`.

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
| `D-nnn` | Decision: a request comment and a record comment in the issue that needed it |
| `E-nnn` | Evidence record |
| `H-nn` | Hypothesis (sub-issue under the epic of the layer it is routed to) |

IDs are unique within a milestone and are used verbatim in comments, files and commits.
