# Sources d'annonces — Zurich, stagiaire, 6 mois

Classées par rendement attendu pour **ce** profil. « Éligible » = MrA peut
postuler sans être immatriculé.

## Priorité 1 — le réseau ETH (le meilleur rapport signal/bruit)

| Source | Accès | Pourquoi |
|---|---|---|
| **Housing Office UZH/ETH** — [wohnen.ethz.ch](https://www.wohnen.ethz.ch/en) | Réservé aux *membres* ETH/UZH. **À confirmer pour un stagiaire.** Sonneggstrasse 27, +41 44 632 20 37 | Bailleurs privés filtrés, quasi zéro arnaque. Le gisement le plus sain s'il est ouvert. |
| **Marktplatz UZH** — [marktplatz.uzh.ch](https://www.marktplatz.uzh.ch) | Compte UZH/ETH | Petites annonces internes, sous-locations de semestre |
| **Le labo lui-même** | Direct | Un doctorant qui part en conférence 3 mois, un post-doc qui sous-loue : ça ne se publie nulle part. **Demander explicitement à l'équipe dès le premier jour.** |
| **Listes de diffusion / Slack du département** | Via le labo | Idem |

## Priorité 2 — colocations (WG), grand public

| Source | Note |
|---|---|
| [wgzimmer.ch](https://www.wgzimmer.ch) | La référence suisse alémanique pour la WG. Annonces en allemand. Recherche par POST, pas d'API. |
| [flatfox.ch](https://flatfox.ch) | **Collecté automatiquement par ce projet** (`scripts/collecte_flatfox.py`). Comptes régie vérifiés, catégories `SHARED` et `APARTMENT`. |
| [meinwgzimmer.ch](https://www.meinwgzimmer.ch) | Complément de wgzimmer |
| [wg-gesucht.de](https://www.wg-gesucht.de/wg-zimmer-in-Zuerich.159.0.1.0.html) | Plateforme allemande, section Zurich active. **Plus exposée aux faux profils** que les portails suisses. |
| [ronorp.net](https://www.ronorp.net) | Communauté zurichoise, newsletter. Bon pour les sous-locations entre particuliers. |
| [flateroo.com](https://flateroo.com) | Nouvel entrant, volume plus faible |
| [roomino.ch](https://www.roomino.ch) · [weegee.ch](https://weegee.ch) | Complémentaires |
| Groupes Facebook | *« Wohnungen & WG-Zimmer Zürich »*, *« Zurich Expats Housing »* — **le terrain de chasse principal des arnaqueurs.** Utile mais à traiter avec la grille anti-arnaque au complet. |

## Priorité 3 — portails immobiliers classiques

[homegate.ch](https://www.homegate.ch) · [immoscout24.ch](https://www.immoscout24.ch) ·
[comparis.ch](https://en.comparis.ch) · [newhome.ch](https://www.newhome.ch) ·
[urbanhome.ch](https://www.urbanhome.ch) · [tutti.ch](https://www.tutti.ch) ·
[alle-immobilien.ch](https://www.alle-immobilien.ch)

Volume élevé mais **baux longue durée** : peu adapté à 6 mois, sauf à trouver
une reprise de bail (*Nachmieter gesucht*).

## Priorité 4 — meublé / temporaire (la solution de repli d'octobre)

| Source | Note |
|---|---|
| [swiftliving.ch](https://www.swiftliving.ch) | Meublé, courte durée, orienté étudiants/stagiaires |
| [tomodomo.ch](https://www.tomodomo.ch) · [nextgenproperties.ch](https://www.nextgenproperties.ch) | Logements meublés temporaires |
| [tauschwohnung.ch](https://www.tauschwohnung.ch) | Échange de logement |
| [livingscience.ch](https://www.livingscience.ch) | Résidence proche ETH — vérifier l'éligibilité hors immatriculation |
| Auberges / Airbnb au mois | Coûteux, mais couvre les 2–3 premières semaines le temps de visiter sur place |

## Réservé aux étudiants immatriculés — accessible seulement en sous-location

| Source | Condition |
|---|---|
| [woko.ch](https://www.woko.ch) | **Immatriculation obligatoire**, attestation à présenter au guichet. Limite d'âge 30 ans sur une partie du parc. |
| [juwo.ch](https://www.juwo.ch) | « Jeunes adultes **en formation** » — formulation plus large que « étudiant ». **À trancher par téléphone : +41 44 298 20 40.** Portail : portal.juwo.ch/csp |
| [students.ch](https://www.students.ch) · [studentenwohnheim.ch](https://www.studentenwohnheim.ch) · studentvillage.ch · flatable.ch · myhomies.ch | Variable selon l'opérateur |

> ⚠️ Sous-louer une chambre WOKO/Juwo peut exiger que **le sous-locataire soit
> lui aussi étudiant**. À faire confirmer par écrit par la coopérative avant de
> verser quoi que ce soit — sinon MrA risque l'expulsion en cours de stage.

## Rythme de veille recommandé

Le marché zurichois se joue en heures, pas en jours. Une bonne annonce en WG
reçoit 40 réponses le premier jour.

- `python3 scripts/pipeline.py` **tous les matins** (collecte + enrichissement)
- Alertes e-mail activées sur wgzimmer, Flatfox, Homegate, Ron Orp
- Répondre dans les 2 h, avec un message prêt à l'emploi (voir `docs/CANDIDATURE.md`)
