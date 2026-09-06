#!/usr/bin/env bash
# Collecte → enrichissement → page → publication sur GitHub Pages.
# Usage : ./scripts/publier.sh   (depuis la racine du dépôt)
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/pipeline.py
python3 scripts/dashboard.py

if git diff --quiet -- index.html data/; then
  echo "Rien de neuf : la page publiée est déjà à jour."
  exit 0
fi

git add -A
git commit -q -m "Annonces au $(date +%d.%m.%Y)"
git push -q origin main
echo "Publié → https://bongix.github.io/SaveMrA/  (compter ~1 min avant la mise à jour)"
