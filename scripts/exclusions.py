#!/usr/bin/env python3
"""Détection des annonces réservées à un genre.

Deux niveaux, volontairement séparés :

- **exclusif** : l'annonce dit qu'elle n'accepte que des femmes. Retirée du jeu
  de données — MrA ne peut pas y postuler.
- **préférence** : l'annonce préfère une femme sans l'exiger (« preferably »,
  « bevorzugt », « idéal pour des étudiantes »). Conservée mais signalée : les
  chances sont faibles, ce n'est pas à l'outil d'en décider à la place de MrA.

Les faux positifs sont le vrai risque ici. « Mitbewohnerin oder Mitbewohner »,
« mein/e Mitbewohnerin », « wir sind vier Frauen und ein Mann » décrivent une
colocation mixte, pas une restriction : chaque règle est écrite pour les
laisser passer.
"""
import re

# Marques d'écriture inclusive ou de formulation mixte : leur présence annule
# toute lecture restrictive d'un substantif féminin isolé.
MIXTE = re.compile(r"""
    mitbewohner(in)?\s*(oder|/|,|\bund\b)\s*(eine[nr]?\s+)?(neue[nr]?\s+)?mitbewohner
  | mitbewohner\s*(oder|/|,)\s*mitbewohnerin
  | \bmein/e\b | \beine/n\b | \bein[e]?/r\b
  | mitbewohner[:*_]innen? | kolleg[:*_]in
  | \bm/w\b | \bw/m\b | \(m/w/d\) | \bm/f\b
  | \ball\s+genders?\b | \bany\s+gender\b | \bregardless\s+of\s+gender\b
""", re.X)

EXCLUSIF = [
    (re.compile(r"\b(women|woman|females?|girls?|ladies)\s+only\b"), "« women only »"),
    (re.compile(r"\bonly\s+(for\s+)?(women|females?|girls?)\b"), "« only for women »"),
    (re.compile(r"\b(female|woman)\s+(tenant|roommate|flat\s?mate|room\s?mate|student)s?\s+only\b"),
     "« female tenant only »"),
    (re.compile(r"\bonly\s+(look(ing)?|search(ing)?)\s+for\s+(a\s+)?(female|woman)"),
     "« only looking for a female »"),
    # « looking for a friendly, easy-going, social woman » : on tolère une file
    # d'adjectifs, mais on refuse de franchir les mots qui signalent une simple
    # description du logement (« … in a flat with three women »).
    (re.compile(r"\b(look(ing)?|search(ing)?)\s+for\s+(?:an?\s+)?"
                r"(?:(?!\b(?:with|flat|room|apartment|wg|join|share[ds]?|live|living)\b)"
                r"[a-zéèà,\-\s]){0,50}?"
                r"\b(female|woman)\b"),
     "cherche explicitement une femme"),
    (re.compile(r"\bfemale\s+(roommate|flat\s?mate|room\s?mate|tenant)\s+wanted\b"),
     "« female roommate wanted »"),
    (re.compile(r"\bno\s+(men|males)\b"), "« no men »"),
    (re.compile(r"nur\s+(für\s+|an\s+)?frauen"), "« nur für Frauen »"),
    (re.compile(r"frauen\s*-?\s*wg|reine[sr]?\s+frauen"), "« Frauen-WG »"),
    (re.compile(r"nur\s+(eine\s+)?weibliche?"), "« nur weiblich »"),
    (re.compile(r"weibliche?\s+(mitbewohnerin|person|nachmieterin)\s+gesucht"),
     "cherche une colocataire femme"),
    (re.compile(r"du\s+solltest\b[^.]{0,60}\bweiblich"), "« du solltest … weiblich »"),
    (re.compile(r"solo\s+donne|riservat[oa]\s+a\s+donne"), "« solo donne »"),
    (re.compile(r"uniquement\s+(pour\s+)?(des\s+)?femmes|réservé\s+aux\s+femmes"),
     "« réservé aux femmes »"),
]

# Substantif féminin isolé : « wir suchen eine Mitbewohnerin », sans alternative
# masculine nulle part dans le texte. En allemand, c'est une restriction.
FEMININ_ISOLE = re.compile(r"\b(eine[nr]?\s+(neue[nr]?\s+)?)?(mitbewohnerin|nachmieterin|"
                           r"mitfahrerin|bewohnerin)\b(?!nen)")
MASCULIN = re.compile(r"\bmitbewohner\b|\bnachmieter\b|\bbewohner\b")

PREFERENCE = [
    (re.compile(r"\b(women|females?)\s+(are\s+)?preferred\b"), "« women preferred »"),
    (re.compile(r"preferabl[yi]\W{0,3}\)?\s*(a\s+)?(woman|female)"), "« preferably a woman »"),
    (re.compile(r"\b(a\s+)?(woman|female)\s+would\s+(be\s+)?(a\s+)?(better|nice|ideal)"),
     "préfère une femme"),
    (re.compile(r"frauen\s+bevorzugt|vorzugsweise\s+(eine\s+frau|weiblich)"),
     "« Frauen bevorzugt »"),
    (re.compile(r"ideal\s+für\s+studentinnen\b"), "« ideal für Studentinnen »"),
    (re.compile(r"hauptsächlich\s+aus\s+frauen|überwiegend\s+frauen"),
     "colocation majoritairement féminine"),
]


def _texte(a):
    return ((a.get("titre") or "") + " \n " + (a.get("description") or "")).lower()


def analyser(a):
    """→ {'niveau': 'exclusif'|'preference'|None, 'motifs': [...]}"""
    t = _texte(a)
    mixte = bool(MIXTE.search(t))

    motifs = [libelle for rx, libelle in EXCLUSIF if rx.search(t)]
    if not motifs and not mixte and FEMININ_ISOLE.search(t) and not MASCULIN.search(t):
        motifs.append("cherche « eine Mitbewohnerin », sans équivalent masculin")
    if motifs:
        return {"niveau": "exclusif", "motifs": motifs}

    motifs = [libelle for rx, libelle in PREFERENCE if rx.search(t)]
    if motifs:
        return {"niveau": "preference", "motifs": motifs}
    return {"niveau": None, "motifs": []}
