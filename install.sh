#!/bin/sh
# Liga o vault e as skills ao Hermes Agent (editar o repo já atualiza o Hermes).
set -e
repo="$(cd "$(dirname "$0")" && pwd)"
home="${HERMES_HOME:-$HOME/.hermes}"
mkdir -p "$repo/Disciplinas" "$repo/Datas"
ln -sfn "$repo" "$home/study-tracker"
# Skills por skills.external_dirs, não por symlink: o Hermes não acha skill em pasta-symlink na
# hora de editar, e as melhorias que ele aprende (skill_manage patch) se perdiam.
if command -v hermes >/dev/null; then
    hermes config set skills.external_dirs '["~/.hermes/study-tracker/skills"]' --force >/dev/null
fi
# Symlinks das versões anteriores (education/ e a skill única da v1), substituídos pelo external_dirs.
for l in "$home"/skills/education/*; do
    [ -L "$l" ] && case "$(readlink "$l")" in "$repo"/*) rm "$l" ;; esac
done
[ -L "$home/skills/education/study-tracker" ] && rm "$home/skills/education/study-tracker"
rmdir "$home/skills/education" 2>/dev/null || true
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
