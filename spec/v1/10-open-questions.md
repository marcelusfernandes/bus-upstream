# 10 — Open questions

| ID | Question | Notes |
|---|---|---|
| Q-04 | Should a hub initiative issue be added in v2? | Deferred. Revisit if the README reading order turns out not to be enough as the cross-layer story. |
| Q-06 | Where does the Product Designer's own process plug in? | Deferred; to be considered further. The User layer is the natural point. |
| Q-09 | Which agent identity is used on GitHub? | Not a concern for now. Decisions are traced through `human:decided` and the PM's own comment. |
| Q-11 | Model routing (R-31): does it hold on the golden case and on the account's available models? | Proposed table in 03-agents.md. |
| Q-12 | Where do link scores (B→U, U→S) live? 02-scoring says links get two scores, but v1 has no link issue. | Candidate: the U epic carries the B→U scores and the S epic carries the U→S scores, as a second header line. The validator does not check link scores yet. |
| Q-13 | Can the intake agent run `create_initiative.py --apply` under `sandbox_mode = "workspace-write"`? It needs network for `gh`. | Unverified. If the sandbox blocks network, the agent plans and the PM (or orchestrator) applies. Check on the first real run. |
