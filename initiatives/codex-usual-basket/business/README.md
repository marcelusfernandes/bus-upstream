# Problema de negócio

**Statement:** A conversão em relação ao App é o outcome prioritário a investigar, mas a comparabilidade e a existência de um desvio de negócio permanecem desconhecidas.

**Estado:** Business permanece `in-progress`. D-001, D-002 e D-003 registradas. D-003 B aceita, sob responsabilidade do PM @marcelusfernandes, o risco de investigar melhoria de conversão sem desvio observado e obter diagnóstico comparável em paralelo, antes de solução, meta ou sucesso (E-011). As versões atuais de B-01 a B-05, incorporando D-003, receberam revisão independente aprovada, sem bloqueios, e foram registradas pelo orquestrador via `upstream_ops`. O painel foi concluído: Definition 4, Grounding 2, Spread 1. Não há decisões pendentes nem divergências de reconciliação. B-01/B-02 e os parâmetros de B-03 permanecem abertos; a aposta aceita é sobre investigar, sem estabelecer um problema demonstrado ou assumido. H-03/H-04 continuam abertas.

| Resposta | Estado | Síntese |
|---|---|---|
| [B-01](answers/B-01.md) | open | Conversão priorizada; comparabilidade e desvio desconhecidos; D-003 autoriza investigar, sem fechar B1. |
| [B-02](answers/B-02.md) | open | Baseline comparável desconhecido; D-003 B aceita investigação como aposta do PM, com diagnóstico paralelo antes de solução/meta/sucesso. |
| [B-03](answers/B-03.md) | open | D-002 escolheu conversão como única primária, tempo/custo como guardrails candidatos e recorrência/AOV exploratórios; D-003 mantém parâmetros, alvo e prazo abertos. |
| [B-04](answers/B-04.md) | open | Gatilho temporal e custo de esperar não demonstrados. |
| [B-05](answers/B-05.md) | evidenced | E-010 documenta origem atribuída, bases e rotas de H-01 a H-04; todas abertas, sem testes individuais; D-003 não resolve H-03/H-04. |

[D-001](../decisions/D-001.md) prioriza conversão ([E-006](evidence/E-006.md)); [D-002](../decisions/D-002.md) escolhe a estrutura provisória ([E-009](evidence/E-009.md)); [D-003](../decisions/D-003.md) aceita o risco de investigação paralela ([E-011](evidence/E-011.md)). [E-008](evidence/E-008.md) registra a lacuna de baseline, que D-003 não preenche. [E-007](evidence/E-007.md) permanece histórico até D-001, superado por E-009 quanto à escolha da estrutura; seus limites não viram evidência de dados inexistentes fora do corpus. Foram usadas somente `evals/usual-basket/evidence.md` e fontes desta iniciativa.

**Próximo passo:** interromper o avanço automático neste checkpoint, pois a próxima investigação útil de H-02 depende do User lead ainda não implementado. O diagnóstico comparável continua como trabalho já aceito em D-003: cabe ao PM obter a fonte ou indicar responsável e trazer o pacote descrito em B-02; fonte acessível, analista e prazo ainda não estão confirmados. Não é uma nova decisão sobre aceitar investigação paralela. Até novas observações, a coleta documental permitida não resolve baseline, gatilho/custo da espera ou H-03/H-04, e B não pode ser concluída.

**Investigação paralela:** o próximo trabalho útil é investigar H-02, encaminhada a U para examinar o vínculo entre velocidade e conversão; essa frente depende do User lead, ainda indisponível nesta versão do processo. Esta camada não responde U nem escolhe solução para H-01. D-001/D-002/D-003 não estão pendentes; nenhuma nova decisão é proposta neste checkpoint.
