# PRD · Usual basket

## 1. Problema de negócio

**Enunciado conscientemente aberto:** a conversão em relação ao App é o outcome prioritário a investigar, mas a comparabilidade e a existência de um desvio de negócio permanecem desconhecidas. O PM aceitou concluir Business com B1–B4 abertas, sem afirmar conversão baixa ou oportunidade demonstrada. [B-01], [D-001], [D-004]

**Baseline:** o corpus não apresenta taxas comparáveis, população elegível, eventos, denominador ou janela entre fluxo e App. Isso não demonstra inexistência de dados fora do corpus nem baseline zero. O diagnóstico comparável permanece sob responsabilidade de @marcelusfernandes. [B-02], [E-008], [D-003]

**Sinal de sucesso:** conversão comparável ao App é a única primária escolhida, buscando diferença favorável ao fluxo. Tempo até o pedido e custo de interação são guardrails candidatos de não piora; recorrência e AOV são exploratórios. Fórmula operacional, baseline, comparação, alvo, horizonte e tolerâncias continuam abertos: ainda não há critério completo para avaliar sucesso. Lançamento e ganho de tempo isolado não demonstram sucesso de negócio. [B-03], [D-002]

**Por que agora:** recompra existente e outcomes desejados sustentam interesse em investigar, mas gatilho temporal, urgência e custo de esperar não foram estabelecidos. Essa lacuna foi aceita para o fechamento documental, sem presumir custo zero. [B-04], [E-001], [E-002], [D-004]

D-007 excepciona D-003 somente para concluir documentalmente S, PRD e handoff neste teste. Diagnóstico e validação continuam obrigatórios em paralelo e antes de qualquer implementação; diagnóstico continua necessário antes de meta ou alegação de sucesso. A decisão não autoriza implementação. [D-003], [D-007], [S-02]

## 2. Problema do usuário

**Aposta:** clientes recorrentes refazem manualmente a seleção dos mesmos itens ao tentar repetir uma compra no fluxo analisado. É a candidata comportamental H-05, formulada pelo agente como `guess` e escolhida por @marcelusfernandes em D-006 B; não é comportamento observado. A população é a de clientes recorrentes que pretendem repetir itens, ainda por delimitar dentro da recompra geral. [U-01], [U-02], [H-05], [D-006]

E-001 sustenta apenas recompra recorrente suficiente para investigação. Não há observação de seleção manual repetida, dificuldade ou desejo de reutilizar itens; a seleção pode ser deliberada. Existência do retrabalho, quantidade de pessoas afetadas, prevalência e frequência permanecem desconhecidas. [E-001], [E-016], [U-01], [U-02]

D-006 prevê discovery em paralelo até **2026-10-10**, sob responsabilidade de @marcelusfernandes, mas explicita que pesquisa real não pode ocorrer neste teste. O plano é observar tentativas reais, confrontá-las com compras anteriores e delimitar magnitude posteriormente; nenhum recrutamento, pesquisador designado ou sessão executada está demonstrado. Se o discovery não acontecer no prazo, o PM deve rever aposta e plano. [D-006], [E-017], [U-02], [H-05]

## 3. Vínculo B→U e confiança

Se a seleção repetida for esforço evitável que provoca desistência, remover esse trabalho poderia aumentar pedidos concluídos entre pessoas elegíveis. Essa relação conecta a candidata User à investigação de conversão em Business; é uma inferência **condicional de confiança baixa, não quantificada**, sob responsabilidade de @marcelusfernandes. Existência de retrabalho não demonstraria que velocidade causa conversão nem superioridade sobre o App. [U-03], [D-006], [H-02]

A revisão **BU-fit** aprovou a compatibilidade documental entre outcome, mecanismo condicional, baixa confiança, dono e falsificadores. Ela não comprovou equivalência de populações, baseline, causalidade ou pesquisa executada; comparabilidade continua dependente do diagnóstico. [BU-fit], [B-02], [U-03]

