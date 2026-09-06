# SaveMrA — brief de recherche

## Le profil

| | |
|---|---|
| **Qui** | MrA, **stagiaire** (pas étudiant inscrit) |
| **Où** | **Laboratorium für Anorganische Chemie**, Vladimir-Prelog-Weg 1-5/10, 8093 Zürich — bâtiment **HCI**, campus **ETH Hönggerberg** |
| **Quand** | **octobre 2026 → mars 2027**, soit ~6 mois |
| **Cherche** | Appartement, studio ou **chambre en colocation (WG)** |
| **Budget** | **≤ CHF 1 600/mois** charges comprises |

## Les trois contraintes qui structurent tout

### 1. Il n'est pas étudiant — c'est le vrai obstacle

Le parc de logements bon marché de Zurich (WOKO, résidences, chambres à
CHF 500–800) est **réservé aux personnes immatriculées** dans une haute école
zurichoise. WOKO l'exige explicitement : il faut présenter une attestation
d'immatriculation au guichet. Un stagiaire, même à l'ETH, n'y a pas droit
en direct.

**Trois portes restent ouvertes :**

- **La sous-location.** Un étudiant WOKO/Juwo part en échange au semestre de
  printemps (février → juin) et sous-loue sa chambre. C'est le mécanisme le plus
  courant, et il tombe pile sur la seconde moitié du séjour de MrA.
  ⚠️ À vérifier auprès de chaque coopérative : plusieurs exigent que le
  sous-locataire soit lui aussi étudiant. À demander par écrit, jamais deviner.
- **Juwo (Jugendwohnnetz).** Cible les « jeunes adultes **en formation** »
  (*in Ausbildung*), pas strictement les immatriculés. Un stage encadré peut
  entrer dans la définition. **À trancher par un appel : +41 44 298 20 40.**
- **Le Housing Office UZH/ETH** (Sonneggstrasse 27, +41 44 632 20 37). Il met en
  relation des bailleurs privés avec les *membres* de l'ETH — pas seulement les
  étudiants. Si le labo ouvre un compte ETH à MrA, l'accès à ce portail est
  probablement le meilleur gisement d'annonces saines du dossier.
  **Action n°1 : faire poser la question par le responsable de stage.**

### 2. La fenêtre octobre → mars est la pire moitié de l'année

Octobre = rentrée du semestre d'automne : c'est le pic de demande, tout part en
48 h. Février = début du semestre de printemps et départs en échange : l'offre
se desserre. Conséquence pratique : **prévoir une solution en deux temps** —
un hébergement d'appoint pour octobre–janvier (chambre meublée, Swift Living,
sous-location courte) puis un vrai bail dès février si nécessaire.

Un séjour de 6 mois est aussi trop court pour la plupart des baux ordinaires
(résiliation trimestrielle). Il faut viser explicitement : *befristet*,
*Zwischenmiete*, *Untermiete*, *temporary*, *sublet*.

### 3. Le labo est à Hönggerberg, pas au Zentrum

**Tranché le 2026-09-06** par l'adresse du labo : *Vladimir-Prelog-Weg* est
l'artère du bâtiment **HCI**, sur le campus **Hönggerberg** (Science City), au
nord-ouest — pas sur le campus historique mitoyen de l'UZH.

Ce n'est pas un détail : la géographie du logement s'inverse. Hönggerberg est
desservi par les bus **69** (depuis Milchbuck) et **80** (depuis Oerlikon et
Bucheggplatz), sans tram ni train direct. Les quartiers qui gagnent :

- **8049 Höngg** — au pied du campus, 5 à 10 min
- **8052 Seebach / Affoltern** et **Oerlikon** — 11 à 15 min par le bus 80
- **8037 Wipkingen** et **8057 Unterstrass** — 10 à 20 min

Les quartiers du centre (8001, 8006, 8032), excellents pour le Zentrum,
retombent à 25–35 min. Le classement se fait donc sur Hönggerberg
(`data/campus.json` → `campus_principal`), et le temps vers ETH Zentrum reste
affiché en second : utile pour les cours, les séminaires et la vie en ville.

## Critères de classement

**Tranches de trajet** (porte-à-porte, transports publics réels, arrivée 9 h un
mardi — marche jusqu'à l'arrêt comprise) :

| Code | Tranche | Lecture |
|---|---|---|
| **A** | ≤ 15 min | Idéal — à pied, à vélo ou un tram direct |
| **B** | 16–30 min | Très bon — trajet quotidien confortable |
| **C** | 31–45 min | Acceptable — 1 h 30 de transport par jour |
| **D** | 46–60 min | Limite — seulement si le reste est exceptionnel |
| **E** | > 60 min | À écarter pour un stage de 6 mois |

**Indice de véracité** : 0–100 %, voir [ANTI-ARNAQUE.md](ANTI-ARNAQUE.md).

**Langue** : chaque annonce est étiquetée 🇩🇪 🇬🇧 🇫🇷 🇮🇹 🇨🇭 et accompagnée d'un
résumé français reconstruit depuis les données structurées, lisible sans
connaître un mot d'allemand. Voir aussi [GLOSSAIRE.md](GLOSSAIRE.md).

## Points tranchés, points ouverts

**Tranché** — campus : **Hönggerberg / HCI**. Budget : **≤ CHF 1 600** charges
comprises (`data/criteres.json`).

**Encore ouvert :**

1. Colocation acceptée, ou logement individuel exigé ?
2. Meublé indispensable ? (pour 6 mois, oui en pratique)
3. Le labo peut-il ouvrir un compte ETH / délivrer une attestation de stage ?
   — c'est la clé du Housing Office, et donc du meilleur gisement d'annonces
   saines du dossier.
