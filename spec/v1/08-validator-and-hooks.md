# 08 — Validator and hooks

Both reference repositories (lohra-ts and Apollo) define rules in writing and enforce
almost none of them, and both have drifted. Examples: issues missing state labels, a
written blocking rule contradicted in practice, stale docs, skill copies that differ.
Writing a drift rule down does not detect drift; something has to run the check.

## Checks

The validator is a single script, `scripts/upstream_validate`:

1. **IDs resolve both ways.** Every ID cited in a comment exists in a file, and every
   ID defined in a file is cited in a comment.
2. **Verdicts match.** A decided answer or review has the same verdict in the comment
   and in the file.
3. **Exclusive label families** have at most one value.
4. **`state:blocked` implies `human:pending`.**
5. **No state advances while `human:pending` is open** on the issue or its decision sub-issues.
6. **Anti-loop is enforced, not just documented.** A third attempt at the same question
   without a new `E-` ID is rejected.
7. **Score header format is valid**, and every header change has a matching
   score-change comment.
8. **Commit format.** Answer commits have the ID title pattern and the required trailers.
9. **Decision authorship.** A `human:decided` issue has a `/decide` comment from the assigned PM
   before the label change.
10. **No silent hypotheses.** A layer epic cannot be `state:done` while any hypothesis routed
    to it is `hyp:open`. Every closed hypothesis has a closing comment with a status and a reason.

## Where it runs

| Trigger | Checks | Catches |
|---|---|---|
| `commit-msg` git hook | 8 | Malformed answer commits, locally |
| GitHub Action on `issues`, `issue_comment` and `labeled` events | 3, 4, 5, 6, 7, 9, 10 | Changes from humans and agents on GitHub |
| Orchestrator reconcile (each run) | all | Drift between files and GitHub |
| PR check at handoff | all | Drift before the merge into main |

Agent harness hooks (for example, running the validator after a tool call) are
optional. Codex hook support has not been verified (see [10-open-questions.md](10-open-questions.md)).

The Action **validates** the score header. It does not sync it to labels, because
scores are never labels.