Ausência de retrabalho evitável, seleção deliberada ou retrabalho sem relação com desistência enfraquecem esse vínculo. A alegação conjunta H-02 exige testar separadamente efeito causal de velocidade e superioridade sobre o App; uma comparação adequada e precisa que exclua qualquer elo a invalida no contexto testado. Dados insuficientes permanecem inconclusivos. Achados contrários à direção ou à comparabilidade exigem reabrir a camada afetada. [U-03], [H-02], [B-01], [B-02]

## 4. Solução

**Aposta escolhida:** reutilizar a composição de uma compra anterior como base ajustável da recompra, para evitar reconstrução manual quando a intenção do cliente for repetir os mesmos itens. S-A foi escolhida por @marcelusfernandes em D-007 A; o mecanismo foi proposto pelo agente, com base `guess`, sem eficácia ou capacidade existente demonstradas. [S-02], [S-A], [D-007]

| Opção considerada | Disposição e motivo | Trade-off documentado |
| --- | --- | --- |
| S-A — reutilização ajustável | Escolhida como aposta; atua diretamente sobre a candidata de reconstrução manual. [S-01], [D-007] | Conferir e corrigir a composição, ou obter os dados anteriores, pode anular o benefício. [S-A] |
| S-B — preparação humana | Estacionada porque S-A foi escolhida; alternativa operacional distinta, sem evidência de invalidação, fora da aposta ativa. [S-01], [S-B] | Transfere trabalho e pode introduzir espera e custo empresarial; capacidade e acesso não demonstrados. [S-B] |
| S-C — fluxo mais rápido, H-01 | Estacionada sem veredicto; aspiração herdada sem mecanismo próprio ou comparação, preservada em vez de convertida em promessa. [S-01], [S-C], [H-01] | Velocidade, sozinha, não especifica como resolver a candidata User. [S-C] |
| S-D — não intervir agora | Estacionada nesta rodada porque D-007 escolhe avanço documental; manter diagnóstico antes da escolha conservaria D-003 integral em iniciativa real. [S-01], [S-D], [D-007] | Adia benefício possível enquanto investiga, sem custo da espera demonstrado. [S-D], [B-04] |

**Como funcionaria em alto nível:** aproveitar uma referência de itens e quantidades de compra anterior que corresponda à intenção atual, mantendo decisão e ajuste com o cliente. O benefício proposto é evitar reconstrução; efeitos comerciais, acesso a dados, custos e capacidades precisam de validação própria. [S-04], [S-A]

**Delimitação:** a aposta atende quem pretende repetir itens e mantém a composição anterior como referência ajustável. Ficam fora compra automática ou recorrente sem nova intenção, previsão/recomendação de cesta, incentivos comerciais, mudanças de preço, estoque, pagamento ou entrega, redesenho da jornada inteira e S-B como aposta paralela. Velocidade e conversão são hipóteses a testar, sem promessa de melhoria. Produto/canal e população elegível permanecem por delimitar; expansão material requer nova decisão do PM. [S-03], [H-01], [H-02]

## 5. Vínculo U→S e sinal de parada

Se U1 corresponder a retrabalho real, reaproveitar uma composição já conhecida pode remover parte desse esforço e preservar ajuste à intenção atual. Esse vínculo é uma inferência de mecanismo, com confiança **baixa, não quantificada**; não há demonstração de repetição dos mesmos itens, desejo de reutilização ou menor esforço de conferência. [S-02], [U-01], [E-001], [E-018]

A revisão **US-fit** aprovou a correspondência documental com a população e situação de U1, a baixa confiança, as lacunas e o dono explícito. Não verificou eficácia, magnitude, conversão, viabilidade ou pesquisa. A escolha e as revisões não aumentam a confiança empírica. [US-fit], [S-02]

