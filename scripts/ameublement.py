#!/usr/bin/env python3
"""État d'ameublement d'une annonce, en quatre états explicites.

Le booléen `is_furnished` de Flatfox n'est pas fiable : il est faux sur
9 annonces sur 68 dont le texte dit pourtant « möbliertes Zimmer ». Et surtout,
`False` ne veut pas dire « non meublé » — il veut dire « le bailleur n'a pas
coché la case ». Pour un séjour de six mois, la différence coûte cher : un
logement vide, c'est un mobilier à acheter puis à revendre en partant.

On croise donc le drapeau et le texte, et on assume un quatrième état :
« à confirmer », qui est une question à poser, pas une absence de meubles.
"""
import re

NON_MEUBLE = re.compile(
    r"\bunmöbliert|nicht\s+möbliert|ohne\s+möbel|leer\s+(übergeben|übernommen)"
    r"|\bunfurnished|not\s+furnished|without\s+furniture"
    r"|non\s+meublé|sans\s+meubles?|\bvuoto\b|non\s+arredato")

PARTIEL = re.compile(
    r"teil(weise\s+)?möbliert|teilmöbliert|halb\s?möbliert"
    r"|part(ly|ially)\s+furnished|semi[-\s]?furnished"
    r"|(gemeinschaftsräume|gemeinschaftsbereiche|common\s+(areas?|rooms?))"
    r"[^.]{0,40}(sind\s+)?(möbliert|furnished)"
    r"|partiellement\s+meublé")

MEUBLE = re.compile(
    r"\bvoll(ständig\s+)?möbliert|\bmöbliert|möblierte[sr]?\s|komplett\s+eingerichtet"
    r"|vollständig\s+eingerichtet|\bfurnished\b|fully\s+furnished"
    r"|\bmeublé|\barredato")

ETATS = {
    "meuble":      {"label": "Meublé",         "couleur": "#12805C", "sur": True},
    "partiel":     {"label": "Partiellement meublé", "couleur": "#A8770F", "sur": True},
    "non_meuble":  {"label": "Non meublé",     "couleur": "#B5560F", "sur": True},
    "a_confirmer": {"label": "Ameublement à confirmer", "couleur": "#5A6360", "sur": False},
}


def evaluer(annonce):
    t = ((annonce.get("titre") or "") + " \n " + (annonce.get("description") or "")).lower()
    drapeau = bool(annonce.get("meuble"))

    # L'ordre compte à deux titres. « unmöbliert » contient « möbliert », donc
    # le négatif passe avant le positif. Et une annonce qui dit « la chambre est
    # vide, les parties communes sont meublées » est un logement vide pour qui
    # doit y dormir : l'état de la chambre prime sur celui du salon.
    communs_meubles = bool(PARTIEL.search(t))
    if NON_MEUBLE.search(t):
        code, source = "non_meuble", "texte de l'annonce"
    elif communs_meubles:
        code, source = "partiel", "texte de l'annonce"
    elif MEUBLE.search(t):
        code, source = "meuble", "texte de l'annonce"
    elif drapeau:
        code, source = "meuble", "case cochée par le bailleur"
    else:
        code, source = "a_confirmer", "ni le texte ni la fiche ne le disent"

    note = None
    if code == "non_meuble" and communs_meubles:
        note = ("La chambre est vide ; seules les parties communes sont meublées. "
                "Compter un lit, un bureau et une armoire à acheter puis à revendre.")
    if drapeau and code in ("non_meuble", "partiel"):
        code, source = "a_confirmer", "contradiction"
        note = ("Le portail annonce « meublé », le texte dit le contraire. "
                "À faire préciser avant toute visite.")
    elif code == "a_confirmer":
        note = ("Rien dans l'annonce ne le dit. Pour six mois, meubler un logement vide "
                "coûte plus cher que l'écart de loyer : question à poser au premier message.")

    e = ETATS[code]
    return {"code": code, "label": e["label"], "couleur": e["couleur"],
            "sur": e["sur"], "source": source, "note": note}
