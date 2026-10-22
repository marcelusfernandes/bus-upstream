# Business problem

**Statement:** A capacidade atual de emissão fiscal do Marketplace não atende à demanda das 15 dark stores, segundo o PM, comprometendo a sustentação da operação durante a expansão 3P.

**State:** Outcome escolhido em D-001 e meta de 250 emissões/dia decidida como opção própria em D-002. B-01/B-02/B-03/B-04 foram atualizados para revisão independente; B-05 foi atualizado aos estados atuais do registro de hipóteses. A meta não foi atingida ou medida nesta etapa. B3 permanece conscientemente aberto (knowingly open): D-004 aceita avançar com prazo, janela de comprovação e guardrails operacionais ainda indefinidos, herdados pelo design e PRD. Isso permite encerrar o trabalho upstream de Business, sujeito à revisão do orchestrator, sem declarar completo o protocolo de sucesso.

## Reading order

1. [B-01](answers/B-01.md) e [B-02](answers/B-02.md): problema atual e baseline declaratório atualizado.
2. [B-03](answers/B-03.md): meta decidida de 250 emissões/dia e condições ainda desconhecidas.
3. [B-04](answers/B-04.md) e [B-05](answers/B-05.md): relevância atual e hipóteses encaminhadas.
4. [E-007](evidence/E-007.md), [D-002](../decisions/D-002.md), [E-006](evidence/E-006.md) e [D-001](../decisions/D-001.md): relato e decisões do PM; intake e evidências anteriores preservados.
5. [Hipóteses](../hypotheses.md) e [review.md](review.md): H-01 validada declaratoriamente em U; H-04 estacionada em U; H-02/H-03 estacionadas em S para teste downstream da escolha D-004.

## Questions

| ID | Estado e limite |
|---|---|
| B-01 | evidenced — insuficiência atual relatada pelo PM; causa raiz e magnitude não medidas. |
| B-02 | evidenced — 15 lojas, 80 notas/dia com 8h contínuas consideradas inviáveis e 200+ na segunda; baseline declaratório. |
| B-03 | open (knowingly open) — meta de 250/dia decidida em D-002; D-004 aceita avançar com prazo, janela e guardrails de correção e esforço ainda abertos, herdados pelo PRD. Não bloqueiam a direção; impedem declarar sucesso antes de definição e verificação. |
| B-04 | evidenced — problema presente e expansão em curso; dezembro é expectativa e 15/11 é início de desenvolvimento, sem entrega prevista. |
| B-05 | evidenced — H-01 validated por confirmação declaratória do PM; H-04 parked; H-02/H-03 parked para teste downstream de S-B escolhido em D-004. |

O novo relato E-007 atualiza 8 lojas históricas para 15 atuais e a insuficiência antes desconhecida para insuficiência explicitamente declarada. Não equivale a observação independente ou prova causal. A meta já foi decidida e não será novamente submetida para aprovação. As lacunas de B3 seguem para validação posterior conforme o aceite de D-004; esse aceite não comprova compatibilidade local, ganho líquido ou 250/dia.

D-1 é rotina operacional relatada; 200+ é limite inferior; 8h descreve esforço atual considerado inviável, não orçamento para a nova meta. Correção fiscal e esforço sustentável exigem definição operacional. O papel provisório desta iniciativa permanece inferência sem prazo final aprovado; APIs seguem fora do escopo.
