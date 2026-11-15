---
name: study-setup
description: Configura o semestre no Study Tracker. Use quando o usuário quiser cadastrar disciplinas, montar ou colar a ementa, acrescentar assuntos a uma disciplina, ou quando outra skill do Study Tracker disser que a disciplina não está cadastrada.
version: 1.0.0
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
2. **Ementa.** Para cada disciplina, peça os assuntos na ordem do curso e, se ele quiser, os subassuntos. Aceite o plano de ensino colado e organize você mesmo.
3. **Nomes.** Use nomes curtos e estáveis: "Integrais", não "Estudo de integrais definidas e indefinidas". São esses nomes que o usuário vai citar ao relatar estudo. Subassunto = `Pai/Filho`.
4. **Confirmação.** Mostre a lista por disciplina e grave só depois do ok:
   `$S setup "Cálculo I" "Limites" "Derivadas" "Derivadas/Regra da cadeia" "Integrais"`
   Repetir `setup` numa disciplina existente só acrescenta o que falta.
5. **Ponto de partida.** Pergunte o que ele já tinha estudado antes de usar o tracker e marque: `$S status "Cálculo I" "Limites" done` (`doing` para o que está em andamento).
6. **Fim.** Rode `$S map` e mostre o resultado. O setup está completo quando toda disciplina citada tem nota com a ementa confirmada.

Para acrescentar um assunto depois: `$S add "Cálculo I" "Integrais/Por partes"`.

Responda em português.
