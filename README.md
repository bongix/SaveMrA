# SaveMrA

Recherche de logement à Zurich pour **MrA**, stagiaire au *Laboratorium für
Anorganische Chemie* de l'ETH (bâtiment **HCI**, campus **Hönggerberg**), du
**1er octobre 2026 au 31 mars 2027**, pour **CHF 1 600/mois** au maximum.

Trois questions structurent l'outil, dans cet ordre :

1. **Combien de temps pour aller au labo ?** — itinéraire ZVV/CFF réel, pas une
   distance à vol d'oiseau. Classement en tranches A à E.
2. **Est-ce que l'annonce est vraie ?** — indice de véracité 0–100 %, grille
   dérivée des schémas d'arnaque locative documentés en Suisse.
3. **Est-ce lisible ?** — chaque annonce est étiquetée par langue et accompagnée
   d'un résumé en français.

**Page publique, à donner à MrA** : https://bongix.github.io/SaveMrA/
(miroir privé : https://claude.ai/code/artifact/87d7dd30-51ad-4755-9d0f-c688f62ca9bf)

## Démarrer

```bash
cd ~/SaveMrA && python3 scripts/pipeline.py && python3 scripts/dashboard.py && open index.html
```

Comptez ~10 minutes au premier passage (l'API des transports est bridée), puis
quelques secondes : les itinéraires sont mis en cache par arrêt.

## Les commandes

| Commande | Effet |
|---|---|
| `python3 scripts/pipeline.py` | Collecte Flatfox + enrichissement complet |
| `python3 scripts/pipeline.py --local` | Ré-enrichit sans recollecter (après une saisie manuelle) |
| `python3 scripts/dashboard.py` | Régénère `index.html` (la page publique) |
| `./scripts/publier.sh` | Tout enchaîne : collecte, page, commit, push sur GitHub Pages |
| `python3 scripts/commute.py "Zürich, Oerlikon"` | Temps de trajet d'un point vers les deux campus |
| `python3 scripts/langue.py "möbliertes Zimmer"` | Test du détecteur de langue |
| `python3 scripts/collecte_flatfox.py 30` | Collecte seule, sur 30 jours |

## Ce qu'il y a dans le dossier

```
docs/BRIEF.md          le profil, les contraintes, les questions ouvertes
docs/SOURCES.md        où chercher, et où MrA a le droit de postuler
docs/ANTI-ARNAQUE.md   la grille de véracité, signal par signal
docs/GLOSSAIRE.md      décoder une annonce en allemand
docs/CANDIDATURE.md    le message à envoyer, le dossier à préparer

data/criteres.json     budget, tranches de prix, période du séjour
data/campus.json       les deux campus ETH — change ici le campus de référence
data/tranches.json     les seuils des tranches de trajet
data/annonces.json     le jeu de données enrichi (sortie du pipeline)
data/cache_trajets.json cache des itinéraires, supprimable sans risque

scripts/collecte_flatfox.py  collecteur Flatfox
scripts/commute.py           itinéraires réels via transport.opendata.ch
scripts/veracite.py          scoring anti-arnaque
scripts/langue.py            détection de langue
scripts/pipeline.py          orchestration
scripts/dashboard.py         génération du tableau de bord
scripts/publier.sh           collecte + page + push GitHub Pages, en une commande

index.html             le tableau de bord, autonome — servi tel quel par GitHub Pages
```

## Sources de données

- **Annonces** : API publique de [Flatfox](https://flatfox.ch). Elle ignore tous
  les filtres serveur et renvoie le catalogue suisse entier trié
  chronologiquement — on remonte donc les dernières pages et on filtre côté
  client sur les NPA zurichois. Les autres portails (wgzimmer, Ron Orp,
  wg-gesucht) n'ont pas d'API ouverte : ils se saisissent à la main, voir
  ci-dessous.
- **Itinéraires** : [transport.opendata.ch](https://transport.opendata.ch)
  (horaires CFF/ZVV réels, sans clé d'API, bridé — d'où le cache).

## Ajouter une annonce trouvée ailleurs

Toute annonce ajoutée à la main dans `data/annonces.json` est enrichie comme les
autres et **survit aux collectes suivantes** (le pipeline reconnaît les entrées
dont la `source` n'est pas Flatfox).

```json
{
  "id": "wgzimmer-2026-09-06-a",
  "source": "wgzimmer.ch",
  "url": "https://www.wgzimmer.ch/…",
  "titre": "WG-Zimmer in Wipkingen, möbliert",
  "description": "…texte original de l'annonce…",
  "prix_chf": 950,
  "charges_incluses": true,
  "pieces": 1,
  "surface_m2": 16,
  "meuble": true,
  "temporaire": true,
  "type": "SHARED",
  "adresse": "Rosengartenstrasse 12, 8037 Zürich",
  "lat": 47.3915, "lon": 8.5262,
  "date_emmenagement": "2026-10-01",
  "photos": 4,
  "regie": null,
  "signaux_manuels": ["visite_proposee", "colocs_joignables"]
}
```

`lat`/`lon` donnent le calcul de trajet le plus juste ; à défaut, renseignez
`arret_proche` (nom d'arrêt ZVV exact) ou une `adresse` complète.

## Limites connues, à ne pas oublier

- **Un seul portail collecté automatiquement.** L'essentiel du marché de la
  colocation zurichoise est sur wgzimmer.ch et Ron Orp, sans API. Le dashboard
  ne montre donc pas tout le marché — il montre ce qui est automatisable, et
  sert de socle pour y coller le reste à la main.
- **Les signaux d'arnaque les plus décisifs se constatent au contact**, pas dans
  les données. Un score de 68 % sur une annonce jamais contactée veut surtout
  dire « rien de suspect dans les métadonnées ».
- **Le campus de référence est ETH Hönggerberg (bâtiment HCI)**, confirmé par
  l'adresse du labo. Le temps vers ETH Zentrum reste calculé et affiché.
- **Le trajet est calculé pour une arrivée à 9 h un mardi.** Un horaire de labo
  décalé (arrivée 8 h, retour 20 h) change les correspondances en périphérie.
- **Le résumé français est reconstruit depuis les données structurées**, pas
  traduit mot à mot. Le texte original reste dans `description`, avec son
  étiquette de langue ; `docs/GLOSSAIRE.md` suffit à le décoder.
