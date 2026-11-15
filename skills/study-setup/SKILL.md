---
name: study-setup
description: Configura o semestre no Study Tracker. Use quando o usuário quiser cadastrar as disciplinas do semestre, dizer o que já estudou antes de começar, ou quando outra skill do Study Tracker disser que a disciplina não está cadastrada.
version: 1.1.0
metadata:
  hermes:
    tags: [education, study, setup]
---

# Study Setup

Cada disciplina vira uma nota `Disciplinas/<Nome>.md` no vault do Obsidian do usuário. Grave sempre pelo script:

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

## Passos

1. **Disciplinas.** Pergunte as disciplinas do semestre, se o usuário ainda não disse. Rode `$S map` para ver as que já existem e evitar duplicar.
2. **Assuntos.** Para cada disciplina, peça a ementa ou a lista de assuntos e siga a skill `to-topics`, que organiza a lista e grava a nota. Se o usuário ainda não tiver a ementa, crie a nota vazia com `$S setup "Cálculo I"` e siga; os assuntos entram depois pela `to-topics`.
3. **Ponto de partida.** Pergunte o que ele já tinha estudado antes de usar o tracker e marque: `$S status "Cálculo I" "Limites" done` (`doing` para o que está em andamento).
4. **Fim.** Rode `$S map` e mostre o resultado.

Completo quando toda disciplina citada tem nota, e cada uma tem os assuntos aprovados ou o combinado de que eles virão depois.

Responda em português.
