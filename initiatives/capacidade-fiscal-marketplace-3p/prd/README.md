# PRD · Capacidade de emissão fiscal para o Marketplace 3P

## 1. Problema de negócio

A capacidade atual de emissão fiscal do Marketplace não atende à demanda das 15 dark stores, segundo o PM, comprometendo a sustentação da operação durante a expansão 3P. O resultado priorizado é capacidade fiscal suficiente para sustentar essa expansão gradual. (B-01; D-001; E-007)

O baseline é declaratório: uma pessoa, até 80 notas/dia, com oito horas contínuas de cliques consideradas inviáveis pelo PM. A rotina relatada é D-1, com notas de sexta a domingo concentradas na segunda-feira, chegando a **200+**, um limite inferior. As 15 lojas atualizam as oito do intake; faltam uma série operacional e medição independente. D-1 descreve a operação, sem estabelecer prazo legal. (B-02; E-001; E-002; E-007)

A métrica primária é capacidade diária de emissão, com **meta decidida de 250 emissões/dia**, preservando correção fiscal. A operacionalização proposta considera emissões corretas concluídas, sem duplicatas, acompanhando demanda elegível, pendências, conferência, retrabalho e esforço humano total. Prazo de alcance, janela de comprovação, critérios operacionais de correção e carga sustentável permanecem abertos; oito horas contínuas não constituem orçamento futuro aprovado. B3 fica conscientemente aberto por aceite do PM em D-004: a direção pode avançar ao design, mas o sucesso ainda não foi demonstrado nem seu protocolo completado. (B-03; D-002; D-004; E-005)

A relevância é presente: insuficiência e esforço já foram relatados enquanto a expansão continua. Há expectativa de 30 lojas em dezembro e previsão de 3000 pedidos/semana, sem equivalência estabelecida entre pedidos e notas ou garantia de que 250/dia atenderá aos picos. Seller prevê iniciar o desenvolvimento de uma integração definitiva no Admin a partir de 15/11; a entrega não foi informada. O papel provisório desta frente é inferência, sem duração aprovada. (B-04; B-03; E-001; E-006; E-007; D-001)

## 2. Problema do usuário

A pessoa responsável pela emissão 3P executa manualmente o fluxo completo de extração na 99 e emissão no Mainô, com dedicação contínua que limita quantas notas consegue concluir. O recorte é a mesma pessoa e o percurso inteiro entre os dois sistemas, incluindo a concentração de trabalho de segunda-feira. (U-01; U-02; D-003)

O PM confirmou a validação do trabalho manual, dos dois sistemas e da limitação de capacidade em D-003. O problema está **evidenciado por confirmação declaratória do PM**, sem observação independente dos agentes, método ou amostra de validação informados. A magnitude disponível é uma pessoa, 80 notas/dia com oito horas contínuas consideradas inviáveis e 200+ notas concentradas na segunda; a etapa dominante não foi identificada. A descoberta anteriormente proposta deixou de ser condição para avançar, sem dispensar medição de resultado da solução. (U-01; U-02; E-002; E-007; E-009; D-003)

## 3. Vínculo B→U e confiança

Reduzir o esforço humano total necessário por nota correta pode liberar capacidade para enfrentar a insuficiência atual. A confiança no mecanismo qualitativo é **moderada**, apoiada na confirmação do PM; é **baixa** no tamanho do ganho e em alcançar 250/dia. A revisão BU-fit aprovou o vínculo com esses limites, sem comprovar efeito de solução ou aceleração de ativações. (U-03; revisão BU-fit de U-03; D-003)

O vínculo perde sustentação se espera, dependências ou exceções limitarem a produção, se a carga migrar para conferência/retrabalho ou se o ganho vier com incorreções. Comparar lotes equivalentes, considerando esforço completo e resultado correto, testa esse efeito. (U-03)

## 4. Solução escolhida e alternativas

**Um agente com IA interpreta telas e escolhe ações no percurso completo de extração na 99 e emissão no Mainô, sem APIs desses sistemas, para reduzir a dedicação contínua da pessoa responsável, que mantém a conferência e a autorização das emissões.** S-B é a aposta escolhida em D-004; a resposta literal foi “Opção B”, sem justificativa adicional. Sua eficácia permanece aposta. (S-02; S-B; D-004)

Em alto nível, o agente interpreta o estado apresentado pelas interfaces e escolhe/executa as ações até a emissão concluída no Mainô. A pessoa confere, trata exceções e autoriza a conclusão. A abordagem precisa permitir verificar ações e resultados, relacionando origem e emissão; o relato do agente não comprova conclusão. E-010 sustenta apenas mecanismos genéricos, sem comprovar operação local ou selecionar fornecedor, modelo ou stack. (S-02; S-04; E-010)

