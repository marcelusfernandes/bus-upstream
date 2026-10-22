# S-A · Automação por regras do percurso completo

**Disposition:** parked — alternativa por regras não escolhida em D-004; preservada para eventual revisão de S-B.

**Mechanism:** automatizar ações repetitivas nas interfaces da 99 e do Mainô com regras explícitas, mantendo a mesma pessoa responsável pela conferência, exceções e autorização da emissão até sua conclusão no Mainô; sem APIs desses sistemas.

**U→S:** substituir parte da execução manual em todo o percurso pode reduzir a dedicação contínua descrita em U-01. A hipótese exige ganho no esforço total, incluindo a supervisão; não basta acelerar uma etapa e transferir trabalho para outra.

**Trade-offs:** regras tornam explícitas as ações previstas, mas precisam ser construídas e mantidas; telas ou condições não previstas podem impedir a execução. A vantagem de esforço e o tempo para colocar em uso são desconhecidos. A recomendação anterior do agente priorizava repetição com ações explícitas; D-004 escolheu S-B sem demonstrar superioridade empírica entre os mecanismos.

**Assumptions:** as interfaces permitem executar todo o trabalho necessário; as regras podem representar as tarefas repetitivas; conferir e autorizar resultados exige menos esforço que fazê-los manualmente; há critérios de correção fiscal definidos pela operação. A documentação genérica E-010 apoia a existência do mecanismo, não essas condições locais.

**Reversibility:** interromper a automação e retomar operação humana; desenvolvimento e manutenção já consumidos não se recuperam, e emissão concluída tem efeitos que a troca de mecanismo não desfaz.

**Decision:** D-004.

**Evidence:** U-01/U-03; B-03; E-004, E-005, E-007, E-009, E-010; D-002/D-003.
