# Hermes Study Tracker

Este repositório é um **vault do Obsidian** que funciona como memória acadêmica do semestre. O usuário conversa com o Hermes Agent ("hoje estudei integrais e acertei 7 de 10", "como estou em Cálculo I?") e o Hermes grava e lê notas Markdown aqui. O usuário lê e edita as mesmas notas no Obsidian.

A ideia central: distinguir assunto **estudado** de assunto **dominado**, com base nos exercícios. O foco é assunto e desempenho, não tempo de estudo.

## Layout

- `Disciplinas/` dados do usuário, uma nota por disciplina (`Cálculo I.md`). Fora do git: o repo é público.
- `scripts/study.py` única porta de leitura e escrita das notas; `--help` lista os comandos.
- `scripts/test_study.py` self-check: `python3 scripts/test_study.py` imprime `ok`.
- `skills/` skills do Hermes, uma por intenção: `study-setup` (disciplinas do semestre), `to-topics` (lista bruta de conteúdos → assuntos e subassuntos), `study-log` (registrar estudo), `study-insights` (relatório, evolução, revisão). A ordem de uso está em `loop.md`.
- `.claude/skills/` symlinks relativos para `skills/`: as mesmas skills no Claude Code, sem cópia.
- `install.sh` liga o repo a `~/.hermes/study-tracker` e as skills a `~/.hermes/skills/education/`.

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

## Regras

- **Leia e grave notas pelo `study.py`.** O parser depende do formato acima; uma edição à mão fora dele some das contas sem erro.
- Mudou o formato ou uma regra de domínio? Atualize o parser, o `test_study.py`, a seção acima e a skill afetada no mesmo commit.
- Limiares de domínio e a heurística de revisão ficam em constantes no topo do `study.py`, fonte única da verdade; as skills só repetem os números para o modelo explicar ao usuário.
- Só stdlib do Python, sem dependências.
- Texto para o usuário em português; código e commits em inglês.
