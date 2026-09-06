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

# Le message « Annonces au … » ne vaut que pour une mise à jour de données.
# Si du code ou de la documentation a changé, c'est un commit à écrire à la
# main : trois commits « Annonces au 06.09.2026 » contenant en fait le filtre
# anti-annonces-réservées et le module d'ameublement, ça s'est déjà produit.
autres=$(git status --porcelain -- . ':(exclude)index.html' ':(exclude)data' | wc -l | tr -d ' ')
if [ "$autres" != "0" ]; then
  echo "Des fichiers hors données ont changé :"
  git status --short -- . ':(exclude)index.html' ':(exclude)data'
  echo
  echo "Committez-les d'abord avec un vrai message, puis relancez ce script."
  exit 1
fi

git add index.html data
git commit -q -m "Annonces au $(date +%d.%m.%Y)"
git push -q origin main
echo "Publié → https://bongix.github.io/SaveMrA/  (compter ~1 min avant la mise à jour)"