**Suspender a direção e retornar ao PM** se observações mostrarem seleção manual deliberada ou ausência de retrabalho evitável; se conferir/corrigir custar tanto quanto ou mais que reconstruir; se dados anteriores adequados não puderem ser obtidos; ou se o diagnóstico contrariar oportunidade ou comparabilidade. Nessas situações, rever S e a camada afetada. Falta de dados ou precisão mantém a conclusão inconclusiva; implementação depende de diagnóstico, validação e autorização próprios. [S-02], [D-007]

## 6. Hipóteses derivadas para validar em design

As quatro hipóteses abaixo são propostas de S4, com base `guess` do agente e confiança baixa, não quantificada. São trabalho futuro antes de implementação, sem resultados existentes ou parâmetros numéricos aprovados. [S-04]

| Hipótese derivada | Como poderia ser testada | O que a enfraquece |
| --- | --- | --- |
| **Valor:** reaproveitamento remove trabalho evitável relevante para quem pretende repetir itens. | Observar tentativas reais e intenção, confrontando compras anteriores; depois comparar reconstrução com conferência/ajuste em situações equivalentes. Observação qualitativa não estima prevalência. [S-04] | Ausência de retrabalho, seleção deliberadamente diferente ou conferência mais onerosa. [S-04] |
| **Usabilidade:** clientes compreendem a referência e conseguem adequá-la à intenção sem anular o benefício. | Design propõe protótipo e observa compreensão, resultado pretendido versus obtido e esforço em tarefas representativas, com relevância definida previamente. [S-04] | Confusão persistente ou divergência da intenção. [S-04] |
| **Viabilidade técnica:** referência anterior adequada e autorizada pode ser obtida e adaptada com confiabilidade suficiente. | Verificar fontes e permissões; investigar qualidade e acesso a itens e quantidades, sem pressupor sistema ou integração existente. [S-04] | Ausência de acesso legítimo ou referência utilizável. [S-04] |
| **Viabilidade econômica:** benefício potencial justifica construção/manutenção sem piora inaceitável dos guardrails. | Após diagnóstico comparável, estimar custo total e testar outcome/guardrails com atribuição, população, janela e critérios definidos previamente pelo PM. [S-04] | Esforço apenas transferido, guardrails piores ou benefício que não justifica custo; incerteza não prova retorno. [S-04] |

@marcelusfernandes mantém a responsabilidade pelas lacunas e pelo discovery de D-006. Design recebe essas hipóteses e métodos para planejar a validação; executores, responsável técnico, orçamento, desenho final e demais prazos estão abertos. Diagnóstico e validação são obrigatórios em paralelo e antes de implementação. [S-04], [D-006], [D-007]

## 7. Hipóteses do stakeholder e suas disposições

H-01–H-04 são atribuídas documentalmente à demanda literal do stakeholder reproduzida no intake; essa origem externa não foi verificada independentemente. Todas estão `parked`, sem validação ou invalidação empírica. H-05 tem origem no agente e mantém a aposta User ativa, com seu teste empírico estacionado. [B-05], [H-01], [H-02], [H-03], [H-04], [H-05]

| ID e alegação preservada | Estado, motivo e condição de retomada |
| --- | --- |
| **H-01:** “fluxo mais rápido” | `parked` em S-C: aspiração sem mecanismo/comparação. D-007 escolheu S-A posteriormente, sem validar rapidez ou definir comparador. Reabrir ao definir intervenção e comparador para teste, antes de alegar redução de tempo ou se diagnóstico contrariar a direção; seguir o teste registrado. [H-01], [S-01], [D-007] |
| **H-02:** “Se o fluxo for mais rápido ele pode converter mais que o App” | `parked` por D-006 B, sem veredicto causal; H-05 reenquadra um problema investigável e não substitui a alegação original. Reabrir antes de alegar causalidade/superioridade ou se diagnóstico contrariar a direção. [H-02], [D-006], [U-04] |
| **H-03:** “o custo de interação é menor” | `parked` por D-004 A: faltam definição e comparação de custo. Reabrir antes de operacionalizar o guardrail ou alegar economia, distinguindo gasto empresarial de esforço do comprador e definindo medidas, contexto e atribuição. [H-03], [D-004] |
| **H-04:** “Também queremos entender se ajuda na recorrência ou mexe no AOV.” | `parked` por D-004 A: efeitos sem evidência, exploratórios por D-002. Reabrir se dados ameaçarem a direção, se virarem requisito/meta ou antes de alegar impacto; impacto negativo também responde à pergunta e não significa sucesso. [H-04], [D-004], [D-002], [B-05] |
| **H-05:** candidata de reconstrução manual dos mesmos itens | `parked` quanto à resolução empírica, com aposta de @marcelusfernandes ativa por D-006 B. Reabrir com observações, antes de afirmar retrabalho comprovado ou se candidata/diagnóstico contrariar a direção; rever aposta/plano se discovery não ocorrer até 2026-10-10. [H-05], [D-006] |

