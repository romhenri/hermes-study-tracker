---
name: study-tracker
description: Memória acadêmica do semestre. Use sempre que o usuário quiser configurar disciplinas e ementas, relatar o que estudou ("hoje estudei integrais e acertei 7 de 10"), marcar um assunto como concluído, ou perguntar sobre progresso, domínio, dificuldades, evolução, revisões ou relatório de uma disciplina.
version: 2.0.0
metadata:
  hermes:
    tags: [education, study, tracking, memory]
---

# Study Tracker

O histórico fica em arquivos Markdown, um por disciplina, em `~/.hermes/study-tracker/` (ou em `$STUDY_DIR`, se definido). Sempre leia e grave pelo script:

```
S="python3 ~/.hermes/skills/education/study-tracker/scripts/study.py"
```

Os arquivos são a fonte da verdade para números. Nunca calcule taxas de acerto nem invente datas de cabeça: consulte o script. Não edite os `.md` direto, a não ser que o usuário peça; o script preserva o que o usuário escreveu à mão (anotações, seções extras como `## Provas`). Use a sua memória própria só para contexto qualitativo (datas de prova, professor, como o usuário prefere estudar).

O foco é **assunto**, não tempo: o que já foi visto, o que está dominado e o que falta. Não pergunte nem registre quanto tempo o usuário estudou.

## Setup do semestre

Rode o setup quando o usuário pedir ("configurar semestre", "minhas disciplinas são...") ou quando ele relatar estudo de uma disciplina que ainda não existe (o script recusa e mostra as cadastradas).

1. Pergunte as disciplinas do semestre, se ele ainda não disse.
2. Para cada disciplina, peça a ementa: os assuntos na ordem do curso e, se ele quiser, os subassuntos. Aceite a ementa colada do plano de ensino e organize você mesmo em assuntos e subassuntos.
3. Use nomes curtos e estáveis ("Integrais", não "Estudo de integrais definidas e indefinidas"), porque são eles que o usuário vai citar depois.
4. Mostre a lista e confirme antes de gravar:
   `$S setup "Cálculo I" "Limites" "Derivadas" "Derivadas/Regra da cadeia" "Integrais"`
   Subassunto = `Pai/Filho`. Rodar `setup` de novo numa disciplina existente só acrescenta o que falta.
5. Se o usuário já viu alguns assuntos antes de começar a usar o tracker, pergunte e marque: `$S status "Cálculo I" "Limites" done`.
6. Termine com `$S map` para ele ver tudo.

A ementa pode crescer depois: `$S add "Cálculo I" "Integrais/Por partes"`.

## Modelo

- **Status** (o que o usuário declara): `todo` não iniciado, `doing` estudando, `done` concluído. Registrar uma sessão muda `todo` para `doing` sozinho. Só marque `done` quando o usuário disser que terminou.
- **Domínio** (o que os exercícios mostram, nas últimas 3 sessões com exercícios): `dominado` (≥80% em ≥10 questões), `em consolidação`, `dificuldade` (<60% em ≥5 questões), `sem exercícios`.

A distinção central: **estudado não é dominado**. Se algo está `concluído` mas não `dominado`, diga isso ao usuário e sugira exercícios.

## Comandos

| Intenção do usuário | Comando |
|---|---|
| "Hoje estudei integrais e acertei 7 de 10" | `$S log "Cálculo I" "Integrais" --correct 7 --total 10` |
| ...e errei sinal e esqueci a constante | acrescente `--mistakes "erro de sinal,esqueceu constante"` (rótulos curtos; reutilize os que já aparecem no `map`/`history`) |
| Só leu ou assistiu aula, sem exercícios | `$S log "Cálculo I" "Integrais"` |
| Estudou ontem / em outra data | `--date AAAA-MM-DD` (converta datas relativas) |
| Observação livre | `--notes "..."` |
| "Terminei limites" | `$S status "Cálculo I" "Limites" done` |
| "O que falta estudar?" / mapa | `$S map ["Cálculo I"]` |
| "Como estou em Cálculo I?" / relatório | `$S report ["Cálculo I"]` |
| "Estou melhorando?" / evolução | `$S compare "Cálculo I" --days 14` (+ `history` para detalhar) |
| "O que devo revisar?" | `$S review [--subject "Cálculo I"] [--n 5]` |
| Sessões passadas | `$S history "Cálculo I" ["Integrais"] [--n 10]` |

Nomes de disciplina e assunto ignoram acento e maiúsculas. Um subassunto pode ser citado só pelo nome ("MRUV" acha "Cinemática/MRUV") se não houver outro igual; se o script disser que é ambíguo, pergunte qual. Se o `log` avisar que o assunto não estava na ementa, confirme com o usuário se era um assunto novo ou um nome diferente para um existente.

## Como responder

- Depois de um `log`, confirme em uma ou duas linhas o que foi registrado e o que mudou ("Integrais saiu de dificuldade para em consolidação", "erro de sinal apareceu de novo, já é recorrente").
- Em relatórios, fale de assuntos: quanto da ementa já foi visto, quanto está dominado, dificuldades, concluídos sem domínio e de 1 a 3 próximos passos concretos.
- Em recomendações de revisão, explique o porquê (acerto baixo, muitos dias sem ver o assunto, erro recorrente).
- Responda em português.
