# [codex test] Usual basket

Milestone: #3
PM: @marcelusfernandes
Mode: piloted

## Reading order

1. `intake.md` — the literal demand and context
2. `hypotheses.md` — every hypothesis and its status
3. `business/README.md`, `user/README.md`, `solution/README.md` — current answer per layer
4. `prd/README.md` — the PRD, once written

## Checkpoint · 2026-10-03 · Business concluída

A direção explícita do PM determinou a escolha: trabalhar somente Business até `done` ou uma decisão pendente. A reconciliação final confirma **B: state:done**, sem divergências, obrigações mecânicas, decisões pendentes ou hipóteses abertas roteadas a B. U e S permanecem `ready`; seus problemas e soluções não foram desenvolvidos.

B-01 a B-04 permanecem conscientemente `open`, com razões e condições de reabertura, conforme D-004 A. B-05 está `evidenced` quanto à completude documental do registro; isso não demonstra a verdade das hipóteses nem um problema de conversão. O diagnóstico comparável exigido em D-003 continua obrigatório antes de solução, meta ou sucesso.

### Decisão aplicada

[D-005 no epic B #19](https://github.com/marcelusfernandes/bus-upstream/issues/19#issuecomment-5970310371): **Aceitar a lacuna de testes de B5 para concluir Business, completar o registro antes do fechamento ou estacionar B5 mantendo Business bloqueada?**

O PM já havia escolhido **B** no GitHub: formular critérios por hipótese, revisá-los independentemente, registrar Test pelo caminho autorizado e rever B5. Esta execução registrou e aplicou essa decisão. Nenhuma nova decisão foi solicitada e nenhuma permanece pendente.

### Trabalho e validação

O Business lead delegou ao collector a auditoria documental E-015, limitada às fontes permitidas. Os critérios de Test e a atribuição de Origin receberam revisão independente antes de quatro chamadas `hypothesis-update`. Os commits 129b729, d0568bb, e0dbd98 e b45a022 registram os reparos; a conferência do lead encontrou Test/Origin correspondentes nas issues e preservação dos demais campos do registro.

Uma revisão final rejeitou afirmações operacionais que seu corpus restrito não permitia verificar. O lead removeu essas afirmações de B-05; uma nova revisão independente aprovou a completude documental. A resposta foi registrada com D-005 no commit 39564d7. Os limites das revisões são documentais: não verificaram empiricamente hipóteses, autoria externa nem resultados de produto.

H-03 (custo) e H-04 (recorrência/AOV) já haviam sido encerradas via `hypothesis-close` como **parked**, sob D-004, por falta de definição/comparação de custo e de evidência dos efeitos exploratórios, respectivamente. Suas razões e condições de reabertura foram preservadas. Não se repetiu a operação de encerramento. H-01/H-02 continuam abertas em S/U; os critérios registrados não executam testes dessas camadas.

Painel isolado e paralelo: luna **5/2**, sol **4/1**, sol56 **5/2**. Medianas: Definition **5** (Concept), Grounding **2**; Spread **1**; todos `mostly_bets=false`. O registro mais completo não fornece baseline ou evidência causal. Scores são instruções de roteamento, não gates.

Fontes de evidência exclusivas: `evals/usual-basket/evidence.md` e arquivos da iniciativa. Nenhuma pesquisa web foi feita. **255 testes unitários passaram**; a reconciliação após `route --layer B --state done` ficou sem drift ou obrigações. O encerramento requer também `summary --layer B` e `checkpoint` para publicar este estado.

### Problemas observados nesta execução

- Permissões: `git switch` falhou inicialmente em `.git/index.lock`; funcionou com escalonamento autorizado. A primeira atualização de H-01 alterou arquivo/body antes de falhar no commit pela mesma restrição; a reexecução escalonada recuperou. O helper não foi atômico diante dessa falha de permissão.
- Escopo da revisão: o lead incluiu alegações sobre execução/commits/issues que o revisor limitado ao corpus documental não podia comprovar. A rejeição foi registrada e o texto corrigido; as observações operacionais ficam neste checkpoint, separadas da resposta documental.
- Registro de review: `upstream_ops review` não oferece campo `limitations`; o escopo das aprovações está explicitado neste checkpoint. A primeira aprovação foi dos critérios propostos; a aprovação final foi da completude documental.
- Apresentação: o resumo do epic mostra `not yet writable` como Statement enquanto B1 está `open`; sua linha na tabela e os arquivos preservam a formulação e o motivo.
- Uma chamada inicial de `upstream_ops.py --help` omitiu `--repo`; foi somente leitura de ajuda. Todas as operações de contrato usaram `--repo marcelusfernandes/bus-upstream` e a assinatura do papel responsável.

As limitações de helper/skill relatadas no checkpoint anterior sobre ausência de `hypothesis-update` e limites de specs não representam as capacidades verificadas nesta execução: o reparo autorizado funcionou sem alteração dos scripts ou skills.