Os testes registrados distinguem apoio, invalidação no contexto e resultado inconclusivo; parâmetros, precisão e comparabilidade precisam ser definidos antes da execução. Testar usabilidade ou obter ganho de tempo não resolve automaticamente as hipóteses causais. [B-05], [H-01], [H-02], [H-03], [H-04], [S-04]

## 8. Apostas nomeadas e riscos aceitos

| Aposta/aceitação | Quem aceitou e decisão | Risco e limite preservados |
| --- | --- | --- |
| Investigar conversão sem desvio observado | @marcelusfernandes, D-003 B. [D-003] | Esforço sem oportunidade demonstrada; diagnóstico comparável permanece obrigatório. [B-02], [D-003] |
| Encerrar Business com B1–B4 conscientemente abertas | @marcelusfernandes, D-004 A. [D-004] | Problema/baseline, sucesso completo e urgência desconhecidos; direção pode exigir reabertura. Aceita disposição documental, sem validar negócio. [B-01], [B-02], [B-03], [B-04] |
| U1/H-05, candidata de retrabalho na recompra | @marcelusfernandes, D-006 B. [D-006] | Retrabalho pode não existir ou não afetar conversão; magnitude e causalidade abertas. Discovery previsto até 2026-10-10, não executável como pesquisa real neste teste. [U-01], [U-02], [U-03], [E-017] |
| S-A, reutilização ajustável da composição anterior | @marcelusfernandes, D-007 A. [D-007] | Herda U1 como aposta, U2/U3 abertas e B1–B4 abertas; pode resolver dificuldade inexistente, não mover conversão, não ser viável ou não justificar investimento. [S-02] |
| Exceção documental a D-003 | @marcelusfernandes, D-007 A, somente neste teste. [D-007] | Permite S/PRD/handoff como aposta, mantendo diagnóstico e validação em paralelo e antes de qualquer implementação. Não se estende a iniciativa real nem dispensa diagnóstico antes de meta/sucesso. [D-007], [S-02] |

Os registros D-004, D-006 e D-007 identificam Claude representando o PM no exercício; essas aceitações são registradas em nome de @marcelusfernandes nesse contexto de teste. Aprovação documental não é resultado de pesquisa ou compromisso externo adicional. [D-004], [D-006], [D-007], [E-017]

## 9. Perguntas abertas entregues a design

Design recebe os desconhecidos abaixo para planejar investigação e voltar ao PM quando houver decisão necessária; não há delegação implícita de aceitação de risco ou expansão de escopo. [S-03], [S-04]

