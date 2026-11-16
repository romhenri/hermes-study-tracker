# Hermes Study Tracker

Este repositório é um **vault do Obsidian** que funciona como memória acadêmica do semestre. O usuário conversa com o Hermes Agent ("hoje estudei integrais e acertei 7 de 10", "como estou em Cálculo I?") e o Hermes grava e lê notas Markdown aqui. O usuário lê e edita as mesmas notas no Obsidian.

A ideia central: distinguir assunto **estudado** de assunto **dominado**, com base nos exercícios. O foco é assunto e desempenho, não tempo de estudo.

## Layout

- `Disciplinas/` dados do usuário, uma nota por disciplina (`Cálculo I.md`). Fora do git: o repo é público.
- `Datas/Provas.md` datas de prova de todas as disciplinas. Também fora do git.
- `scripts/study.py` única porta de leitura e escrita das notas; `--help` lista os comandos.
- `scripts/test_study.py` self-check: `python3 scripts/test_study.py` imprime `ok`.
- `scripts/deck.py` flight deck: painel em texto corrido (lê bem como mensagem do Telegram, sem bloco de código), com notícias, datas e faltas, lendo o CLI `sigaa` e o `Datas/Provas.md`. Self-check: `python3 scripts/test_deck.py`.
- `skills/` skills do Hermes, uma por intenção: `study-setup` (disciplinas do semestre), `to-topics` (lista bruta de conteúdos → assuntos e subassuntos), `study-log` (registrar estudo), `study-insights` (relatório, evolução, revisão), `study-reset` (limpa tudo para um semestre novo). A ordem de uso está em `loop.md`.
- `.trash/` lixeira do vault (a mesma do Obsidian): o `reset` move as notas para `.trash/reset-<data-hora>/` em vez de apagar. Fora do git.
- `.claude/skills/` symlinks relativos para `skills/`: as mesmas skills no Claude Code, sem cópia.
- `install.sh` liga o repo a `~/.hermes/study-tracker` e as skills a `~/.hermes/skills/education/`, instala o [sigaa-tools](https://github.com/PucaVaz/sigaa-tools) fixado num commit revisado (`sigaa_ref`) e registra o MCP `sigaa` no Hermes. O login do SIGAA fica no keychain via `sigaa init`, fora do repo.

## Formato da nota

```markdown
# Cálculo I

## Assuntos
- [ ] Limites
- [/] Derivadas
  - [x] Regra da cadeia

## Registro
- 2026-11-14 | Derivadas | 7/10 | erros: erro de sinal | nota: texto livre
- 2026-11-15 | Limites | —
```

- `[ ]` não iniciado, `[/]` estudando, `[x]` concluído (`[~]` legado também vale estudando). Subassunto = 2 espaços de recuo.
- Registro: data ISO, caminho do assunto (`Pai/Filho`), `acertos/total` ou `—` sem exercícios, campos opcionais `erros:` e `nota:`.
- O script edita só a linha que muda e preserva o resto: texto livre, seções extras (`## Provas`), links. O usuário pode marcar checkbox no Obsidian.

`Datas/Provas.md`, uma linha por prova:

```markdown
- 2026-12-02 | Cálculo I | P1 | assuntos: Limites, Derivadas
- 2026-12-10 | Física I | P2
```

- Sem `assuntos:`, a prova cobre a ementa inteira; um assunto pai cobre seus subassuntos.
- Prova a até `URGENT_DAYS` (21) dias sobe seus assuntos não dominados no `review`, incluindo os nunca estudados; `exams` mostra pendentes e ritmo (assuntos por dia).
- `exam` com disciplina e nome já existentes reescreve a linha (prova adiada); prova passada fica no arquivo e sai do `exams`.

## Regras

- **SIGAA é fonte, não armazenamento.** As skills leem disciplinas, planos e datas pelo MCP `sigaa` e gravam nas notas pelo `study.py`, sempre depois da confirmação do usuário. Ao trocar o `sigaa_ref`, revise o diff do sigaa-tools antes.
- **Leia e grave notas pelo `study.py`.** O parser depende do formato acima; uma edição à mão fora dele some das contas sem erro.
- Mudou o formato ou uma regra de domínio? Atualize o parser, o `test_study.py`, a seção acima e a skill afetada no mesmo commit.
- Limiares de domínio e a heurística de revisão ficam em constantes no topo do `study.py`, fonte única da verdade; as skills só repetem os números para o modelo explicar ao usuário.
- Só stdlib do Python, sem dependências.
- Texto para o usuário em português; código e commits em inglês.
