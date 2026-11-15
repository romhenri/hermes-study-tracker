---
name: study-tracker
description: Memória acadêmica do semestre. Use sempre que o usuário relatar uma sessão de estudo ("hoje estudei integrais por 2h e acertei 7 de 10"), cadastrar disciplinas/assuntos, marcar algo como concluído, ou perguntar sobre progresso, evolução, dificuldades, revisões ou relatório de uma disciplina.
version: 1.0.0
metadata:
  hermes:
    tags: [education, study, tracking, memory]
---

# Study Tracker

Todo o histórico de estudo vive num banco SQLite, acessado por um único script:

```
S="python3 ~/.hermes/skills/education/study-tracker/scripts/study.py"
```

O banco é a fonte da verdade para números. Nunca invente horas, taxas de acerto ou datas: sempre consulte o script antes de responder sobre progresso. Use a sua memória própria só para coisas qualitativas (como o usuário prefere estudar, datas de provas, professor), não para estatísticas.

## Modelo

- **Disciplina** (`subject`): "Cálculo I".
- **Assunto/subassunto** (`path`, separado por `/`): "Integrais", "Integrais/Por partes".
- **Status** que o usuário declara: `todo` (não iniciado), `doing` (estudando), `done` (concluído). Registrar uma sessão muda `todo` para `doing` automaticamente.
- **Domínio** que os dados mostram, calculado nas últimas 3 sessões com exercícios: `dominado` (≥80% em ≥10 questões), `em consolidação`, `dificuldade` (<60% em ≥5 questões), `sem exercícios`.

A distinção central: **estudado não é dominado**. Se algo está `concluído` mas não `dominado`, diga isso ao usuário.

## Antes de gravar

Rode `$S map "<disciplina>"` e reutilize o nome exato que já existe (ex.: o usuário diz "integral" e já existe "Integrais"). Nomes são case-insensitive, mas acentos e plurais diferentes criam duplicatas. Se a disciplina for ambígua, pergunte.

## Comandos

| Intenção do usuário | Comando |
|---|---|
| "Hoje estudei integrais por 2h e acertei 7 de 10" | `$S log "Cálculo I" "Integrais" --min 120 --correct 7 --total 10` |
| ...e errei sinal e esqueci a constante | acrescente `--mistakes "erro de sinal,esqueceu constante"` (rótulos curtos e consistentes; reutilize os já vistos no `map`/`history`) |
| Estudou ontem / em outra data | `--date AAAA-MM-DD` (converta datas relativas) |
| Observação livre | `--notes "..."` |
| Cadastrar ementa / assuntos | `$S add "Cálculo I" "Integrais/Por partes"` (um por assunto) |
| "Terminei limites" | `$S status "Cálculo I" "Limites" done` |
| "O que falta estudar?" / mapa | `$S map ["Cálculo I"]` |
| "Como estou em Cálculo I?" / relatório | `$S report ["Cálculo I"]` |
| "Estou melhorando?" / evolução | `$S compare "Cálculo I" --days 14` (+ `history` para detalhar) |
| "O que devo revisar?" | `$S review [--subject "Cálculo I"] [--n 5]` |
| Sessões passadas | `$S history "Cálculo I" ["Integrais"] [--n 10]` |

Só exercícios contam para domínio: se o usuário só leu/assistiu aula, registre `--min` sem `--correct/--total`.

## Como responder

- Depois de um `log`, confirme em uma ou duas linhas o que foi registrado e comente o que mudou (ex.: "Integrais saiu de dificuldade para em consolidação", "erro de sinal apareceu de novo, já é recorrente").
- Em relatórios e evolução, transforme a saída do script em uma resposta curta e humana: pontos fortes, dificuldades, concluídos sem domínio, e de 1 a 3 próximos passos concretos.
- Em recomendações de revisão, explique o porquê (acerto baixo, muitos dias sem estudar, erro recorrente).
- Responda em português.
