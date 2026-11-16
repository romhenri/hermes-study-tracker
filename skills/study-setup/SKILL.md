---
name: study-setup
description: Configura o semestre no Study Tracker. Use quando o usuário quiser cadastrar as disciplinas do semestre, importar disciplinas ou provas do SIGAA, informar ou mudar datas de prova, dizer o que já estudou antes de começar, ou quando outra skill do Study Tracker disser que a disciplina não está cadastrada.
version: 1.3.0
metadata:
  hermes:
    tags: [education, study, setup]
---

# Study Setup

Cada disciplina vira uma nota `Disciplinas/<Nome>.md` no vault do Obsidian do usuário. Grave sempre pelo script:

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

**SIGAA.** Quando as ferramentas `sigaa_*` do MCP `sigaa` estiverem disponíveis, elas são a fonte de disciplinas, planos de curso e datas: busque lá primeiro e use o usuário para confirmar e completar. Sem o MCP, ou se ele responder erro de login (peça para o usuário rodar `sigaa init` no terminal), pergunte tudo ao usuário. As ferramentas `sigaa_*` aqui são só de leitura.

## Passos

1. **Disciplinas.** Rode `$S map` para ver as que já existem e evitar duplicar.
   - Com SIGAA: `sigaa_list_classes` traz as turmas matriculadas (código e nome em maiúsculas). Proponha os nomes em grafia normal, com acento ("CALCULO NUMERICO" → "Cálculo Numérico"), e confirme a lista com o usuário.
   - Sem SIGAA: pergunte as disciplinas do semestre.
2. **Assuntos.** Para cada disciplina, consiga a lista de assuntos e siga a skill `to-topics`, que organiza e grava a nota.
   - Com SIGAA: `sigaa_get_course_plan(class_code)` traz o plano de curso, cujo `schedule` descreve cada aula. Quando as descrições forem conteúdo ("Integração numérica: trapézio"), use-as como a lista bruta da `to-topics`; se forem genéricas ("Aula 1"), trate como plano vazio.
   - Sem SIGAA, ou plano vazio: peça a ementa ao usuário. Se ele não tiver, crie a nota vazia com `$S setup "Cálculo I"`; os assuntos entram depois pela `to-topics`.
3. **Provas.** Grave uma prova por vez em `Datas/Provas.md`:
   `$S exam "Cálculo I" 2026-12-02 --name P1 --topics "Limites,Derivadas"`
   - Com SIGAA: para cada turma, junte as `evaluations` do `sigaa_get_course_plan(class_code)` com os itens `avaliacao` de `sigaa_list_deadlines(class_code)`. Fique com as datas futuras; converta `DD/MM/AAAA` para `AAAA-MM-DD` e use a descrição como `--name`. Reposição e exame final só entram se o usuário quiser. Professores deixam datas velhas ou conflitantes no plano (avaliação de outro semestre, tabela e cronograma divergindo): aponte cada conflito e pergunte qual data vale. Mostre a lista por disciplina, marcando os "a confirmar", e grave depois do ok.
   - Sem SIGAA: pergunte as datas.
   - Pergunte quais assuntos caem em cada prova. Sem `--topics`, a prova cobre a ementa inteira; um assunto pai cobre seus subassuntos. Repetir o comando com o mesmo `--name` atualiza a prova (data adiada, assuntos novos).
4. **Ponto de partida.** Pergunte o que ele já tinha estudado antes de usar o tracker e marque: `$S status "Cálculo I" "Limites" done` (`doing` para o que está em andamento).
5. **Fim.** Rode `$S map` e `$S exams` e mostre o resultado.

Completo quando toda disciplina confirmada tem nota, cada uma tem os assuntos aprovados ou o combinado de que eles virão depois, e as provas confirmadas estão em `$S exams`.

Datas e assuntos de prova podem chegar a qualquer momento do semestre ("a P2 de Física é dia 10, cai dinâmica", "puxa as provas novas do SIGAA"): rode só o passo 3.

Responda em português.
