# Problema de negócio

**Statement:** A conversão em relação ao App é o outcome prioritário a investigar, mas a comparabilidade e a existência de um desvio de negócio permanecem desconhecidas.

**Estado:** D-004 A foi decidida pelo PM e registrada em 2026-10-03: B1–B4 ficam conscientemente abertas, não bloqueantes para concluir Business, e H-03/H-04 são estacionadas sem veredicto. O estacionamento de ambas foi aplicado por `upstream_ops hypothesis-close`. As respostas abaixo são rascunhos finais para revisão independente; a camada permanece `in-progress` até o orquestrador registrar as respostas, reavaliar os scores e executar `route --layer B --state done`. D-001/D-002/D-003 continuam válidas. U/S não estão autorizadas por este fechamento.

| Resposta | Estado | Disposição aceita em D-004 A |
|---|---|---|
| [B-01](answers/B-01.md) | open | Desvio e comparabilidade desconhecidos: não há evidência para afirmar problema; reabrir B1/B2 se diagnóstico contradisser direção ou comparabilidade. |
| [B-02](answers/B-02.md) | open | Baseline ausente no corpus, sem fonte acessível confirmada; PM mantém responsabilidade pelo diagnóstico antes de solução, meta ou sucesso. |
| [B-03](answers/B-03.md) | open | Parâmetros, alvo e prazo sem suporte; reabrir para decisão explícita após diagnóstico e antes de solução/meta/sucesso. |
| [B-04](answers/B-04.md) | open | Sem gatilho/custo da espera documentados; reabrir ao obter contexto e antes de alegar urgência ou perda por atraso. |
| [B-05](answers/B-05.md) | evidenced | Conteúdo e rotas documentados; H-03/H-04 parked por D-004; H-01/H-02 continuam open em S/U. Registro não tem testes individuais completos. |

## Risco aceito e dependências

A aposta procedimental pertence ao PM @marcelusfernandes (gate 4): é aceitável concluir Business com lacunas documentadas. Isso aceita o risco de esforço sem oportunidade demonstrada e de reabertura posterior; não aposta que a conversão esteja baixa nem que as hipóteses sejam verdadeiras. O diagnóstico comparável em paralelo continua obrigatório por D-003 antes de solução, meta ou sucesso. Não há prazo confirmado e nenhum é inventado.

D-002 preserva conversão comparável ao App como única primária, diferença favorável ao fluxo como direção, tempo/custo como guardrails candidatos e recorrência/AOV como exploratórios. Faltam definições, alvo, horizonte e tolerâncias operacionais. H-03 reabre antes de operacionalizar o guardrail de custo ou alegar economia; H-04 reabre se dados exploratórios ameaçarem a direção, se seus outcomes virarem requisito/meta ou antes de alegar impacto. Estacionar não demonstra efeito nem descarta essas medidas.

[E-014](evidence/E-014.md) audita o alcance de D-004: autorização de disposição, não evidência empírica nem prova de execução. A execução das hipóteses está no [registro](../hypotheses.md). [E-012](evidence/E-012.md)/[E-013](evidence/E-013.md) são retratos anteriores a D-004: seus limites empíricos permanecem, sua ausência de autorização foi superada. [E-010](evidence/E-010.md) limita B5 à origem atribuída e às rotas documentadas, sem testes individuais completos. E-014 também registra a divergência histórica das versões anteriores deste README/respostas, corrigida nestes rascunhos.

Fontes exclusivas: `evals/usual-basket/evidence.md` e arquivos desta iniciativa. Nenhuma pesquisa externa nem trabalho de U/S foi executado. O último painel registrado é Definition 4 / Grounding 2 / Spread 2; não representa a reavaliação destes rascunhos. O próximo passo é revisão independente, registro, novo painel e rota final pelo orquestrador; não há nova decisão proposta.
