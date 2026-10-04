# 10 — Open questions

| ID | Question | Notes |
|---|---|---|
| Q-04 | Should a hub initiative issue be added in v2? | Deferred. Revisit if the README reading order turns out not to be enough as the cross-layer story. |
| Q-06 | Where does the Product Designer's own process plug in? | Deferred; to be considered further. The User layer is the natural point. |
| Q-09 | Which agent identity is used on GitHub? | Agents comment with the PM's own account today. Current mitigation: the invisible Enceladus marker on every agent comment (R-40). A separate bot identity (GitHub App or machine user named Enceladus) would make authorship unambiguous. |
| Q-11 | Model routing (R-31): does it hold on the golden case and on the account's available models? | Proposed table in 03-agents.md. |
| Q-12 | Where do link scores (B→U, U→S) live? 02-scoring says links get two scores, but v1 has no link issue. | Candidate: the U epic carries the B→U scores and the S epic carries the U→S scores, as a second header line. The validator does not check link scores yet. |
| Q-13 | Can the intake agent run `create_initiative.py --apply` under `sandbox_mode = "workspace-write"`? It needs network for `gh`. | Unverified. If the sandbox blocks network, the agent plans and the PM (or orchestrator) applies. Check on the first real run. |
| Q-14 | All agents are built (R-43, R-44). | Next: the Product Designer's own process (Q-06). |
| Q-15 | Can a Codex subagent (`business_lead`) dispatch another subagent (`collector`)? | Unverified. The skill has a fallback: return the bounded questions to the orchestrator, which dispatches collectors. |
| Q-16 | Decision authorship is checked against the issue's *current* assignees. If the PM is later unassigned, past records would fail check 9. | Not fixed yet. Option: accept a `/decide` whose author is the one named in the record (`Decided by: @x`). |
