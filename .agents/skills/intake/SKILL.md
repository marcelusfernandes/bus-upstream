---
name: intake
description: Use when a new stakeholder demand arrives, to turn it into a BUS initiative (literal demand, context, per-layer fragments and scores, registered hypotheses) and create its milestone, epics and folder skeleton. Not for researching or answering any layer.
---

# Intake

References: `spec/v1/01-process.md` (Intake), `spec/v1/02-scoring.md`,
`spec/v1/12-key-questions.md`, and `templates/intake.example.json` for the exact shape (its content is only an illustration;
never borrow its domain).
The JSON needs the PM's GitHub login (`pm`): every decision is assigned to it.

## Steps

1. **Preserve the demand literally.** Copy it as it arrived, with no rewording.
2. **Gather context**: the product, the journey step, and any comparison the demand
   makes. If nothing says otherwise, assume the App and write that down. Keep `context`
   short. When the context is genuinely ambiguous, say so in one line and list it in your
   report as the first decision the orchestrator should request; never ask an open question.
3. **Split the demand into fragments per layer** (B, U, S). One sentence often contains
   all three: a solution, a business outcome and an open question.
4. **Register hypotheses.** Every user-problem, solution or causal claim that arrived
   with the demand becomes an `H-nn` entry with its origin (who and where) and is routed to
   the layer that can test it. If you raise one yourself, set `origin: agent` and give a
   `basis` (evidence IDs or `guess`). Write `origin` in words (who, and where it came up),
   never a file path: a PM on GitHub cannot open it. Give each hypothesis a `test`: what
   would validate or invalidate it, in one line.
5. **Record evidence you cite.** Each `E-nnn` gets a claim, kind, source and layer, plus
   population, time window, freshness and limitations when known. Never cite an ID you did
   not record, and never record one you do not cite.
6. **Score each layer** on Definition and Grounding, using the 0/5/10 anchors only. In
   `why`, say why the score is not closer to the other extreme. Grounding is about the
   layer's statement: with no statement yet it stays low, and a `decision` (what someone
   wants) is not evidence that a problem exists. A solution-shaped demand
   usually means S has high Definition and low Grounding, and B and U are low.
7. **Write each statement as one sentence**, or `null` when it cannot be written yet. A
   null statement is the expected result for most demands.
8. **Validate and plan:**
   `python3 scripts/create_initiative.py <intake.json>`. It prints the plan or the
   validation errors. Fix errors in the JSON, never in the script.
9. **Create the initiative:** `python3 scripts/create_initiative.py <intake.json> --apply`.
   It first switches to the initiative's own branch `upstream/<slug>` (created from an
   updated `main`; the PM never does this). Then it creates the milestone (holding the
   intake snapshot), the B/U/S/PRD epics with score headers and first score comments,
   the hypothesis sub-issues and `initiatives/<slug>/`, and finally commits and pushes the
   branch. It refuses to start with uncommitted changes.
10. **Stop.** Report the milestone number and anything the PM must decide first (as
    proposed options), then hand over to the orchestrator.

## Never

- Rewrite the demand into a problem statement, or a solution into a user problem.
- Drop a stakeholder hypothesis because it looks wrong. Register it; the layer tests it.
- Fill a field just to complete the template. `null` or `open` is an honest answer.
