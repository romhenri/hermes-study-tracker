#!/bin/sh
# Liga a skill ao Hermes Agent (symlink, então editar o repo já atualiza a skill).
set -e
dest="${HERMES_HOME:-$HOME/.hermes}/skills/education"
mkdir -p "$dest"
ln -sfn "$(cd "$(dirname "$0")" && pwd)/study-tracker" "$dest/study-tracker"
echo "Skill instalada em $dest/study-tracker"
