# Solution

**Statement:** Um agente com IA interpreta telas e escolhe ações no percurso completo de extração na 99 e emissão no Mainô, sem APIs desses sistemas, para reduzir a dedicação contínua da pessoa responsável, que mantém a conferência e a autorização das emissões.

**State:** S-B escolhida pelo PM em D-004, com aceite dos riscos explicitados (gates 3/4); respostas atualizadas aguardam revisão independente, commits do orchestrator e revisão U→S. A direção está decidida; eficácia permanece aposta.

## Reading order

1. [S-01](answers/S-01.md): opções consideradas e destino de H-02/H-03.
2. [S-02](answers/S-02.md): solução escolhida, elo U→S, confiança e sinal de parada.
3. [S-03](answers/S-03.md) e [S-04](answers/S-04.md): limites e hipóteses a avaliar downstream.
4. [S-B escolhida](bets/S-B/README.md); alternativas [S-A por regras](bets/S-A/README.md), [S-E híbrida](bets/S-E/README.md), [S-C manual](bets/S-C/README.md) e [S-D manter atual](bets/S-D/README.md).
5. [D-004](../decisions/D-004.md) registra “Opção B” sem justificativa adicional; [E-010](evidence/E-010.md) descreve mecanismos genéricos, sem provar compatibilidade local ou 250/dia.

| Pergunta | Estado do rascunho atualizado |
|---|---|
| S-01 | evidenced — opções comparadas e escolha B registrada; A/C/E parked, D discarded. |
| S-02 | bet — B escolhida pelo PM; confiança baixa na eficácia local e em 250/dia. |
| S-03 | bet — limites preservam o percurso completo e controle humano; adequação operacional ainda a avaliar. |
| S-04 | bet — abordagem IA e hipóteses de valor, usabilidade e viabilidades técnica/operacional para design. |

H-02/H-03 continuam parked como apostas escolhidas em S-B e testes downstream, sem validação de eficácia. A resolução original é histórica; D-004 e os testes atualizados substituem a recomendação A pela escolha B, preservando o registro. U confirma o problema por declaração do PM; S herda essa base e as lacunas de B-03: prazo, janela, condições sustentáveis e critérios de correção. D-004 aceita avançar ao design com esses riscos, sem preencher as lacunas ou exigir reconfirmação. 250/dia é meta decidida, não resultado; oito horas contínuas já foram consideradas inviáveis. 15/11 é início do desenvolvimento Seller e a duração desta frente não foi decidida.
