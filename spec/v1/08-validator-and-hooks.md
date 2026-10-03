# 08 — Validator and hooks

Both reference repositories (lohra-ts and Apollo) define rules in writing and enforce
almost none of them, and both have drifted. Examples: issues missing state labels, a
written blocking rule contradicted in practice, stale docs, skill copies that differ.
Writing a drift rule down does not detect drift; something has to run the check.

## Checks

The validator is a single script, `scripts/upstream_validate`:

1. **IDs resolve both ways.** Every ID cited on GitHub exists in a file (always checked;
   a decision with a request but no record yet needs no file until it is recorded). Every ID defined in a file is
   cited on GitHub, but that direction is checked only at handoff (`--final`): mid-process,
   drafts and fresh evidence legitimately exist before anything cites them.
2. **Verdicts match.** A decided answer or review has the same verdict in the comment
   and in the file.
3. **Exclusive label families** have at most one value.
4. **`state:blocked` implies `human:pending`.**
5. **No state advances while `human:pending` is open** on the issue (a decision there waits for the PM).
6. **Anti-loop is enforced, not just documented.** A third attempt at the same question
   without a new `E-` ID is rejected.
7. **Score header format is valid**, and every header change has a matching
   score-change comment.
8. **Commit format.** Answer commits have the ID title pattern and the required trailers.
9. **Decision authorship.** An issue labeled `human:decided` has a valid `/decide` from its
   assigned PM on that same issue, before the label change. Comments starting with a `## `
   title are agents' and never count.
10. **No silent hypotheses.** A layer epic cannot be `state:done` while any hypothesis routed
    to it is `hyp:open`. Every closed hypothesis has a closing comment with a status and a reason.

## Where it runs

| Trigger | Checks | Catches |
|---|---|---|
| `commit-msg` git hook | 8 | Malformed answer commits, locally |
| GitHub Action on `issues`, `issue_comment` and `labeled` events | 3, 4, 5, 6, 7, 9, 10 | Changes from humans and agents on GitHub |
| Codex `PreToolUse` hook (repo-level) | 3, 4, 5, 10 | **Blocks** an agent's `gh` label change that would break a rule, before it runs |
| Codex `Stop` hook (repo-level) | 1, 2 | Drift left at the end of an agent turn; blocking it makes the agent keep going and fix it |
| Orchestrator reconcile (each run) | all | Drift between files and GitHub |
| PR check at handoff | all | Drift before the merge into main |

### Codex hooks

Format checked against the Codex hooks reference (https://learn.chatgpt.com/docs/hooks)
on 2026-10-02. Implemented in `.codex/config.toml` and `scripts/codex_hooks.py`.

- `PreToolUse` with matcher `Bash` reads `tool_input.command`. For every
  `gh issue edit N --add-label/--remove-label`, it loads the initiative's snapshot,
  simulates the change, and blocks (exit 2, reason on stderr) when the change would add a
  validator error. It always blocks an agent from adding `human:decided`.
- `Stop` runs the drift checks (1, 2) over every `initiatives/<slug>/` that has a
  milestone. It blocks once; when `stop_hook_active` is true it lets the turn end, so it
  never loops.
- The hooks **fail open**: if GitHub cannot be reached, they say so on stderr and allow
  the action. A broken hook must not stop all agent work. The Action, the reconcile and
  the PR check still catch the problem.
- They load only after the project `.codex/` layer is trusted and the hooks are reviewed
  with `/hooks`.
- Hooks only see **agent** actions. Human changes on GitHub are covered by the Action.
- `scripts/upstream_ops.py` calls `gh` from Python, so the `PreToolUse` hook does not
  see those calls. That is intended: its plans refuse rule-breaking writes before they
  happen. The hook catches agents that bypass the helper with `gh issue edit`.

The Action **validates** the score header. It does not sync it to labels, because
scores are never labels.
