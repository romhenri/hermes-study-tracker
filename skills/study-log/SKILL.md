---
name: study-log
description: Registra estudo no Study Tracker. Use quando o usuário contar o que estudou ("hoje vi integrais e acertei 7 de 10"), relatar exercícios ou erros, ou disser que terminou ou começou um assunto.
version: 1.0.0
metadata:
  hermes:
    tags: [education, study, log]
---

# Study Log

Grave sempre pelo script, que escreve nas notas da disciplina no vault do Obsidian:

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

O foco é **assunto e exercícios**: registre o que foi estudado e o desempenho. Tempo de estudo fica fora.

## Comandos

| O usuário diz | Comando |
|---|---|
| "Hoje estudei integrais e acertei 7 de 10" | `$S log "Cálculo I" "Integrais" --correct 7 --total 10` |
| ...errei sinal e esqueci a constante | acrescente `--mistakes "erro de sinal,esqueceu constante"` |
| Só leu ou assistiu aula | `$S log "Cálculo I" "Integrais"` |
| Foi ontem / outra data | `--date AAAA-MM-DD` (converta datas relativas) |
| Observação livre | `--notes "..."` |
| "Terminei limites" | `$S status "Cálculo I" "Limites" done` |
| "Comecei derivadas" | `$S status "Cálculo I" "Derivadas" doing` |

- **Rótulos de erro** são curtos e consistentes: antes de inventar um, veja os que já existem em `$S history "<disciplina>"` e reutilize. É a repetição do mesmo rótulo que revela um erro recorrente.
- **Status** `done` só quando o usuário disser que terminou. Um `log` já muda "não iniciado" para "estudando".

## Nomes

O script ignora acento e maiúsculas, e acha um subassunto só pelo nome ("MRUV" acha "Cinemática/MRUV").

- Disciplina não cadastrada: o script recusa. Use a skill `study-setup` antes de registrar.
- Nome ambíguo: o script lista as opções. Pergunte qual.
- Aviso "não estava na ementa": pergunte se era um assunto novo ou outro nome para um existente; se for o segundo caso, avise que o registro ficou num assunto novo e ajuste a nota com o usuário.
- Disciplina não dita: se só uma disciplina tem esse assunto (`$S map`), use-a; senão, pergunte.

## Resposta

Confirme em uma ou duas linhas o que foi registrado e o que mudou, usando a linha que o script imprime: "Integrais saiu de dificuldade para em consolidação", "erro de sinal apareceu de novo, já é recorrente". Responda em português.
