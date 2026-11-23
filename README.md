```
█████ █████ █   █ ████  █   █
█       █   █   █ █   █  █ █
█████   █   █   █ █   █   █
    █   █   █   █ █   █   █
█████   █   █████ ████    █

█████ ████   ███  █████ █   █ █████ ████
  █   █   █ █   █ █     █  █  █     █   █
  █   ████  █████ █     ███   ████  ████
  █   █  █  █   █ █     █  █  █     █  █
  █   █   █ █   █ █████ █   █ █████ █   █
```

> Hermes Agent setup that turns daily study logs into an academic memory: progress, mastery, weak spots and review picks.

Um copiloto de estudos para o semestre. Você conta para o [Hermes Agent](https://github.com/NousResearch/hermes-agent), pelo terminal ou pelo Telegram, o que estudou e quanto acertou, e ele mantém uma nota Markdown por disciplina num vault do Obsidian: a ementa como to-do list e o registro de cada sessão.

A ideia central é separar assunto **estudado** de assunto **dominado**. O status vem do que você declara; o domínio vem dos exercícios (≥80% em ≥10 questões nas últimas sessões). É isso que permite apontar dificuldades, erros recorrentes, conteúdos "concluídos" sem domínio comprovado e o que revisar primeiro.

## Loop

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

Detalhes de cada passo em [`loop.md`](loop.md).

## Instalação

macOS e Linux, com Python 3 e o [Hermes Agent](https://github.com/NousResearch/hermes-agent) já instalado e configurado (`hermes setup`):

```sh
git clone https://github.com/romhenri/hermes-study-tracker.git
cd hermes-study-tracker
./install.sh
```

O `install.sh` liga o repo a `~/.hermes/study-tracker` e as skills a `~/.hermes/skills/education/`. Depois, `sigaa init`, `hermes gateway setup` (Telegram) e `./config.sh`; a ordem completa e cada configuração estão em [`CONFIG.md`](CONFIG.md). Integrações opcionais (Notion, Google Calendar, Todoist) em [`CONNECTIONS.md`](CONNECTIONS.md). Depois, abra a pasta como vault no Obsidian: as notas aparecem em `Disciplinas/`.

## Exemplo de uso

```text
você   ▸ Organiza os assuntos de Cálculo I: "UNIDADE I - Limites (12h): noção
         intuitiva; limites laterais; continuidade. UNIDADE II - Derivadas: ..."
hermes ▸ Gravado em "Cálculo I". Descartados: numeração, carga horária e bibliografia.

você   ▸ Hoje fiz substituição, 5 de 10, esqueci de trocar os limites de integração.
hermes ▸ Registrado. Substituição está em dificuldade.

você   ▸ Como estou em Cálculo I? O que devo revisar primeiro?
hermes ▸ Acerto geral de 60% em 40 exercícios. Domínio comprovado: Regra da cadeia.
         Revise primeiro Limites laterais: 50% de acerto, 10 dias sem estudar e
         erro de sinal recorrente.
```

A nota resultante, `Disciplinas/Cálculo I.md`:

```markdown
## Assuntos
- [ ] Limites
  - [/] Limites laterais
  - [x] Continuidade
- [ ] Integrais
  - [/] Substituição

## Registro
- 2026-11-05 | Limites/Limites laterais | 6/10 | erros: erro de sinal
- 2026-11-15 | Integrais/Substituição | 5/10 | erros: esqueceu de trocar os limites de integração
```

## Desenvolvimento

Só stdlib do Python, sem dependências. O formato das notas e as regras para agentes estão em [`AGENTS.md`](AGENTS.md).

```sh
python3 scripts/test_study.py   # imprime "ok"
python3 scripts/study.py --help
```
