# Git/GitHub workflow do upstream

GitHub é a superfície visível do processo.

## Labels

Execução: use `state:*` do repositório.

Problem — exatamente um:
- `problem:explore`
- `problem:frame`
- `problem:investigate`
- `problem:ready`

Solution — exatamente um:
- `solution:explore`
- `solution:shape`
- `solution:validate`
- `solution:deliver`

Tipos sugeridos:
- `type:investigation`
- `type:framing`
- `type:design`
- `type:experiment`
- `type:decision`
- `epic`

## Transição

Toda troca `problem:*` ou `solution:*` recebe comentário usando
`templates/state-transition-comment.md`.

## Milestone

Milestone upstream é PRD curto: objective, starting hypothesis, outcomes,
entry state, critical unknowns, scope/out-of-scope, gates e exit criteria.
Fecha pelo critério, não pela contagem de issues.

## Epic/subissues

Iniciativa grande vira epic; decisões globais ficam na mãe; subissues reduzem
gaps independentes; achado fora de escopo vira follow-up com origem.

## Handoff

`problem:ready + solution:deliver + readiness approved` gera delivery tracking.
A partir daí segue o workflow de implementação do repositório.
