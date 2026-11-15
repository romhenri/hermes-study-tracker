---
name: study-insights
description: Analisa o progresso no Study Tracker. Use quando o usuário perguntar como está numa disciplina, o que falta estudar, se está melhorando, o que revisar, quais as dificuldades, ou pedir um relatório.
version: 1.0.0
metadata:
  hermes:
    tags: [education, study, report, review]
---

# Study Insights

Os números vêm do script, que lê as notas da disciplina no vault do Obsidian. Rode o comando antes de responder; taxas, datas e contagens saem da saída dele, nunca de cabeça.

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

| O usuário pergunta | Comando |
|---|---|
| "Como estou em Cálculo I?" / relatório | `$S report ["Cálculo I"]` |
| "O que falta estudar?" / mapa da ementa | `$S map ["Cálculo I"]` |
| "Estou melhorando?" / evolução | `$S compare "Cálculo I" --days 14`, depois `$S history "Cálculo I"` para detalhar |
| "O que devo revisar?" | `$S review [--subject "Cálculo I"] [--n 5]` |
| Histórico de um assunto | `$S history "Cálculo I" "Integrais" [--n 10]` |

Sem disciplina citada, rode sem ela (todas). Disciplina não cadastrada: ofereça a skill `study-setup`.

## Status vs. domínio

- **Status** é o que o usuário declara: não iniciado, estudando, concluído.
- **Domínio** é o que os exercícios mostram, nas últimas 3 sessões com exercícios: `dominado` (≥80% em ≥10 questões), `em consolidação`, `dificuldade` (<60% em ≥5 questões), `sem exercícios`.

**Estudado não é dominado.** Todo assunto concluído sem domínio comprovado entra na resposta, com sugestão de exercícios.

## Resposta

- **Relatório:** quanto da ementa já foi visto, quanto está dominado, dificuldades, concluídos sem domínio e de 1 a 3 próximos passos concretos.
- **Evolução:** a variação de acerto entre os períodos e quais assuntos puxaram a mudança.
- **Revisão:** cada recomendação com o porquê (acerto baixo, dias sem ver o assunto, erro recorrente).

Curto e em português.
