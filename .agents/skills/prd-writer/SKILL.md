---
name: prd-writer
description: Use when Business, User and Solution are done, to compile the PRD from the committed layers. Writes initiatives/<slug>/prd/README.md only; invents nothing.
---

# PRD writer

Reference: `spec/v1/07-branching-and-handoff.md` (PRD content).

Read every committed answer (`business/`, `user/`, `solution/` and their `answers/`), the
recorded decisions (`decisions/`), `hypotheses.md`, the bets and the evidence. Write
`initiatives/<slug>/prd/README.md` in the PM's language, with these sections, in order:

1. **Business problem**: the statement (one sentence, or why it is still open), the
   baseline, the success signal (primary metric and guardrails), why it is relevant now.
2. **User problem**: the statement, who and in what situation, the evidence, how big it
   is, and whether it is evidenced or a bet.
3. **B→U link** and its confidence (from U3 and the BU-fit review).
4. **Solution**: the chosen bet (S2), the alternatives considered and why they were not
   chosen (S1), the high-level How (S4), and what it is not (S3).
5. **U→S link**: confidence and what would prove us wrong (the stop signal).
6. **Derived hypotheses to validate in design**, each with how it could be tested (S4).
7. **Stakeholder hypotheses and what happened to them**, from the register, each with its
   status and reason.
8. **Named bets and accepted risks**, with who accepted them and in which decision.
9. **Open questions handed to design**: everything upstream left open, with the reason.

Rules:
- Every claim cites its source ID (B-01, U-03, D-004, H-02, E-008…).
- No acceptance criteria, no files, no edge cases, no screens: those are downstream.
- Never fill a gap: if upstream did not decide it, it goes to section 9.
- A reader who sees only the PRD epic on GitHub must understand what will be designed,
  why, and how sure we are.

Return at most 15 lines: the sections written and anything you could not source.
