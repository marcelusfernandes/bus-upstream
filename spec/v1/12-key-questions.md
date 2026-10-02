# 12 — Key questions

These questions are the core of the process. The agents work to answer them, and the
junior PM learns product sense from them. The set is **small on purpose**: the first
version of the process failed because it had many questions, most of which could not
be answered when they were asked, so people filled in fields instead of thinking.

## Rules

- **One-sentence statements.** B1, U1 and S2 are each answered in **one sentence**
  that explains the matter clearly. Test: could a stakeholder repeat it after hearing it
  once? The detail goes in the answer file behind the ID, never in the sentence itself.
- **Three honest answer states**:
  - `evidenced`: there is a source.
  - `bet`: explicitly assumed, with an owner.
  - `open`: unknown, marked as blocking or not.

  A bet is a legitimate answer (the ~70% rule). A field filled in just to complete the
  template is not.
- **Grounding cap.** If most of a layer's answers are `bet`, its Grounding score is
  capped at 5, whatever its Definition score.
- **Who answers.** Every question is tagged with who can answer it, so the PM is only
  asked for what only people can provide:
  - 🔎 **agent**: research, data, evidence.
  - 🗣 **PM homework**: only people have it (stakeholder intent, internal context).
    The agent drafts candidates; the PM confirms, often in a meeting.
  - ⚖️ **gate**: a human decision (see [01-process.md](01-process.md#human-decisions)).
- **Propose, don't ask.** The agent never sends the PM an open question. It proposes
  candidate answers with a recommendation, and the PM picks one or proposes something
  else. This applies to PM homework as well as to gates.
- **Agent-only probing.** Techniques such as asking "why" repeatedly or separating a
  surface complaint from the root problem are instructions for the agent. They are
  never shown to the PM as extra questions.

## Business: define the business problem

| ID | Question | Answered when | Who |
|---|---|---|---|
| B1 | **What is the business problem?** | One sentence naming the outcome at stake and what is going wrong, in business terms: revenue, cost, risk, obligation or strategy | 🗣 → ⚖️ gate 1 |
| B2 | How do we know it exists? | A current value or observation, with its source, population and time window | 🔎 |
| B3 | How will we know we succeeded? | **One primary** metric or success description, with direction, target and timeframe, plus the **guardrails** that must not get worse. The agent proposes options; the PM picks one or proposes another | 🔎 → 🗣 |
| B4 | Why is it relevant now? | A trigger or context that makes it matter now, and what happens if we wait | 🗣 |
| B5 | Which hypotheses came from the business? | Every user-problem, solution and causal hypothesis that arrived with the demand or came up with stakeholders is registered with its origin and routed to the layer that will test it | 🔎 🗣 |

Anti-patterns:
- B1 written as a feature ("we need X").
- B1 written as a user problem ("users find it confusing"). That belongs in U, registered as a hypothesis.
- B3 written as an output ("launch X") instead of an outcome.

## User: define the user problem

| ID | Question | Answered when | Who |
|---|---|---|---|
| U1 | **What is the user problem?** | One sentence that explains the root problem, with no solution inside it. Who is affected, the situation, and the root versus the symptoms go in the answer file | 🔎 → ⚖️ gate 2 |
| U2 | How do we know it is real? | Evidence that fits the affected population, plus its magnitude (how many people, how often) | 🔎 |
| U3 | **B→U:** if we solve it, how does the business problem move? | The mechanism is stated, with a confidence level and what would prove it wrong | 🔎 |
| U4 | What happened to the hypotheses? | Every user-problem hypothesis routed to U is resolved with evidence. New solution hypotheses raised by users are registered and routed to S | 🔎 |

Anti-patterns:
- U1 as an opinion ("the site is bad") instead of a behavior ("the next screen was blank").
- U1 with a solution inside ("users need a faster checkout").
- A business hypothesis dropped without an explicit resolution.

## Solution: define the solution

| ID | Question | Answered when | Who |
|---|---|---|---|
| S1 | Which options were considered? | Genuinely different mechanisms, including non-product ones (process, operations, communication), **every inherited solution hypothesis**, and "don't do it". Each one is chosen, discarded or parked, with a reason | 🔎 |
| S2 | **What is the solution?** | One sentence stating the chosen bet, plus the **U→S** link: why it solves U1, a confidence level, and a stop signal ("we stop if…") | 🔎 → ⚖️ gate 3 |
| S3 | What is it not? | Scope and non-goals clear enough that the designer does not have to guess | 🔎 |
| S4 | What is the high-level How, and what must be true for it to work? | An approach sketch, plus **derived hypotheses** (value, usability, feasibility, viability), each with how it could be tested. They go to design as things to validate downstream | 🔎 |

Anti-patterns:
- Options that are cosmetic variations of the same mechanism.
- S2 that restates the business demand without the U→S reasoning.
- S4 that turns into flows, screens and edge cases. Those belong downstream.

A non-product solution still produces a PRD. The PRD describes what will be done and
why, whoever does it.

## Hypothesis register

Hypotheses can come from any layer. They are registered where they appear, routed
to the layer that can test them, and closed explicitly. **A stakeholder's hypothesis is
never silently dropped.**

| Field | Values |
|---|---|
| ID | `H-nn` |
| Statement | The hypothesis, in the words of whoever raised it |
| Kind | `user-problem`, `solution`, `causal` |
| Origin | Who raised it and where (stakeholder role, meeting, research, agent, designer) |
| Basis | The evidence IDs it came from, or `guess`. Required when the origin is `agent`. A guess is allowed, but it must be labeled as one |
| Raised at | B, U or S |
| Routed to | The layer that must test it |
| Status | `open`, `validated`, `invalidated`, `reframed → H-xx`, `merged → H-xx`, `parked` |
| Resolution | Evidence or decision IDs, plus a one-line reason |

There are two flows:
- **Inherited hypotheses** are raised in B or U and resolved in U4 or S1.
- **Derived hypotheses** come out of the chosen solution in S4 and are handed to design.

`reframed` keeps the link to the original idea, so a stakeholder can see that their
idea evolved rather than being rejected. `merged` and `parked` keep the register
manageable when stakeholders bring many ideas at once.

**Rule:** a layer cannot reach `state:done` while a hypothesis routed to it is still `open`.
