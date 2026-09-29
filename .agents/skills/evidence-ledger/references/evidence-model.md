# Evidence model

## Tipos

- `fact`: observado/documentado diretamente.
- `hypothesis`: relação esperada e refutável.
- `assumption`: premissa necessária ainda não evidenciada.
- `inference`: conclusão derivada, não observação direta.
- `decision`: escolha aceita; não prova causalidade.
- `unknown`: pergunta aberta.

## Evidence Record

```yaml
id: E-001
claim: "..."
kind: fact | hypothesis | assumption | inference | decision | unknown
source:
  type: analytics | interview | repository | github | notion | web | experiment | prototype | observation
  uri: "..."
  retrieved_at: "YYYY-MM-DD"
scope:
  population: "..."
  time_window: "..."
freshness: current | stale | unknown
relationship: supports | contradicts | does-not-resolve
criticality: critical | supporting
status: evidenced | inferred | unverified | refuted
limitations:
  - "..."
```

Claim crítica só fecha Knowledge quando a evidência é adequada à população,
janela e decisão. Contagem de fontes não é proxy de conhecimento.
