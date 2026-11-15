# Loop de estudo

O semestre é um ciclo: você estuda, conta para o Hermes, ele mostra onde você está e o que revisar, e isso decide o próximo estudo. Antes do ciclo, o setup cadastra as disciplinas e a `to-topics` transforma cada ementa numa to-do list de assuntos. Cada passo usa uma skill de `skills/`, que chama `scripts/study.py`.

```
     ┌──────────────────────────────────────────────────┐
     │ 1. SETUP                     início do semestre  │
     │ skill: study-setup                               │
     │ "minhas disciplinas são Cálculo I e Física I"    │
     │ "a P1 de Cálculo I é dia 2/12, cai limites"      │
     │ → setup · status · exam                          │
     │ cria Datas/Provas.md com as datas de prova       │
     └─────────────────────────┬────────────────────────┘
                               │  cria Disciplinas/<Nome>.md
                               ▼
     ┌──────────────────────────────────────────────────┐
     │ 2. ORGANIZAR ASSUNTOS     ementa nova ou extra   │
     │ skill: to-topics                                 │
     │ "segue a ementa de Cálculo I: ..." (colada)      │
     │ triagem → árvore → prévia → ok                   │
     │ → map · setup                                    │
     │ grava - [ ] Assunto / - [ ] Subassunto           │
     └─────────────────────────┬────────────────────────┘
                               │
 ┌────────────────────────────▶│
 │                             ▼
 │   ┌──────────────────────────────────────────────────┐
 │   │ 3. ESTUDAR                  você, fora do Hermes │
 │   │ aula, leitura, lista de exercícios               │
 │   │ (nenhuma skill)                                  │
 │   └─────────────────────────┬────────────────────────┘
 │                             │
 │                             ▼
 │   ┌──────────────────────────────────────────────────┐
 │   │ 4. REGISTRAR                                     │
 │   │ skill: study-log                                 │
 │   │ "vi MRUV, acertei 6 de 10, errei unidades"       │
 │   │ → log · status                                   │
 │   │ grava em ## Registro, marca [/] ou [x]           │
 │   └─────────────────────────┬────────────────────────┘
 │                             │
 │                             ▼
 │   ┌──────────────────────────────────────────────────┐
 │   │ 5. ANALISAR                                      │
 │   │ skill: study-insights                            │
 │   │ "como estou em Física I?" "estou melhorando?"    │
 │   │ → report · map · compare · history               │
 │   │ estudado ≠ dominado (exercícios decidem)         │
 │   └─────────────────────────┬────────────────────────┘
 │                             │
 │                             ▼
 │   ┌──────────────────────────────────────────────────┐
 │   │ 6. REVISAR                                       │
 │   │ skill: study-insights                            │
 │   │ "o que devo revisar?" ou check-in 19h (Telegram) │
 │   │ → exams · review                                 │
 │   │ prova perto puxa a disciplina e pede prioridade  │
 │   │ acerto baixo · dias parado · erro recorrente     │
 │   └─────────────────────────┬────────────────────────┘
 │                             │
 └─────────────────────────────┘  próximo ciclo: escolhe o que estudar
```

| Passo | Skill | Comandos do `study.py` | Quando |
|---|---|---|---|
| 1. Setup | `study-setup` | `setup`, `status`, `exam` | Início do semestre; data de prova nova ou adiada |
| 2. Organizar assuntos | `to-topics` | `map`, `setup` | Ementa colada no setup, ou lista nova no meio do semestre |
| 3. Estudar | nenhuma | nenhum | Você estuda |
| 4. Registrar | `study-log` | `log`, `status` | Depois de cada sessão |
| 5. Analisar | `study-insights` | `report`, `map`, `compare`, `history` | Quando quiser saber como está |
| 6. Revisar | `study-insights` | `exams`, `review` | Antes de decidir o que estudar; check-in das 19h nos dias úteis |

A `to-topics` também roda fora do setup: colar uma lista nova de conteúdos a qualquer momento ("o professor passou estes tópicos para a P2") acrescenta os assuntos à nota sem apagar os que já existem.

Com prova a até 21 dias, a revisão começa por ela: mostra quantos assuntos faltam dominar e o ritmo por dia, e pergunta se você quer priorizar aquela disciplina.

Os passos 4 a 6 podem acontecer numa mesma mensagem: "vi integrais, acertei 7 de 10; o que revisar amanhã?" aciona `study-log` e depois `study-insights`.
