# Configuração do Hermes

O Study Tracker depende de configurações que vivem em `~/.hermes`, fora deste repositório. Esta página lista todas, quem aplica cada uma e por quê.

## Ordem num Mac novo

1. Instalar o [Hermes Agent](https://github.com/NousResearch/hermes-agent) e escolher o modelo: `hermes setup`.
2. `./install.sh`: liga o vault e as skills, instala o sigaa-tools e registra o MCP `sigaa`.
3. `sigaa init`: salva o login do SIGAA no keychain.
4. `hermes gateway setup`, escolhendo Telegram, e `hermes gateway install`: liga o bot.
5. `./config.sh`: aplica as configurações do Hermes abaixo.

Rodar `install.sh` ou `config.sh` de novo é seguro: os dois atualizam o que já existe, sem duplicar.

## Aplicadas pelo `config.sh`

| Configuração | Valor | Por quê |
|---|---|---|
| `cron.wrap_response` | `false` | Mensagens de agendamento chegam no Telegram só com o conteúdo, sem o cabeçalho "Cronjob Response: …" e o rodapé "To stop or manage this job…". Vale para todos os agendamentos do Hermes. |
| `skills.disabled` | `[google-workspace]` | A agenda passa pelo MCP `notion` (ver [CONNECTIONS.md](CONNECTIONS.md)). A skill embutida `google-workspace` pegava os pedidos de agenda e pedia um arquivo `client_secret` do Google Cloud. |
| Agendamento "Check-in de estudos 19h" | `0 19 * * 1-5`, fuso `America/Sao_Paulo`, skill `study-insights`, entrega `telegram`, `--catch-up off` | Check-in nos dias úteis: prova urgente primeiro (pedindo prioridade), até 3 revisões com o motivo e a pergunta "o que você estudou hoje?". Com o Mac desligado às 19h, o dia é pulado, para não chegar atrasado. |
| Agendamento "Compromissos do dia" | `0 7,12,18 * * *`, fuso `America/Sao_Paulo`, entrega `telegram`, `--catch-up off` | Às 7h, 12h e 18h, os eventos que faltam no dia, lidos do Google Calendar pelo MCP `notion` (somente leitura). Sem evento restante, o agente responde `[SILENT]` e nada chega. |

O texto dos agendamentos está no próprio `config.sh`, que é a fonte dele: edite lá e rode o script de novo. Uma edição feita com `hermes cron edit` é sobrescrita na próxima execução.

## Aplicadas pelo `install.sh`

| Configuração | Onde | Por quê |
|---|---|---|
| Link do vault | `~/.hermes/study-tracker` → este repo | As skills chamam `~/.hermes/study-tracker/scripts/study.py` de qualquer pasta. |
| `skills.external_dirs` | `[~/.hermes/study-tracker/skills]` em `~/.hermes/config.yaml` | O Hermes descobre as skills do repo; editar o repo já atualiza o Hermes. Antes eram symlinks em `skills/education/`, mas o Hermes não acha skill em pasta-symlink na hora de editar, e as melhorias que ele mesmo aprende se perdiam. |
| MCP `sigaa` | `mcp_servers` em `~/.hermes/config.yaml`, `connect_timeout` 60, todas as tools | O servidor leva uns 7 segundos para subir; com o tempo padrão de 30 segundos, a conexão falhava às vezes. |

## Manuais (pessoais ou secretas, nunca no repo)

| Configuração | Onde | Como |
|---|---|---|
| Modelo | `model.provider` e `model.default` em `~/.hermes/config.yaml` | `hermes model`. Qualquer provedor funciona; aqui é `openai-codex`, com login da conta ChatGPT/Codex. |
| Token do bot | `TELEGRAM_BOT_TOKEN` em `~/.hermes/.env` | Criado no @BotFather; `hermes gateway setup` grava. |
| Quem pode falar com o bot | `TELEGRAM_ALLOWED_USERS` em `~/.hermes/.env` | Só o seu ID do Telegram. O bot tem acesso ao terminal do Mac, então nunca deixe vazio. |
| Login do SIGAA | Keychain do macOS | `sigaa init` (ou `sigaa login` depois de trocar a senha). |