| Alternativa considerada | Destino e motivo registrado |
|---|---|
| **S-A · Automação por regras** | Estacionada. Era a recomendação do agente por atacar a repetição com ações explícitas; o PM escolheu S-B. Exige construção e manutenção de regras e não tem ganho local demonstrado. A escolha não comprova superioridade de IA. (S-01; S-A; D-004) |
| **S-E · IA na preparação/conciliação, regras na execução** | Estacionada. A necessidade de interpretar dados com IA não foi demonstrada; seus resultados acrescentam conferência. Permanece alternativa à escolha S-B. (S-01; S-E; D-004) |
| **S-C · Organização manual em lotes** | Estacionada. Mantém execução humana por nota e não há evidência de que reorganização resolva a restrição ou alcance 250/dia. (S-01; S-C; D-004) |
| **S-D · Manter o processo atual** | Descartada nesta direção: conserva esforço e insuficiência declarados. Aguardar Seller não oferece data de resolução conhecida. (S-01; S-D; D-004) |

O escopo cobre extração e emissão concluída, preservando a mesma pessoa responsável. Ficam fora automação isolada de uma ponta, aquisição/uso de APIs da 99 ou Mainô, substituição da pessoa, decisão autônoma de regras fiscais, contratação/terceirização, integração definitiva Seller e ativação de lojas. A restrição às APIs desses dois sistemas não define a infraestrutura de IA. A escolha de direção não autoriza emissão operacional. (S-03; S-02; E-004; D-003; D-004)

## 5. Vínculo U→S, confiança e sinal de parada

Delegar interpretação e execução ao agente busca liberar esforço humano para conferência, autorização e exceções. Só há ganho se diminuir o esforço total por emissão correta, incluindo supervisão e retrabalho. A confiança na eficácia local de S-B e em alcançar 250/dia é **baixa**: não houve teste do mecanismo nos sistemas. A revisão US-fit aprovou a coerência dessa aposta e de seus limites, sem comprovar viabilidade ou desempenho. (S-02; revisão US-fit de S-02; S-B)

Interromper a ampliação da aposta e revisar a direção se o percurso completo não puder ser executado pelas interfaces, se supervisão/conferência/retrabalho anularem o ganho ou se a avaliação mostrar incorreções/duplicatas. Se 250/dia depender da dedicação contínua já considerada inviável, não declarar sucesso. A troca de mecanismo não desfaz atos fiscais concluídos nem recupera o custo de preparação já incorrido. (S-02; S-B; B-03)

## 6. Hipóteses derivadas a validar no design

As hipóteses abaixo vêm de S-04 e ainda não são resultados demonstrados. Operação e responsável fiscal são participantes propostos para estabelecer critérios e avaliação, sem compromisso já assumido por eles. (S-04)

| Tipo | O que precisa ser verdade | Como testar |
|---|---|---|
| **Valor** | Delegar o percurso reduz esforço humano total e permite avançar rumo a 250 emissões corretas/dia. (S-04) | Comparar amostras equivalentes atuais e assistidas, incluindo concentração de segunda, emissões corretas concluídas, supervisão, conferência e retrabalho. Definir prazo, janela e condição sustentável antes de declarar sucesso. (S-04; B-03) |
| **Usabilidade** | A pessoa conduz e confere o trabalho sem supervisão contínua equivalente aos cliques atuais. (S-04) | Avaliar tarefas representativas do percurso inteiro com a operadora, registrando intervenções, entendimento dos resultados, dependência de ajuda e esforço completo. (S-04) |
| **Viabilidade técnica** | O agente interpreta estados e executa ações corretas até concluir no Mainô, sem APIs desses sistemas e com resultado verificável. (S-04) | Prova técnica controlada em condições autorizadas pela operação, confrontando dados e resultados observáveis com fontes e critérios fiscais definidos, registrando erros e intervenções. Documentação ou texto do agente não substituem essa prova. (S-04; E-010) |
| **Viabilidade operacional** | Preparação, supervisão, manutenção e custos de execução cabem na capacidade de suporte e no período de utilidade da iniciativa. (S-04) | Estimar e depois medir custos com responsáveis por operação/suporte; confrontar com prazo ainda a definir e plano Seller atualizado, sem presumir entrega em 15/11 ou duração da frente. (S-04; B-04) |

## 7. Hipóteses herdadas e seu destino

| ID e origem | Estado, motivo e retomada |
|---|---|
| **H-01 · Trabalho manual limita a capacidade** — inferência do intake. | **Validated:** o PM confirmou a restrição em D-003. Validação declaratória, sem medição observada pelos agentes, etapa dominante identificada ou ganho futuro demonstrado. O registro preserva o teste por esforço por etapa e comparação de esforço total com correção. (H-01; U-04; E-009; D-003) |
| **H-02 · Solução rápida com IA utilizável pela pessoa** — stakeholder. | **Parked para teste downstream de S-B escolhida**, sem validação de rapidez, uso ou viabilidade. Testar o percurso completo sem APIs, uso pela operadora e tempo de disponibilização contra prazo a definir. (H-02; B-05; S-01; D-004) |
| **H-03 · IA aumenta emissão** — stakeholder. | **Parked para teste downstream de S-B**, sem ganho demonstrado. Comparar emissões corretas por esforço humano total com e sem IA, incluindo supervisão, conferência e retrabalho, sob as condições de B3 a definir. (H-03; B-05; S-01; B-03; D-004) |
| **H-04 · Capacidade fiscal acelera ativações** — inferência do Business lead. | **Parked:** não foi confirmada e não é necessária ao recorte de insuficiência atual. Retomar se aceleração de ativações integrar promessa ou meta, confrontando motivos reais de liberar/adiar lojas; outra restrição dominante ou capacidade já suficiente contrariam o elo. (H-04; U-04; D-003) |