| Pergunta aberta | Por que permanece aberta / condição necessária |
| --- | --- |
| Qual produto/canal, fluxo, App comparador e população elegível delimitam a aposta? | O corpus não os identifica operacionalmente nem demonstra equivalência de populações. Confirmar o recorte antes de pesquisa/comparação. [U-02], [S-03], [BU-fit] |
| Existe retrabalho evitável dos mesmos itens, qual sua causa, quantas pessoas afeta e com que frequência? | E-001 só demonstra recorrência; candidata, dificuldade e magnitude não foram observadas. Executar discovery futuro e reabrir U/H-05 conforme os achados. [U-01], [U-02], [E-016], [H-05] |
| Há oportunidade de negócio e baseline comparável de conversão? | Taxas, eventos, denominadores, população, fontes, janela e contexto faltam. @marcelusfernandes responde pelo diagnóstico; contrariar direção/comparabilidade exige reabertura de B. [B-01], [B-02], [D-003] |
| Como avaliar sucesso e não piora? | Formulação operacional, método, alvo/diferença relevante, horizonte, guardrails e tolerâncias não foram decididos; custo precisa distinguir gasto empresarial de esforço do comprador. Reabrir B3 para decisão explícita após diagnóstico e antes de meta/sucesso. [B-03], [D-002], [S-02], [H-03] |
| Qual gatilho temporal ou custo da espera justificaria priorização? | Não há fonte para urgência ou perdas por atraso. Reabrir B4 com novo contexto antes de usar essa justificativa. [B-04] |
| Reutilizar a referência é desejável, compreensível e menos oneroso que reconstruir? | Preferência, intenção, valor e esforço de conferência não foram observados. Planejar os testes de valor/usabilidade de S4 sem tratar métodos como resultados. [S-02], [S-04] |
| Quais dados anteriores adequados e autorizados existem, com que acesso e qualidade? | Fontes, permissões e capacidades não foram demonstradas. Planejar investigação de viabilidade; não presumir integração existente. [S-03], [S-04] |
| O benefício justifica custo total e afeta conversão, custo, recorrência ou AOV? | Viabilidade econômica e vínculos causais permanecem sem demonstração. Definir critérios/desenho com o PM após diagnóstico; reabrir H-02/H-03/H-04 antes das respectivas alegações. [S-04], [H-02], [H-03], [H-04] |
| Quem executa pesquisa e investigação técnica, com qual orçamento, desenho final, critérios e demais prazos? | O dono é @marcelusfernandes e só o discovery tem prazo registrado; executores, recrutamento e recursos não estão confirmados. Rever aposta/plano se discovery não ocorrer até 2026-10-10. [U-02], [S-04], [D-006] |
| Quando a aposta poderá virar implementação? | Este handoff é documental para o teste; diagnóstico, validação e autorização de implementação próprios continuam necessários. Qualquer mudança de aposta ou expansão material requer nova decisão do PM. [D-007], [S-02], [S-03] |

[B-01]: ../business/answers/B-01.md
[B-02]: ../business/answers/B-02.md
[B-03]: ../business/answers/B-03.md
[B-04]: ../business/answers/B-04.md
[B-05]: ../business/answers/B-05.md
[U-01]: ../user/answers/U-01.md
[U-02]: ../user/answers/U-02.md
[U-03]: ../user/answers/U-03.md
[U-04]: ../user/answers/U-04.md
[S-01]: ../solution/answers/S-01.md
[S-02]: ../solution/answers/S-02.md
[S-03]: ../solution/answers/S-03.md
[S-04]: ../solution/answers/S-04.md
[D-001]: ../decisions/D-001.md
[D-002]: ../decisions/D-002.md
[D-003]: ../decisions/D-003.md
[D-004]: ../decisions/D-004.md
[D-006]: ../decisions/D-006.md
[D-007]: ../decisions/D-007.md
[E-001]: ../user/evidence/E-001.md
[E-002]: ../business/evidence/E-002.md
[E-008]: ../business/evidence/E-008.md
[E-016]: ../user/evidence/E-016.md
[E-017]: ../user/evidence/E-017.md
[E-018]: ../solution/evidence/E-018.md
[H-01]: ../hypotheses.md
[H-02]: ../hypotheses.md
[H-03]: ../hypotheses.md
[H-04]: ../hypotheses.md
[H-05]: ../hypotheses.md
[S-A]: ../solution/bets/S-A/README.md
[S-B]: ../solution/bets/S-B/README.md
[S-C]: ../solution/bets/S-C/README.md
[S-D]: ../solution/bets/S-D/README.md
[BU-fit]: ../user/review.md
[US-fit]: ../solution/review.md
