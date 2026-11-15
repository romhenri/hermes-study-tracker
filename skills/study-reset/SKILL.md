---
name: study-reset
description: Limpa todo o setup do Study Tracker (disciplinas, ementas, registros e provas). Use somente quando o usuário pedir explicitamente para resetar, zerar ou apagar tudo do tracker, como num semestre novo.
version: 1.0.0
metadata:
  hermes:
    tags: [education, study, reset]
---

# Study Reset

O reset move todas as notas de `Disciplinas/` e o `Datas/Provas.md` para `.trash/reset-<data-hora>/` no vault. Nada é apagado: o usuário recupera pelo Finder ou pela lixeira do Obsidian.

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

## Passos

1. **Prévia.** Rode `$S reset` (sem `--yes`). Ele só lista os arquivos e não altera nada.
2. **Confirmação.** Mostre a lista ao usuário, diga que todo o histórico de estudo e as provas saem do tracker, e pergunte se ele confirma. Siga só com um "sim" claro na resposta a essa pergunta; o pedido original de reset não conta como confirmação.
3. **Reset.** Rode `$S reset --yes`.
4. **Fim.** Informe onde os arquivos ficaram e ofereça a skill `study-setup` para começar o semestre novo.

Para limpar só uma disciplina ou só uma prova, o reset não serve: oriente o usuário a apagar a nota ou a linha no Obsidian.

Responda em português.
