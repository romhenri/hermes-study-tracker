---
name: flight-deck
description: Mostra o flight deck do semestre, um painel de texto com notícias do SIGAA, datas importantes (prazos e provas) e barras de falta. Use quando o usuário pedir o flight deck, painel de bordo, dashboard ou visão geral do semestre.
version: 1.4.0
metadata:
  hermes:
    tags: [education, study, sigaa, dashboard]
---

# Flight Deck

O painel é montado pelo script em texto corrido, feito para ler como mensagem normal (inclusive no Telegram, em fonte proporcional). Rode e repasse a saída sem editar:

```
python3 ~/.hermes/study-tracker/scripts/deck.py
```

- **Atualização.** Por padrão, notícias e prazos vêm da base local do SIGAA e as faltas, ao vivo. Se o usuário pedir dados atualizados ("atualiza", "tem notícia nova?"), acrescente `--sync`: leva uns 40 segundos, avise antes de rodar.
- **Envio.** A saída vai como texto da mensagem, **fora** de bloco de código (sem três crases): no Telegram o bloco vira uma caixa separada. Repasse as linhas como estão, sem reescrever, resumir ou reordenar.
- **Acrônimos.** O painel chama cada disciplina pela sigla definida no setup (`Siglas.md`) ou, sem ela, pelas iniciais das palavras relevantes, com romano virando número (Linguagem de Programação II → LP2). Para mudar uma sigla, use `study.py sigla` pela skill `study-setup`. Use sempre os mesmos acrônimos no texto que você escrever junto com o painel, sem o nome por extenso, a não ser que o usuário pergunte o que um acrônimo significa. Acrônimo é só para nome de disciplina: rótulos como Total, Notícias, Datas e Faltas ficam sempre por extenso.
- **Depois do painel**, no máximo duas linhas: a prova mais próxima e a disciplina com menos margem de faltas, com um próximo passo concreto (ex.: "revise a Segunda Avaliação de SBC: 9 dias"). Para detalhar uma prova, use a skill `study-insights`.
- **Erros.** Linhas no fim começando com "SIGAA indisponível" ou "faltas de" indicam falha de rede ou login: repasse e sugira `sigaa init` no terminal se for login.

Responda em português.
