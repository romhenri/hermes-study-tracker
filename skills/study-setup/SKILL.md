---
name: study-setup
description: Configura o semestre no Study Tracker. Use quando o usuário quiser cadastrar as disciplinas do semestre, informar ou mudar datas de prova, dizer o que já estudou antes de começar, ou quando outra skill do Study Tracker disser que a disciplina não está cadastrada.
version: 1.2.0
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
3. **Provas.** Pergunte as datas de prova de cada disciplina e, se ele souber, quais assuntos caem em cada uma. Grave uma por vez em `Datas/Provas.md`:
   `$S exam "Cálculo I" 2026-12-02 --name P1 --topics "Limites,Derivadas"`
   Sem `--topics`, a prova cobre a ementa inteira. Um assunto pai cobre seus subassuntos. Converta datas como "dia 2 de dezembro" para `AAAA-MM-DD`. Repetir o comando com o mesmo `--name` atualiza a prova (data adiada, assuntos novos).
4. **Ponto de partida.** Pergunte o que ele já tinha estudado antes de usar o tracker e marque: `$S status "Cálculo I" "Limites" done` (`doing` para o que está em andamento).
5. **Fim.** Rode `$S map` e `$S exams` e mostre o resultado.

Completo quando toda disciplina citada tem nota, cada uma tem os assuntos aprovados ou o combinado de que eles virão depois, e as provas informadas estão em `$S exams`.

Datas e assuntos de prova podem chegar a qualquer momento do semestre ("a P2 de Física é dia 10, cai dinâmica"): rode só o passo 3.

Responda em português.
