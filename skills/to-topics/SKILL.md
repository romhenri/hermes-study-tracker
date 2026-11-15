---
name: to-topics
description: Organiza uma lista bruta de assuntos em assuntos e subassuntos de uma disciplina no Study Tracker. Use quando o usuário colar uma ementa, plano de ensino, sumário de livro ou lista solta de conteúdos, ou pedir para organizar os assuntos de uma disciplina.
version: 1.0.0
metadata:
  hermes:
    tags: [education, study, setup, topics]
---

# To Topics

Transforma texto bagunçado numa to-do list de assuntos e subassuntos, gravada na nota `Disciplinas/<Nome>.md` do vault.

```
S="python3 ~/.hermes/study-tracker/scripts/study.py"
```

## Passos

1. **Disciplina.** Descubra de qual disciplina é a lista; se não estiver claro, pergunte. Rode `$S map "<disciplina>"`: se ela já tem assuntos, a lista nova é uma fusão com eles, não uma substituição. Disciplina não cadastrada é criada pelo próprio `setup` do passo 5.
2. **Triagem.** Separe conteúdo de ruído. Ruído sai: numeração ("1.2", "Unidade III"), carga horária, objetivos, metodologia, avaliação, bibliografia, datas.
3. **Árvore.** Monte no máximo dois níveis, assunto e subassunto:
   - **Assunto** é um tema do curso (o título de uma unidade ou capítulo). **Subassunto** é algo em que dá para fazer uma lista de exercícios.
   - Mantenha a ordem do curso.
   - Item que repete outro com palavras diferentes vira um só.
   - Itens soltos com tema em comum ganham um assunto pai; um item que já é um tema inteiro fica como assunto sem filhos.
   - Assunto que já existe na nota mantém o nome exato que está lá.
4. **Nomes.** Curtos e estáveis, de 1 a 4 palavras, porque o usuário vai citá-los ao registrar estudo. Encurte também os títulos de unidade e de item: "Integral indefinida e técnicas" → "Integrais"; "Definição de derivada e reta tangente" → "Definição de derivada". Sem `/` dentro de um nome.
5. **Prévia.** Mostre a árvore exatamente como vai ficar na nota, e embaixo a lista do que foi descartado na triagem:

   ```
   - [ ] Limites
     - [ ] Limites laterais
     - [ ] Continuidade
   - [ ] Derivadas
   ```

   Ajuste o que o usuário pedir. Grave só depois do ok, com cada subassunto como `Pai/Filho`:
   `$S setup "Cálculo I" "Limites" "Limites/Limites laterais" "Limites/Continuidade" "Derivadas"`
6. **Fim.** Rode `$S map "<disciplina>"` e mostre o resultado.

Completo quando cada item de conteúdo do texto original está na árvore (sozinho ou fundido com outro) ou aparece na lista de descartados, e a nota mostra a árvore aprovada.

Responda em português.
