---
name: readiness-review
description: Use somente quando Problem=Ready e Solution=Deliver são alegados; faz revisão adversarial antes do handoff para delivery.
---


# Readiness Review

Você não melhora o package. Você tenta refutá-lo.

Problem: current state, population/context, problem statement sem solução,
claims evidenciadas, critical unknowns, outcomes/métricas, out-of-scope.

Solution: mechanism, flow/states, rules, edge cases/fallbacks, constraints,
critical assumptions, observability, riscos e separação product rule × technical suggestion.

Governance: decisões registradas, human gates resolvidos, freshness adequada,
nenhuma claim crítica dependente apenas de inferência.

Saída:
```json
{
  "verdict": "approved|rejected",
  "blocking": ["..."],
  "return_to": "none|problem-explore|problem-frame|problem-investigate|solution-explore|solution-shape|solution-validate|human-gate",
  "evidence": ["E-..."],
  "limitations": ["..."]
}
```

