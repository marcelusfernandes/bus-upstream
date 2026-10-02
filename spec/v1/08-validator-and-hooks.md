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
| Codex `PreToolUse` hook (repo-level) | 3, 4, 5, 10 | **Blocks** an agent's `gh` label change that would break a rule, before it runs |
| Codex `Stop` hook (repo-level) | 1, 2, 7 | Drift left at the end of an agent turn; blocking it makes the agent keep going and fix it |
| Orchestrator reconcile (each run) | all | Drift between files and GitHub |
| PR check at handoff | all | Drift before the merge into main |

### Codex hooks

Hooks are a stable feature in Codex CLI 0.160 (checked locally on 2026-10-02 with
`codex features list`). The event names and the config format below come from Codex's
own answer about its documentation. Verify them before implementing.

- Events used: `PreToolUse` (can **block** a tool call) and `Stop` (can block the end
  of a turn and ask the agent to continue). `SubagentStop` can also be used to validate
  a subagent's single-file return.
- Config lives at repo level in `.codex/config.toml` (or `.codex/hooks.json`), committed
  with the script. The project has to be trusted, and hooks reviewed through `/hooks`.
- A hook receives JSON on stdin. Exit code `2`, with a reason on stderr, blocks.
- Hooks only see **agent** actions. Human changes on GitHub are covered by the Action.

The Action **validates** the score header. It does not sync it to labels, because
scores are never labels.
