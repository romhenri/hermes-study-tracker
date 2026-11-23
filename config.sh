#!/bin/sh
# Aplica no Hermes as configurações que o Study Tracker usa (lista e motivos em CONFIG.md).
# Idempotente: rodar de novo atualiza o que já existe, sem duplicar.
set -e
command -v hermes >/dev/null || { echo "hermes não está no PATH (rode o install.sh do Hermes antes)"; exit 1; }

# 1. Mensagens de agendamento chegam só com o conteúdo, sem "Cronjob Response" nem rodapé.
hermes config set cron.wrap_response false >/dev/null
echo "cron.wrap_response = false"

# Agenda: o Google Calendar entra pelas tools notion-calendar-* do MCP notion. A skill embutida
# google-workspace pede um client_secret do Google Cloud e roubava os pedidos de agenda.
hermes config set skills.disabled '["google-workspace"]' --force >/dev/null
echo "skills.disabled = [google-workspace]"

# Cria ou atualiza um agendamento pelo nome. Este arquivo é a fonte do texto: se o job já
# existe, o texto e o horário são sobrescritos com os daqui.
# Uso: job <nome> <cron> <prompt> [flags extras do create]
job() {
    name=$1 schedule=$2 prompt=$3
    shift 3
    id=$(hermes cron list 2>/dev/null | awk -v n="$name" '
        /^  [0-9a-f]+ \[/ { id = $1 }
        $1 == "Name:" { sub(/^ *Name: */, ""); if ($0 == n) print id }' | head -1)
    if [ -n "$id" ]; then
        hermes cron edit "$id" --schedule "$schedule" --prompt "$prompt" >/dev/null
        echo "cron: '$name' atualizado ($id)"
    else
        hermes cron create "$schedule" "$prompt" --name "$name" "$@" \
            --deliver telegram --timezone America/Sao_Paulo --catch-up off >/dev/null
        echo "cron: '$name' criado"
    fi
}

# 2. Check-in de estudos às 19h nos dias úteis, no Telegram.
job "Check-in de estudos 19h" "0 19 * * 1-5" "Check-in diário de estudos pelo Telegram. Rode o exams e o review do Study Tracker para todas as disciplinas e escreva uma mensagem curta em português. (1) Se houver prova marcada como URGENTE (até 21 dias), comece por ela: disciplina, dias restantes, assuntos pendentes e o ritmo por dia; proponha priorizar essa disciplina hoje e pergunte se eu topo (com duas provas urgentes, pergunte qual priorizar). (2) Até 3 assuntos para revisar, cada um com o motivo em poucas palavras (prova chegando, acerto baixo, dias sem estudar, erro recorrente). (3) Termine perguntando o que eu estudei hoje e quantos exercícios acertei, para eu responder e registrar. Se ainda não houver disciplinas ou histórico, diga isso em uma linha e sugira colar a ementa de uma disciplina. Sem tabelas, no máximo 8 linhas." \
    --skill study-insights

