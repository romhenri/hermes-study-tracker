#!/bin/sh
# Liga o vault e as skills ao Hermes Agent (symlinks: editar o repo já atualiza o Hermes).
set -e
repo="$(cd "$(dirname "$0")" && pwd)"
home="${HERMES_HOME:-$HOME/.hermes}"
skills="$home/skills/education"
mkdir -p "$skills" "$repo/Disciplinas" "$repo/Datas"
ln -sfn "$repo" "$home/study-tracker"
for s in "$repo"/skills/*/; do
    ln -sfn "${s%/}" "$skills/$(basename "$s")"
done
# Skill única da v1, substituída pelas de skills/.
[ -L "$skills/study-tracker" ] && rm "$skills/study-tracker"
echo "Vault: $repo/Disciplinas | skills: $(ls "$repo/skills" | tr '\n' ' ')"

# SIGAA (CLI + MCP), fixado num commit revisado; para atualizar, revise o diff e troque o ref.
sigaa_ref=aa0fa9e
if command -v uv >/dev/null && command -v hermes >/dev/null; then
    uv tool install -q "sigaa-tools[mcp] @ git+https://github.com/PucaVaz/sigaa-tools@$sigaa_ref"
    if ! hermes mcp list 2>/dev/null | grep -q '^ *sigaa '; then
        # Respostas: "salvar mesmo sem conectar" (antes do sigaa init) e "habilitar todas as tools".
        printf 'y\nY\n' | hermes mcp add sigaa --command "$HOME/.local/bin/sigaa-mcp" --connect-timeout 60 >/dev/null
    fi
    echo "SIGAA: MCP 'sigaa' no Hermes. Se ainda não fez, rode 'sigaa init' uma vez para salvar seu login."
else
    echo "SIGAA: pulado (precisa de uv e hermes no PATH)."
fi
