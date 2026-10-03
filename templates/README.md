# Templates

These templates define what agents write on GitHub and in `initiatives/<slug>/`. The
validator parses the same lines: `scripts/upstream_contract.py` holds the regexes, and
`tests/test_contract.py` fails if a template stops matching them.

| File | Used by | For |
|---|---|---|
| [epic-body.md](epic-body.md) | intake, orchestrator | Body of each B/U/S layer epic |
| [decision-request.md](decision-request.md) | leads, orchestrator | Decision request **comment** on the issue that needs the decision |
| [hypothesis-body.md](hypothesis-body.md) | intake, leads | Body of a hypothesis sub-issue |
| [comments.md](comments.md) | all agents | Comment title patterns |
| [hypotheses-register.md](hypotheses-register.md) | leads, orchestrator | `initiatives/<slug>/hypotheses.md` |
| [review-file.md](review-file.md) | reviewers | `initiatives/<slug>/<layer>/review.md` |
| [answer.md](answer.md) | leads | `initiatives/<slug>/<layer>/answers/<ID>.md` |

## Who writes what

- **Everything below is written through `scripts/upstream_ops.py`**, never by hand.
- **Score header:** the orchestrator (`upstream_ops score`). It updates the header line
  in the epic body **and** posts the score-change comment in the same action. The header
  always equals the latest score comment (validator check 7).
- **Labels:** the orchestrator, except `human:decided`, which the `/decide` GitHub
  Action applies when the assigned PM decides.
- **Decisions:** comments in the issue that needs them (`decision-request.md`), never a
  separate issue. Every agent comment carries the invisible `<!-- enceladus:<role> -->`
  marker.
- **Answers:** `answer.md` (its first three lines feed the epic summary).
- **Review comments and `review.md`:** the orchestrator records the read-only
  reviewer's verdict (`upstream_ops review`). The comment and the file carry the same
  title line (check 2).
- **Hypothesis closing comment and the `hypotheses.md` row:** the lead that resolved
  the hypothesis (`upstream_ops hypothesis-close`). The status must match in both places (check 2), and it must match the
  `hyp:` label (check 10).

## Rules carried from the spec

- B1, U1 and S2 answers are **one sentence**.
- IDs are used verbatim everywhere: `B-01`, `U-02`, `S-01`, `D-001`, `E-001`, `H-01`.
- Agents propose options. They never ask the PM an open question.
