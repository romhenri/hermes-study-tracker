# Loop de estudo

O semestre é um ciclo: você estuda, conta para o Hermes, ele mostra onde você está e o que revisar, e isso decide o próximo estudo. Antes do ciclo, o setup cadastra as disciplinas e a `to-topics` transforma cada ementa numa to-do list de assuntos. Cada passo usa uma skill de `skills/`, que chama `scripts/study.py`.

```
     ┌──────────────────────────────────────────────────┐
     │ 1. SETUP                     início do semestre  │
     │ skill: study-setup                               │
     │ "minhas disciplinas são Cálculo I e Física I"    │
     │ → setup · status                                 │
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
 │   │ "o que devo revisar?"                            │
 │   │ → review                                         │
 │   │ acerto baixo · dias parado · erro recorrente     │
 │   └─────────────────────────┬────────────────────────┘
 │                             │
 └─────────────────────────────┘  próximo ciclo: escolhe o que estudar
```

| Passo | Skill | Comandos do `study.py` | Quando |
|---|---|---|---|
| 1. Setup | `study-setup` | `setup`, `status` | Início do semestre |
| 2. Organizar assuntos | `to-topics` | `map`, `setup` | Ementa colada no setup, ou lista nova no meio do semestre |
| 3. Estudar | nenhuma | nenhum | Você estuda |
| 4. Registrar | `study-log` | `log`, `status` | Depois de cada sessão |
| 5. Analisar | `study-insights` | `report`, `map`, `compare`, `history` | Quando quiser saber como está |
| 6. Revisar | `study-insights` | `review` | Antes de decidir o que estudar |

A `to-topics` também roda fora do setup: colar uma lista nova de conteúdos a qualquer momento ("o professor passou estes tópicos para a P2") acrescenta os assuntos à nota sem apagar os que já existem.

Os passos 4 a 6 podem acontecer numa mesma mensagem: "vi integrais, acertei 7 de 10; o que revisar amanhã?" aciona `study-log` e depois `study-insights`.
