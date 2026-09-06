#!/usr/bin/env python3
"""Détection de la langue d'une annonce (de / en / fr / it), sans dépendance externe.
Marché zurichois : allemand (souvent suisse allemand dans les WG), anglais (labos,
expats), italien et français à la marge.
"""
import re, unicodedata

MARQUEURS = {
    "de": ["wohnung", "zimmer", "miete", "wg", "möbliert", "nachmieter", "untermiete",
           "kaution", "ab sofort", "befristet", "nebenkosten", "einzugsdatum", "sucht",
           "und", "der", "die", "das", "mit", "für", "ist", "wir", "nähe", "bad",
           "küche", "balkon", "waschmaschine", "monatlich", "besichtigung"],
    "en": ["apartment", "room", "flat", "rent", "furnished", "sublet", "deposit",
           "available", "shared", "flatmate", "the", "and", "with", "for", "is",
           "kitchen", "bathroom", "close to", "monthly", "viewing", "utilities"],
    "fr": ["appartement", "chambre", "loyer", "meublé", "colocation", "caution",
           "disponible", "charges", "cuisine", "salle de bain", "proche", "et",
           "avec", "pour", "le", "la", "les", "des", "visite", "mensuel"],
    "it": ["appartamento", "camera", "affitto", "arredato", "cauzione", "disponibile",
           "spese", "cucina", "bagno", "vicino", "con", "per", "il", "la", "di", "e"],
}
NOMS = {"de": "Allemand", "en": "Anglais", "fr": "Français", "it": "Italien",
        "gsw": "Suisse allemand", "?": "Indéterminée"}
DRAPEAUX = {"de": "🇩🇪", "en": "🇬🇧", "fr": "🇫🇷", "it": "🇮🇹", "gsw": "🇨🇭", "?": "🏳️"}

# Tournures typiquement suisses allemandes / helvétismes écrits
GSW = ["zimmerwohnung", "wohnig", "gsuecht", "znüni", "velo", "putzete", "wgzimmer",
       "morn", "gäll", "hoi", "grüezi", "mir sind", "es het"]


def _norm(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return re.sub(r"[^a-zà-ÿ\s]", " ", t)


def detecter(texte):
    t = _norm(texte)
    if not t.strip():
        return {"code": "?", "nom": NOMS["?"], "drapeau": DRAPEAUX["?"], "confiance": 0}
    scores = {}
    for code, mots in MARQUEURS.items():
        scores[code] = sum(len(re.findall(r"\b" + re.escape(_norm(m)).strip() + r"\b", t))
                           for m in mots)
    total = sum(scores.values()) or 1
    code = max(scores, key=scores.get)
    conf = round(100 * scores[code] / total)
    if scores[code] == 0:
        return {"code": "?", "nom": NOMS["?"], "drapeau": DRAPEAUX["?"], "confiance": 0}
    if code == "de" and any(g in t for g in GSW):
        code = "gsw"
    return {"code": code, "nom": NOMS[code], "drapeau": DRAPEAUX[code], "confiance": conf}


if __name__ == "__main__":
    import sys
    print(detecter(" ".join(sys.argv[1:])))
