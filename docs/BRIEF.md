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

## Annonces réservées aux femmes

Une part non négligeable des colocations zurichoises ne loge que des femmes.
Ces annonces sont **retirées automatiquement** du jeu de données par
`scripts/exclusions.py`, et consignées dans `data/exclues_genre.json` pour que
le retrait reste vérifiable.

La détection sépare deux cas, et c'est délibéré :

- **exclusif** — « women only », « nur für Frauen », « female tenant only »,
  « du solltest weiblich sein », ou un « eine Mitbewohnerin » sans équivalent
  masculin nulle part dans le texte. Retiré.
- **préférence** — « preferably a woman », « Frauen bevorzugt », « ideal für
  Studentinnen ». **Conservé et signalé en orange** sur la page : les chances
  sont faibles, mais ce n'est pas à l'outil de renoncer à la place de MrA.

Le risque réel ici est le faux positif. *« Mitbewohnerin oder Mitbewohner »*,
*« mein/e Mitbewohnerin »*, *« wir sind vier Frauen und ein Mann »* décrivent
une colocation mixte, pas une restriction : chaque règle est écrite pour les
laisser passer, et le jeu de règles est vérifié contre ces cas.

## Meublé ou pas — la question qui coûte le plus cher

Pour six mois, meubler un logement vide (lit, bureau, armoire, à acheter puis à
revendre en partant) coûte plus que l'écart de loyer entre un meublé et un vide.
C'est donc un critère de premier rang, pas un détail de confort.

Deux pièges dans les données, traités par `scripts/ameublement.py` :

1. **La case « meublé » du portail est fausse une fois sur sept.** Neuf annonces
   sur soixante-huit la laissent décochée alors que le texte dit
   *« möbliertes Zimmer »*. On croise donc la case et le texte.
2. **Décochée ne veut pas dire vide**, seulement « non renseignée ». D'où un
   quatrième état assumé : **à confirmer**, qui est une question à poser, pas
   une absence de meubles.

| État | Ce que ça veut dire |
|---|---|
| **Meublé** | Le texte ou la fiche le dit |
| **Partiellement meublé** | *teilmöbliert*, ou seules les parties communes le sont |
| **Non meublé** | *unmöbliert* explicite. Si seules les parties communes sont meublées, c'est ici que l'annonce tombe : la chambre où l'on dort est vide. |
| **À confirmer** | Ni le texte ni la fiche ne le disent — ou les deux se contredisent |

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
2. Meublé indispensable, ou MrA peut-il récupérer du mobilier sur place ?
   L'outil affiche l'état pour chaque annonce, mais 20 sur 68 restent
   « à confirmer » : autant de questions à poser au premier message.
3. Le labo peut-il ouvrir un compte ETH / délivrer une attestation de stage ?
   — c'est la clé du Housing Office, et donc du meilleur gisement d'annonces
   saines du dossier.
