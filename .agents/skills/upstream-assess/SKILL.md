---
name: upstream-assess
description: Use no início e após cada avanço material para classificar Problem e Solution separadamente, identificar gates faltantes e escolher a próxima classe de trabalho.
---


# Upstream Assess

Leia `references/matrix-and-gates.md` e `references/evidence-model.md`.

1. Preserve literalmente a hipótese/sinal inicial.
2. Liste outcomes desejados.
3. Liste fatos/evidências disponíveis e unknowns.
4. Avalie separadamente os gates de Problem Definition, Problem Knowledge,
   Solution Definition e Solution Knowledge.
5. Cada gate é `met`, `not-met` ou `unknown`, com Evidence IDs.
6. Derive os quadrantes.
7. Escolha **um** gap crítico e a próxima skill/mode.

Routing:
- Problem Explore → `$problem-work`, mode `explore`
- Problem Frame → `$problem-work`, mode `frame`
- Problem Investigate → `$problem-work`, mode `investigate`
- Problem Ready + Solution não Deliver → `$solution-work`
- Problem Ready + Solution Deliver → `$readiness-review`

Nunca use score numérico como substituto de gate.

