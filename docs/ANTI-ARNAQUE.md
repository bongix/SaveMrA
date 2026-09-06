# Indice de véracité — comment il est calculé

Zurich est un marché tendu, donc un terrain d'arnaque rentable. Le schéma
dominant est toujours le même : **faire payer avant la visite.**

Le score part de **50 %** (annonce inconnue, ni bonne ni mauvaise), applique des
signaux pondérés, et se borne à 0–100. Il ne remplace pas le jugement : il dit
*où regarder*, pas *quoi croire*.

## Cinq signaux rédhibitoires — plafonnent le score à 8 %

Ce ne sont pas des doutes, ce sont les scénarios d'escroquerie documentés par
comparis.ch et newhome.ch. Un seul suffit à disqualifier l'annonce.

| Signal | Le script | Poids |
|---|---|---|
| `bailleur_a_etranger` | « Je suis à Londres / au Nigeria / en mission » — donc pas de visite | −45 |
| `cle_par_la_poste` | « Je vous envoie les clés, vous visitez, on vous rembourse si ça ne va pas » — la clé n'arrive jamais | −45 |
| `acompte_avant_visite` | Caution ou premier loyer exigé avant d'avoir vu le logement | −45 |
| `contrat_avant_visite` | Un bail à signer avant la visite, pour donner l'air sérieux | −20 |
| `paiement_intracable` | Western Union, crypto, cartes cadeaux, virement hors CH | −50 |

**Règle absolue pour MrA : aucun franc ne part avant d'avoir vu le logement en
personne (ou par un tiers de confiance sur place) et signé un bail dont le
bailleur est vérifiable.**

## Signaux négatifs pondérés

| Signal | Poids | Lecture |
|---|---|---|
| `aucune_visite_possible` | −30 | Esquive systématique |
| `prix_trop_bas` | −25 | >30 % sous le marché du quartier à surface égale. Calculé automatiquement contre la médiane CHF/m² du lot collecté. |
| `photos_suspectes` | −25 | Photos de catalogue, ou retrouvées ailleurs par recherche d'image inversée |
| `contrat_avant_visite` | −20 | (aussi rédhibitoire) |
| `hors_plateforme_immediat` | −15 | Bascule immédiate sur WhatsApp / e-mail perso |
| `aucune_photo` | −15 | Détecté automatiquement |
| `urgence_artificielle` | −12 | « 20 personnes intéressées, réservez aujourd'hui » |
| `pas_adresse_precise` | −12 | « Centre de Zurich », sans rue. Détecté automatiquement. |
| `texte_traduit_machine` | −10 | Incohérences de traduction automatique |
| `compte_neuf` | −10 | Profil créé récemment, aucun historique |

## Signaux positifs

| Signal | Poids | Lecture |
|---|---|---|
| `recommandation_reseau` | +22 | Vient du labo, du Housing Office, du bouche-à-oreille ETH |
| `regie_identifiable` | +20 | Régie inscrite au registre du commerce, IDE et adresse vérifiables. Détecté automatiquement quand le portail expose l'agence. |
| `visite_proposee` | +20 | Visite ou journée portes ouvertes proposée d'emblée |
| `portail_verifie` | +18 | Flatfox, Homegate, ImmoScout24, wohnen.ethz.ch |
| `adresse_verifiee` | +15 | Adresse exacte, cohérente avec les photos sur Street View. Détecté automatiquement. |
| `colocs_joignables` | +15 | Colocataires actuels joignables, profils réels |
| `prix_coherent` | +10 | Dans la fourchette du marché. Calculé automatiquement. |
| `annonce_detaillee` | +8 | Surface, étage, charges, date, règles de la coloc |

## Lecture du score

| Score | Niveau | Conduite à tenir |
|---|---|---|
| 80–100 | **fiable** | Postuler vite |
| 60–79 | **probablement OK** | Postuler, vérifier à la visite |
| 40–59 | **à vérifier** | Poser les questions de contrôle avant de se déplacer |
| 20–39 | **douteux** | Ne pas s'engager sans preuve d'identité du bailleur |
| 0–19 | **arnaque probable** | Ignorer, et signaler à la plateforme |

## Signaux automatiques vs. manuels

Le pipeline pose seul ce qu'il peut lire dans les données : `portail_verifie`,
`regie_identifiable`, `aucune_photo`, `adresse_verifiee` / `pas_adresse_precise`,
`annonce_detaillee`, `prix_trop_bas` / `prix_coherent`.

Tout le reste se constate **au contact**. On l'ajoute à la main dans
`data/annonces.json`, champ `signaux_manuels` — le pipeline le conserve d'une
collecte à l'autre :

```json
{ "id": "flatfox-51159", "signaux_manuels": ["visite_proposee", "colocs_joignables"] }
```

## Les six questions de contrôle à envoyer au bailleur

1. Quand puis-je visiter ? *(Toute réponse évasive = fin de l'échange.)*
2. Quelle est l'adresse exacte, numéro et étage compris ?
3. Êtes-vous le propriétaire ou la régie ? Quel est le nom inscrit au bail ?
4. Le bail est-il un contrat suisse standard, avec caution sur un **compte de
   garantie bloqué au nom du locataire** ? *(C'est la loi : art. 257e CO. Une
   caution versée sur un compte privé est un signal d'alarme.)*
5. La sous-location est-elle autorisée par le propriétaire, par écrit ?
   *(Indispensable pour toute chambre WOKO/Juwo.)*
6. Puis-je parler aux colocataires actuels ?

## Vérifications à faire soi-même

- **Recherche d'image inversée** sur 2–3 photos (Google Images, TinEye) : une
  photo qui apparaît sur une annonce à Berlin est volée.
- **Street View** sur l'adresse annoncée : le bâtiment correspond-il aux photos ?
- **Nom de la régie** dans le registre du commerce zurichois
  ([zefix.ch](https://www.zefix.ch)).
- **Recherche du texte de l'annonce** entre guillemets : les arnaqueurs
  recyclent le même texte sur plusieurs villes.
