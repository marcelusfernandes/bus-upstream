# Problema de negócio

**Statement:** A conversão em relação ao App é o outcome prioritário a investigar, mas a comparabilidade e a existência de um desvio de negócio permanecem desconhecidas.

**Estado:** Business permanece `in-progress`; este pacote prepara exclusivamente seu fechamento, sem executar U/S. D-001/D-002/D-003 continuam registradas e válidas. Os cinco rascunhos atuais B-01 a B-05 receberam revisão independente aprovada, com os pareceres registrados pelo orquestrador. D-004 foi aberta no epic B #19 e aguarda escolha explícita do PM. A spec final recebeu nova aprovação independente em B-01/B-05, com os pareceres registrados. Nenhuma disposição final foi aceita ou aplicada; B1–B4 continuam open e B5 evidenced. H-03/H-04 continuam abertas. O painel atual resultou em Definition 4 / Grounding 2 / Spread 2 (avaliações individuais: 6/3, 4/1 e 4/2; todas com mostly_bets=false); essa pontuação não é aprovação do PM e D-004 permanece pendente.

| Resposta | Estado atual | Disposição proposta em D-004 A |
|---|---|---|
| [B-01](answers/B-01.md) | open | Manter desvio e comparabilidade conscientemente abertos para concluir Business: fontes não demonstram problema; risco de reabrir se não houver oportunidade. |
| [B-02](answers/B-02.md) | open | Manter baseline conscientemente aberto: corpus sem medida/fonte acessível; diagnóstico do PM continua obrigatório antes de solução, meta ou sucesso. |
| [B-03](answers/B-03.md) | open | Manter parâmetros, alvo e prazo conscientemente abertos para evitar definição sem suporte; reabrir para decisão explícita após diagnóstico e antes de solução/meta/sucesso. |
| [B-04](answers/B-04.md) | open | Manter gatilho/custo da espera conscientemente abertos: corpus só registra interesse; não justificar urgência nem inferir custo zero. |
| [B-05](answers/B-05.md) | evidenced | Registro documentado; estacionar H-03/H-04 sem veredicto somente após aprovação, preservando custo como guardrail candidato e recorrência/AOV exploratórios. |

## Decisão de fechamento proposta

**A — recomendada:** concluir Business com B1–B4 conscientemente abertas pelos motivos acima e H-03/H-04 `parked` com razões e condições de reabertura em B-05. A aposta distinta dessas respostas abertas pertence ao PM @marcelusfernandes: aceitar o risco de encerrar Business sem problema, baseline, critério completo de sucesso ou urgência demonstrados (gate 4). Sua validação ocorre com o diagnóstico paralelo já exigido em D-003 e decisões posteriores específicas sobre problema/medição; uma direção contradita exige reabrir Business. Não há prazo confirmado e nenhum é inventado. Esse encerramento não aprova solução, meta, sucesso ou execução de U/S.

**B:** manter Business em andamento até diagnóstico, contexto e resolução das lacunas, preservando a investigação paralela de D-003. A diferença é o momento e o risco do fechamento de Business, não a reabertura de decisões já tomadas.

[E-012](evidence/E-012.md) delimita o que D-001/D-002/D-003 autorizam e o que segue desconhecido; [E-013](evidence/E-013.md) mostra que H-03/H-04 não tiveram efeitos nem estacionamento decididos. Ambas são auditorias documentais, não novas observações de produto. As únicas fontes usadas foram `evals/usual-basket/evidence.md` e arquivos desta iniciativa. [E-010](evidence/E-010.md) preserva o limite de B5: origem atribuída e rotas documentadas, mas testes individuais não registrados.

**Próximo passo:** obter a decisão explícita do PM sobre D-004 no epic B #19. Os cinco rascunhos e a spec final tiveram revisão independente aprovada; a decisão permanece pendente. Se A for escolhida, registrar D-004, executar `hypothesis-close` de H-03/H-04 como `parked` com as razões de B-05, atualizar/revisar as respostas conforme a escolha e só então avaliar o encerramento de B. Se B for escolhida, manter B em andamento. Neste checkpoint a decisão é necessária para a disposição de fechamento; não há motivo para deslocar o trabalho para U/S.
