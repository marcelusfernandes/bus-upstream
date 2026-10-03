# [codex test] Usual basket

Milestone: #3
PM: @marcelusfernandes
Mode: piloted

## Reading order

1. `intake.md` — the literal demand and context
2. `hypotheses.md` — every hypothesis and its status
3. `business/README.md`, `user/README.md`, `solution/README.md` — current answer per layer
4. `prd/README.md` — the PRD, once written

## Checkpoint · 2026-10-03

A direção do PM nesta execução é fechar apenas Business; ela determinou a escolha da camada. D-004 A, já decidida pelo PM no GitHub, foi registrada. O Business lead aplicou a disposição; um collector produziu E-014, revisores isolados avaliaram as respostas e os três scorers avaliaram o mesmo pacote em paralelo. As fontes se limitaram a `evals/usual-basket/evidence.md` e arquivos da iniciativa; U/S não foram trabalhadas.

B-01 a B-04 foram aprovadas e registradas em commits individuais com D-004; permanecem conscientemente `open`, com motivos e condições de reabertura. H-03/H-04 foram encerradas via `hypothesis-close` como `parked`, com razões, D-004 e condições de reabertura. Não resta hipótese aberta roteada a B.

B-05 ficou `open`: o registro não tem o campo obrigatório `Test` nem testes individuais para H-01/H-02. Duas rejeições sem nova evidência acionaram o anti-loop. A revisão seguinte aprovou apenas o pacote da decisão de bloqueio, não a completude de B5 nem o fechamento de Business. Nenhum answer final de B-05 foi registrado nesta execução.

Business permanece **state:blocked / human:pending**, aguardando [D-005 no epic B #19](https://github.com/marcelusfernandes/bus-upstream/issues/19#issuecomment-5970310371): **Aceitar a lacuna de testes de B5 para concluir Business, completar o registro antes do fechamento ou estacionar B5 mantendo Business bloqueada?**

A recomendação é A: aceitar a lacuna como risco do PM, mantendo correção e revisão antes do uso do registro; B propõe reparar o registro antes do fechamento; C estaciona B5 mantendo Business bloqueada. O pedido no GitHub contém contexto, opções, trade-offs e reversibilidade completos. Nenhuma escolha foi inferida. D-001/D-002/D-003/D-004 seguem válidas; diagnóstico comparável permanece obrigatório antes de solução, meta ou sucesso.

Painel atual: Definition **4**, Grounding **2**, Spread **1** (luna 5/2, sol 4/1, sol56 4/2; mostly_bets=false nos três). Os scores descrevem a camada, sem substituir a decisão. O próximo passo é a escolha explícita do PM em D-005; depois registrar e aplicar a escolha antes de qualquer avanço de estado.

### Problemas observados nesta execução

- Permissão: `git switch` falhou ao criar `.git/index.lock` no sandbox; a sincronização e os commits funcionaram com escalonamento autorizado.
- Descoberta: o nome inicial do projeto não foi encontrado no grafo; o repositório foi indexado. O índice reportou scripts excluídos, exigindo fallback no lead; o root conseguiu localizar funções pelo grafo/search_code depois. O lead também tentou um template inexistente (`templates/layer-readme.md`) e recuperou pelo template disponível.
- Encaminhamento: o orquestrador forneceu inicialmente o diretório errado de E-001 aos revisores B1/B2. As rejeições foram registradas; o caminho correto em `user/evidence/` permitiu aprovação sem alterar respostas ou inventar evidência.
- Contrato/ferramenta: a spec exige `Test`, ausente do registro; a interface atual de `upstream_ops` não oferece atualização desses campos, embora seja o único caminho de escrita de contrato. A segunda rejeição de B5 mostrou também que a alegação operacional não era verificável no pacote restrito do revisor; ela foi removida da justificativa do pedido ao PM.
- Spec de decisão: a skill não explicita os limites de 200 caracteres da pergunta e 300 de texto/trade-offs por opção. `decision-open` recusou a pergunta e depois o trade-off A; foram encurtados sem mudar a escolha, validados por dry-run e publicados. A referência a D-005 no parecer antes da abertura causou drift transitório, resolvido pela publicação.
- Apresentação: `summary` usa “not yet writable” no Statement quando B1 está open; a linha B-01 da tabela preserva a explicação. O helper de review não possui campo para limitations; a aprovação restrita do pedido de bloqueio fica explicitada neste checkpoint.

Validação: 250 testes unitários passaram; a reconciliação após a abertura de D-005 e o novo score não encontrou drift nem obrigações mecânicas pendentes. Summary e checkpoint atualizam/publicam a entrega antes de parar no PM.
