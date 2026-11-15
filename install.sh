#!/bin/sh
# Liga o vault e as skills ao Hermes Agent (symlinks: editar o repo já atualiza o Hermes).
set -e
repo="$(cd "$(dirname "$0")" && pwd)"
home="${HERMES_HOME:-$HOME/.hermes}"
skills="$home/skills/education"
mkdir -p "$skills" "$repo/Disciplinas"
ln -sfn "$repo" "$home/study-tracker"
for s in "$repo"/skills/*/; do
    ln -sfn "${s%/}" "$skills/$(basename "$s")"
done
# Skill única da v1, substituída pelas de skills/.
[ -L "$skills/study-tracker" ] && rm "$skills/study-tracker"
echo "Vault: $repo/Disciplinas | skills: $(ls "$repo/skills" | tr '\n' ' ')"
