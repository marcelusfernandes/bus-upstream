# Product Upstream — Codex-native scaffold

Scaffold para testar um processo agentic de upstream de Product Design / Product
Management **sem usar o runtime do lohra-ts**.

O `lohra-ts` entra apenas como referência das práticas de development workflow:
issue-first, milestone como PRD, sub-issues, registros de decisão, human gates,
labels e revisão independente.

A execução do upstream é Codex-native:

- `AGENTS.md` prende invariantes e o loop autônomo;
- `.codex/agents/*.toml` define papéis especializados;
- `.agents/skills/*/SKILL.md` contém procedimentos reutilizáveis;
- GitHub issues, milestones, labels e comentários tornam o estado visível;
- scripts pequenos validam apenas regras mecânicas;
- **não existem workflows JSON do Lohra nem chamadas ao runtime Lohra**.

## Matriz

### Problem

| Definition \\ Knowledge | Unknown | Known |
|---|---|---|
| Concrete | Investigate | Ready |
| Vague | Explore | Frame |

### Solution

| Definition \\ Knowledge | Unknown | Known |
|---|---|---|
| Concrete | Validate | Deliver |
| Vague | Explore | Shape |

O processo não exige percorrer os quadrantes em uma ordem fixa. O orchestrator
identifica o **gap epistemológico atual** e carrega a skill adequada.

## Estrutura

```text
.
├── AGENTS.md
├── .codex/agents/
│   ├── upstream_orchestrator.toml
│   ├── evidence_researcher.toml
│   ├── product_builder.toml
│   ├── upstream_reviewer.toml
│   └── delivery_spec_writer.toml
├── .agents/skills/
│   ├── upstream-assess/
│   ├── evidence-ledger/
│   ├── problem-work/
│   ├── solution-work/
│   ├── decision-record/
│   ├── readiness-review/
│   └── delivery-package/
├── .github/ISSUE_TEMPLATE/
│   ├── upstream.yml
│   ├── decision.yml
│   └── delivery.yml
├── docs/upstream/
├── templates/
├── evals/usual-basket/
└── scripts/
```

## Model routing inicial

- `upstream_orchestrator` → `gpt-6-astra`, high
- `evidence_researcher` → `gpt-5.6-luna`, xhigh
- `product_builder` → `gpt-5.6-sol`, high
- `upstream_reviewer` → `gpt-5.6-sol`, high
- `delivery_spec_writer` → `gpt-5.6-sol`, medium

A intenção do V0 é usar o modelo mais forte nos pontos de framing, síntese,
decisão e revisão, mantendo pesquisa delimitada em um modelo rápido.

## Quick start

### 1. Validar o scaffold

```bash
python3 scripts/validate_scaffold.py
```

### 2. Criar os labels no GitHub

Dry-run:

```bash
python3 scripts/bootstrap_labels.py
```

Aplicar no repositório atual:

```bash
python3 scripts/bootstrap_labels.py --apply
```

### 3. Testar o golden case

Abra Codex na raiz e use:

```text
Trabalhe o caso evals/usual-basket/input.md seguindo AGENTS.md.
Use evals/usual-basket/evidence.md como a evidência disponível.
Não leia expected-trajectory.md antes de terminar a primeira classificação.
Mostre Problem e Solution iniciais e execute apenas o próximo trabalho necessário.
```

Depois compare com `evals/usual-basket/expected-trajectory.md`.

## Condição de saída

O upstream termina somente com:

```text
Problem = Ready
Solution = Deliver
Readiness = approved
```

O handoff gera um pacote de delivery; o upstream não implementa o produto.
