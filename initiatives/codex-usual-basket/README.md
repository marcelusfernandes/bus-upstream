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


## Checkpoint · 2026-10-03 · User aguarda D-006

A direção explícita do PM determinou o trabalho em U, H-02 primeiro. O User lead examinou H-02 antes das respostas e delegou a auditoria documental E-016 ao collector, limitada a `evals/usual-basket/evidence.md` e aos arquivos existentes da iniciativa. Não houve pesquisa web nem pesquisa com usuários. E-016 sustenta recorrência como contexto, sem comprovar retrabalho, magnitude ou causalidade.

U-01–U-04 foram redigidas como `open` e receberam quatro revisões documentais aprovadas, registradas com suas limitações. Nenhuma resposta foi registrada como decidida: todas dependem da disposição do PM sobre discovery, aposta ou adiamento. Existe `user/discovery-brief.md`; seis sessões e prazo são propostas futuras, não resultados nem compromissos vigentes. H-02 continua aberta e preservada; nenhuma hipótese foi registrada ou encerrada. A candidata comportamental é explicitamente guess, sem H-id fictício.

### Decisão pendente no epic U #20

**D-006 · Investigar o retrabalho na recompra antes de escolher U1, assumir essa candidata como aposta com discovery em paralelo ou adiar User, explicitando o destino de H-02?**

E-001 registra recompra recorrente no fluxo analisado, sem contagens, frequência ou dificuldade observada. E-002 registra tempo/custo como outcomes desejados; E-003 diz que nenhuma intervenção foi definida. A auditoria E-016 não encontrou fricção, magnitude nem causalidade velocidade→conversão/App nas fontes permitidas.

A candidata do agente é: clientes recorrentes refazem manualmente a seleção dos mesmos itens ao tentar repetir uma compra no fluxo analisado. É um guess, não um achado: até a repetição dos mesmos itens e seu caráter problemático são desconhecidos. H-02 preserva a alegação causal do stakeholder e continua aberta. U1–U4 estão abertas; decisões B anteriores não aceitam risco em U.

O brief propõe seis sessões observadas como contraste qualitativo, levantamento de magnitude e planejamento causal separado. Dono proposto: PM @marcelusfernandes, responsável por designar pesquisador e obter relatório inicial até 2026-10-10; não é compromisso vigente. D-003 mantém diagnóstico comparável antes de solução, meta ou sucesso. Aceitar aposta não fecha U automaticamente: registro da candidata, revisão BU-fit e demais pendências continuam necessários.

- **A** — Executar o discovery proposto, sob responsabilidade de @marcelusfernandes, com relatório inicial até 2026-10-10; manter U1–U4 e H-02 abertas até evidência ou nova decisão. Trade-offs: Recomendado: investiga a candidata sem assumir retrabalho nem efeito na conversão; exige recrutamento e mantém o fechamento de U pendente. O relatório inicial não é prova causal. Reversibilidade: Alta: mudar ou descartar a candidata à luz das observações.
- **B** — Escolher a candidata de retrabalho como aposta de @marcelusfernandes, executar discovery em paralelo até 2026-10-10 e estacionar H-02 sem veredicto causal. Trade-offs: Gates 2/4: aceita risco de retrabalho inexistente ou sem efeito em conversão e mantém magnitude/causalidade abertas. Reabrir H-02 antes de alegar causalidade/superioridade ou se o diagnóstico contrariar a direção; não autoriza solução nem fechamento automático de U. Reversibilidade: Reversível com retrabalho: revisar a aposta quando houver evidência; registro da candidata segue pendente.
- **C** — Adiar User sem escolher problema e estacionar H-02 sem veredicto até retomada explícita do PM. Trade-offs: Evita esforço de pesquisa agora, mas mantém U inconclusa e sem base para solução; reabrir H-02 na retomada ou antes de alegar causalidade/superioridade. Reversibilidade: Alta: PM retoma a camada com o mesmo registro e as lacunas preservadas.

**Recomendação:** A — O corpus só sustenta recorrência; observar a tarefa pode separar retrabalho evitável de seleção deliberada, sem converter desejo de velocidade em problema comprovado.

**Mudaria a recomendação:** Evidência observável de uma dificuldade recorrente no mesmo recorte e magnitude conhecida, ou decisão explícita do PM de aceitar a candidata e suas lacunas como risco.

### Estado, validação e limites

Reconciliação após abrir D-006: U `in-progress`, D-006 pendente, H-02 aberta, Definition 0 / Grounding 5 (baseline anterior, sem novo painel); B permanece `done` 5/2, sem nova contradição que exija reabertura. Não houve BU-fit nem re-score: o ciclo parou na decisão do PM antes de respostas decididas ou fechamento. Business lead e painel de scorers não foram acionados porque suas condições de despacho não foram alcançadas. Os 258 testes unitários passaram.

### Problemas observados

- A skill User exige registrar a hipótese reenquadrada, mas `upstream_ops` não tem comando de criação; `hypothesis-update` só altera Test/Origin/Basis. O código/CLI confirmam o limite. Nenhuma escrita manual contornou o contrato. O reenquadramento ficou proposto, não executado, e impede fechamento.
- `git switch` falhou em `.git/index.lock` por permissão; escalonamento permitiu switch/pull e registros das revisões. Não houve rejeição de aprovação automática.
- A ferramenta recusou um segundo reviewer com `agent thread limit reached`, apesar de collector concluído. O mesmo reviewer foi reutilizado em quatro tarefas de alvo único, em sequência: isso preserva separação autor/revisor, mas não proporciona contexto limpo entre respostas.
- O User lead tentou ler `templates/decision-request.json`, inexistente; corrigiu para o template `.md`, sem efeito no contrato.
- Uma chamada inicial de ajuda de `upstream_ops` omitiu `--repo`; somente leitura. Todas as operações de contrato usaram o repo solicitado e a assinatura do papel.
- Reviews são documentais e não atestam pesquisa, recrutamento, prazo nem execução externa. O resumo atual apresenta Statement `not yet written — U-01 is open`, com a candidata e seu estado explícitos.
