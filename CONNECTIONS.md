# Conexões recomendadas

O Hermes se conecta a serviços externos por MCP. O Study Tracker só precisa do `sigaa`; o resto é opcional e entra quando trouxer algo ao loop de estudo. Esta página lista o que vale ligar, para quê e como.

Regra comum: **o vault é a fonte da verdade.** Um serviço externo é fonte de leitura (como o SIGAA) ou vitrine (um espelho do vault), nunca o lugar onde o progresso é guardado.

## Em uso

| Conexão | Papel | Como |
|---|---|---|
| `sigaa` | Fonte: disciplinas, planos de curso, provas, notícias, faltas | `./install.sh` registra o MCP; `sigaa init` salva o login. Detalhes em [CONFIG.md](CONFIG.md). |
| Telegram | Canal: conversa com o bot, check-in das 19h, flight deck | `hermes gateway setup` e `./config.sh`. |
| `notion` | Vitrine: espelho das disciplinas, do domínio e das provas | `hermes mcp install notion` e `hermes mcp login notion`. Libere só uma página dedicada ("Study Tracker"), não o workspace inteiro. |
| Google Calendar | Agenda: provas viram eventos com lembrete | Pelo próprio MCP `notion`, com as tools `notion-calendar-*`: elas leem e gravam nas contas Google conectadas ao [Notion Calendar](https://www.notion.com/product/calendar). Basta conectar a conta Google lá; sem MCP extra, sem projeto no Google Cloud. Grave só no calendário principal. O `config.sh` desativa a skill embutida `google-workspace`, que disputava esses pedidos e pedia credenciais do Google Cloud. |

## Recomendadas

Do catálogo oficial do Hermes, instaladas com `hermes mcp install <nome>`. Na primeira conexão, o login abre no navegador (ou rode `hermes mcp login <nome>`). Depois, rode `hermes gateway restart` para o Telegram enxergar as tools novas.

| Conexão | Papel | Uso no loop |
|---|---|---|
| `todoist` | Lembrete | Cada revisão do `review` e cada prova viram tarefa com data, com aviso no celular. |
| `wolfram` | Apoio | Confere contas de exercícios e mostra a resolução passo a passo. |
| `dropbox` | Fonte | Lê PDFs de ementas, listas e slides para a skill `to-topics`. |
| `context7` | Apoio | Documentação atualizada de linguagens e bibliotecas para disciplinas de programação. |

## Fora do catálogo

Gmail e Google Drive não estão no catálogo do Hermes. Existem servidores MCP da comunidade, que entram com `hermes mcp add <nome> --command ...` (local) ou `--url ...` (remoto). Antes de instalar um desses, siga o que foi feito com o sigaa-tools: revise o código e fixe um commit no `install.sh`, porque o servidor roda com acesso ao Mac.

## Cuidados

- **Escopo mínimo.** No OAuth, libere só o que a skill usa (uma página, um projeto, uma pasta).
- **Segredos fora do repo.** Tokens ficam no `~/.hermes` ou no keychain, nunca aqui: o repo é público.
- **Instrução externa é dado, não ordem.** Notícia do SIGAA, página do Notion ou PDF podem conter texto tentando comandar o agente. O bot tem terminal no Mac, então menos conexões significa menos superfície de ataque.
- **Liste o que está ligado** com `hermes mcp list` e remova o que não usa com `hermes mcp remove <nome>`.