O estacionamento de H-02/H-03 preserva hipóteses da IA escolhida para avaliação posterior; não descarta S-B. A resolução histórica de H-02 ainda menciona recomendação S-A e gate 3 pendente: essa escolha foi superada por D-004, S-01 e pelo teste atualizado do registro, mantendo a eficácia em aberto. (H-02; H-03; B-05; S-01; D-004)

## 8. Apostas nomeadas e riscos aceitos

O PM **@marcelusfernandes** é dono da aposta **S-B**, escolhida em D-004 com aceite dos riscos explicitados para avançar ao design. Não informou motivo adicional para preferir IA; a aceitação não comprova eficácia nem exige repetir a decisão já tomada. (D-004; S-01; S-02; S-B)

| Risco herdado pela aposta | Aceite e limite |
|---|---|
| Compatibilidade local e confiabilidade do agente ainda não comprovadas; documentação apenas genérica. | PM em D-004, conforme S-02/S-04. A prova técnica permanece por fazer. (S-02; S-04; E-010; D-004) |
| Supervisão, conferência, retrabalho, manutenção e custos de execução podem anular o ganho; 250/dia não foi demonstrado. | PM em D-004. H-02/H-03 e testes de S-04 preservam a necessidade de avaliar ganho líquido e uso real. (S-02; S-04; S-B; H-02; H-03; D-004) |
| B3 sem prazo, janela de comprovação, critérios operacionais de correção ou carga humana sustentável definidos. | PM em D-004 aceitou manter essas lacunas conscientemente abertas para design. Isso permite avançar a direção, sem completar o protocolo ou declarar sucesso. (B-03; S-02; D-004) |

O problema e o elo qualitativo partem da confirmação declaratória aceita em D-003; o baseline não é uma série medida. A duração útil frente à integração Seller também permanece desconhecida. Essas limitações são herdadas pela aposta, sem transformá-las em resultados observados ou prazo aprovado. (U-02; U-03; S-02; S-04; B-04; D-003; D-004)

## 9. Questões abertas entregues ao design

As lacunas a seguir são herdadas do upstream; D-004 aceita avançar com elas. A meta de D-002, o problema de D-003 e a escolha de D-004 continuam decididos. (B-03; S-02; D-002; D-003; D-004)

- **Quando alcançar e por quanto tempo comprovar 250/dia?** Prazo de alcance e janela de avaliação não foram informados. Dezembro e 15/11 não são deadlines desta frente. (B-03; B-04)
- **Qual carga humana é sustentável?** Faltam limite aceitável de esforço, jornada disponível e caracterização da carga completa, incluindo preparação, supervisão, conferência e retrabalho. Oito horas contínuas descrevem o modelo considerado inviável. (B-03; S-04; E-007)
- **Como verificar correção e conclusão fiscal?** Faltam critérios operacionais, modo de verificação e tratamento de exceções definidos com operação/responsável fiscal; a demanda não especificou documento fiscal, entidades emissoras ou regras aplicáveis. Sem essas definições, guardrails propostos ainda não constituem protocolo completo. (B-03; S-03; S-04; E-005)
- **Qual é o baseline observado e a demanda fiscal elegível?** Faltam série de emissões corretas, pendências, tempos por etapa, espera, erros/retrabalho e distribuição real dos volumes, inclusive na segunda-feira. A etapa dominante não foi identificada; 200+ não é valor exato e pedidos não equivalem necessariamente a notas. Esses dados informam avaliação da solução, sem reabrir a existência do problema confirmada pelo PM. (B-02; B-03; U-01; U-02; E-001; E-007)
- **O agente funciona no percurso completo e seu resultado pode ser verificado?** Acesso, compatibilidade, confiabilidade local e intervenções necessárias ainda não foram provados; E-010 cobre mecanismos genéricos. Modelo, fornecedor e stack serão definidos downstream. (S-03; S-04; E-010)
- **Há ganho líquido e uso viável pela operadora?** Faltam comparação com o processo atual, avaliação de supervisão e teste de usabilidade que mostrem redução do esforço sem deslocamento de carga ou incorreções, e que permitam avaliar 250/dia sob as condições de B3. (S-02; S-04; H-02; H-03; B-03)
- **Preparação, manutenção, suporte e custos cabem na utilidade desta frente?** Não foram avaliados, nem houve compromisso informado dos participantes propostos. A entrega Seller, a duração provisória, eventual encerramento e escopo de migração não foram aprovados; 15/11 é início de desenvolvimento. (S-04; B-04; E-006)
