# Problema de negócio

**Statement:** A conversão em relação ao App é o outcome prioritário a investigar, mas a comparabilidade e a existência de um desvio de negócio permanecem desconhecidas.

**Estado:** D-001 e D-002 registradas; os rascunhos B-01 a B-04 receberam revisão independente aprovada. B-05 foi revisada com nova evidência E-010 após rejeição e aguarda nova revisão; este status não afirma commits de respostas. A proposta D-003 foi revisada e ainda não foi publicada. Prioridade e estrutura de medição não demonstram um problema de negócio.

| Resposta | Estado | Síntese |
|---|---|---|
| [B-01](answers/B-01.md) | open | Conversão priorizada; comparabilidade e desvio desconhecidos. |
| [B-02](answers/B-02.md) | open | Baseline comparável ausente das fontes; D-003 proposta para diagnóstico ou investigação como aposta. |
| [B-03](answers/B-03.md) | open | D-002 escolheu conversão como única primária, tempo/custo como guardrails candidatos e recorrência/AOV exploratórios; parâmetros, alvo e prazo abertos. |
| [B-04](answers/B-04.md) | open | Gatilho temporal e custo de esperar não demonstrados. |
| [B-05](answers/B-05.md) | evidenced | E-010 documenta origem atribuída, bases e rotas de H-01 a H-04; todas abertas, sem testes individuais; rascunho aguarda nova revisão. |

[D-001](../decisions/D-001.md) prioriza conversão ([E-006](evidence/E-006.md)); [D-002](../decisions/D-002.md) escolhe a estrutura provisória ([E-009](evidence/E-009.md)). [E-008](evidence/E-008.md) registra a persistência da lacuna de baseline. [E-007](evidence/E-007.md) permanece histórico até D-001, superado por E-009 quanto à escolha da estrutura; seus limites não viram evidência de dados inexistentes fora do corpus. Foram usadas somente `evals/usual-basket/evidence.md` e fontes desta iniciativa.

**Próximo checkpoint proposto:** nova revisão de B-05 com [E-010](evidence/E-010.md), seguida da eventual solicitação D-003 no [epic B #19](https://github.com/marcelusfernandes/bus-upstream/issues/19), pelo orquestrador. Recomendação A: PM obter fonte/responsável e diagnóstico comparável antes de fechar problema ou meta. Alternativa B: aceitar explicitamente o risco (gate 4) de investigação paralela como aposta, com validação antes de solução/meta/sucesso. Nenhuma opção já está aceita ou preenche os parâmetros de B3; H-03/H-04 permanecem abertas. A decisão D-002 não está pendente.
