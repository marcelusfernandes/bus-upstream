---
name: solution-work
description: Use quando Problem está suficientemente pronto e é preciso explorar, definir ou validar a intervenção nos modos explore, shape ou validate.
---


# Solution Work

Leia `references/matrix-and-gates.md`.

## mode=explore — Vague + Unknown

Gere mecanismos diferentes, não variações cosméticas da mesma feature.
Para cada opção: mecanismo, por que ataca o problema, trade-offs, assumptions,
reversibilidade e constraints. Registre alternativas descartadas.

## mode=shape — Vague + Known

Torne explícitos: mechanism, happy path, states, business/product rules,
edge cases, fallbacks, non-goals, metrics/observability, critical assumptions.
Separe **product/design rules** de **technical suggestions**.

## mode=validate — Concrete + Unknown

Ataque assumptions críticas de value, usability/comprehension, technical
feasibility, operation/performance/cost e riscos relevantes. Status por
assumption: `supported | refuted | unresolved | accepted-risk`.

