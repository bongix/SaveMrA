#!/usr/bin/env python3
"""Pipeline SaveMrA : collecte → trajet → langue → véracité → résumé FR.

    python3 scripts/pipeline.py            # tout : collecte + enrichissement
    python3 scripts/pipeline.py --local    # ré-enrichit annonces.json sans recollecter
"""
import json, sys, pathlib, statistics, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import commute, veracite, langue, exclusions

RACINE = pathlib.Path(__file__).resolve().parent.parent
F_ANNONCES = RACINE / "data" / "annonces.json"

# Séjour de MrA : stage à l'ETH, arrivée octobre 2026, départ fin mars 2027.
SEJOUR_DEBUT = datetime.date(2026, 10, 1)
SEJOUR_FIN = datetime.date(2027, 3, 31)

TYPE_FR = {"SHARED": "Colocation (chambre en WG)", "ROOM": "Chambre",
           "APARTMENT": "Appartement", "STUDIO": "Studio"}


def _nombre(v):
    """Flatfox renvoie tantôt des nombres, tantôt des chaînes."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def disponibilite(a):
    """Compatibilité avec la fenêtre octobre 2026 → mars 2027.

    On ne connaît que la date d'entrée côté portail : une entrée trop tardive
    ampute le séjour, une entrée très en avance oblige à payer à vide.
    """
    brut = (a.get("date_emmenagement") or "").strip()
    if not brut or brut.lower() in ("immediately", "sofort", "par accord", "on request"):
        return {"code": "immediat", "label": "Dispo. immédiate", "ok": True,
                "detail": "Entrée possible tout de suite — compatible avec une arrivée en octobre."}
    try:
        d = datetime.date.fromisoformat(brut[:10])
    except ValueError:
        return {"code": "inconnu", "label": "Date à confirmer", "ok": None,
                "detail": f"Date d'entrée non exploitable ({brut}) — à demander au bailleur."}
    if d <= SEJOUR_DEBUT:
        marge = (SEJOUR_DEBUT - d).days
        if marge > 45:
            return {"code": "trop_tot", "label": f"Libre dès le {d:%d/%m/%Y}", "ok": True,
                    "detail": f"Libre {marge} jours avant l'arrivée : loyer à vide, à négocier."}
        return {"code": "ideal", "label": f"Libre dès le {d:%d/%m/%Y}", "ok": True,
                "detail": "Entrée alignée sur le début du stage."}
    perdu = (d - SEJOUR_DEBUT).days
    if d <= SEJOUR_FIN:
        return {"code": "tardif", "label": f"Libre dès le {d:%d/%m/%Y}", "ok": False,
                "detail": f"{perdu} jours de stage sans logement — solution d'attente nécessaire."}
    return {"code": "hors_periode", "label": f"Libre dès le {d:%d/%m/%Y}", "ok": False,
            "detail": "Disponible après la fin du stage — hors sujet."}


def signaux_automatiques(a, reference):
    """Signaux déductibles des données structurées. Les signaux humains
    (visite proposée, bailleur à l'étranger…) s'ajoutent à la main après contact.

    `reference` = médiane CHF/m² de la catégorie, sauf pour les colocations où
    c'est la médiane du loyer mensuel."""
    # On repart de zéro : réutiliser a["signaux"] ferait survivre les verdicts
    # d'une passe précédente, y compris ceux qu'un changement de règle infirme.
    s = set(a.get("signaux_manuels", []))
    s.add("portail_verifie")                       # Flatfox : comptes régie vérifiés
    if a.get("regie"):
        s.add("regie_identifiable")
    if not a.get("photos"):
        s.add("aucune_photo")
    if a.get("adresse") and not a["adresse"][0].isdigit():
        s.add("adresse_verifiee")
    else:
        s.add("pas_adresse_precise")
    desc = a.get("description") or ""
    if len(desc) > 350 and a.get("surface_m2") and a.get("pieces"):
        s.add("annonce_detaillee")
    # Référence de prix : au m² pour un logement entier, au loyer absolu pour une
    # chambre en WG — là, la surface publiée est trop souvent celle de tout
    # l'appartement, et un CHF/m² calculé dessus n'a aucun sens.
    prix, surf = _nombre(a.get("prix_chf")), _nombre(a.get("surface_m2"))
    ref = None
    if a.get("type") == "SHARED":
        if prix and reference:
            ref = prix / reference
    elif prix and surf and reference:
        ref = (prix / surf) / reference
    if ref is not None:
        if ref < 0.60:
            s.add("prix_trop_bas")
        elif 0.75 <= ref <= 1.5:
            s.add("prix_coherent")
    return sorted(s)


def tranche_prix(prix, tranches):
    if not prix:
        return {"code": "P?", "label": "prix non indiqué"}
    for t in tranches:
        if prix <= t["max_chf"]:
            return {"code": t["code"], "label": t["label"]}
    return {"code": "P+", "label": "au-dessus du budget"}


def resume_fr(a):
    """Résumé français reconstruit depuis les données structurées : lisible
    quelle que soit la langue de l'annonce d'origine."""
    p = []
    p.append(TYPE_FR.get(a.get("type"), a.get("type") or "Logement"))
    surf = _nombre(a.get("surface_m2"))
    if surf:
        # Pour une chambre en WG, le portail publie la surface du logement entier.
        p.append(f"logement {int(surf)} m²" if a.get("type") == "SHARED" and surf > 40
                 else f"{int(surf)} m²")
    pi = _nombre(a.get("pieces"))
    if pi:
        p.append(f"{pi:g} pièce" + ("s" if pi > 1 else ""))
    prix = _nombre(a.get("prix_chf"))
    if prix:
        p.append(f"CHF {int(prix):,}/mois".replace(",", "'") +
                 (" charges comprises" if a.get("charges_incluses") else " hors charges"))
    if a.get("meuble"):
        p.append("meublé")
    if a.get("temporaire"):
        p.append("location temporaire")
    if a.get("date_emmenagement"):
        p.append(f"dispo. {a['date_emmenagement']}")
    t = a.get("trajet") or {}
    if t.get("minutes"):
        p.append(f"{t['minutes']} min du campus ({t.get('tranche_label')})")
    return " · ".join(p)


def main(local=False):
    campus = json.loads((RACINE / "data" / "campus.json").read_text())
    tranches = json.loads((RACINE / "data" / "tranches.json").read_text())
    criteres = json.loads((RACINE / "data" / "criteres.json").read_text())
    plafond = criteres["loyer_max_chf"]

    if local and F_ANNONCES.exists():
        base = json.loads(F_ANNONCES.read_text())["annonces"]
    else:
        import collecte_flatfox
        base = collecte_flatfox.collecter(21)
        if F_ANNONCES.exists():
            anciennes = {a["id"]: a for a in json.loads(F_ANNONCES.read_text())["annonces"]}
            for a in base:                          # on conserve les annotations manuelles
                if a["id"] in anciennes:
                    for champ in ("signaux_manuels", "notes", "statut", "description_fr"):
                        if champ in anciennes[a["id"]]:
                            a[champ] = anciennes[a["id"]][champ]
            for id_, a in anciennes.items():        # et les annonces saisies à la main
                if a.get("source") != "Flatfox" and id_ not in {b["id"] for b in base}:
                    base.append(a)

    # Annonces réservées aux femmes : retirées, mais consignées dans
    # data/exclues_genre.json pour que la décision reste vérifiable.
    retirees = []
    gardees = []
    for a in base:
        r = exclusions.analyser(a)
        a["genre"] = r
        (retirees if r["niveau"] == "exclusif" else gardees).append(a)
    # Registre cumulé : une annonce retirée à une passe précédente n'est plus
    # dans le jeu de données, donc un compteur « de cette passe » retomberait à
    # zéro dès le passage suivant et la page mentirait.
    f_log = RACINE / "data" / "exclues_genre.json"
    registre = {}
    if f_log.exists():
        registre = {x["id"]: x for x in json.loads(f_log.read_text())}
    for a in retirees:
        registre[a["id"]] = {"id": a["id"], "titre": a["titre"], "url": a.get("url"),
                             "prix_chf": a.get("prix_chf"), "motifs": a["genre"]["motifs"]}
    if registre:
        f_log.write_text(json.dumps(list(registre.values()), ensure_ascii=False, indent=2))
    if retirees:
        print(f"  {len(retirees)} annonces réservées aux femmes retirées à cette passe "
              f"({len(registre)} au total, détail : data/exclues_genre.json)", file=sys.stderr)
    base = gardees

    avant = len(base)
    base = [a for a in base if not (_nombre(a.get("prix_chf")) or 0) > plafond]
    if avant != len(base):
        print(f"  {avant - len(base)} annonces au-dessus de CHF {plafond} écartées", file=sys.stderr)

    # En colocation, Flatfox publie la surface du LOGEMENT, pas celle de la
    # chambre : mélanger les deux dans une seule médiane fait passer toutes les
    # WG pour des affaires en or et déclenche à tort « prix trop bas ».
    par_cat = {}
    for a in base:
        prix, surf = _nombre(a.get("prix_chf")), _nombre(a.get("surface_m2"))
        if a.get("type") == "SHARED":
            if prix:
                par_cat.setdefault("SHARED", []).append(prix)          # loyer mensuel
        elif prix and surf:
            par_cat.setdefault(a.get("type"), []).append(prix / surf)  # CHF/m²
    medianes = {c: statistics.median(v) for c, v in par_cat.items() if len(v) >= 5}
    m2 = [r for c, v in par_cat.items() if c != "SHARED" for r in v]
    mediane_m2 = statistics.median(m2) if m2 else None

    cache = commute._charger_cache()
    for i, a in enumerate(base, 1):
        commute.enrichir(a, campus, tranches, cache)
        a["langue"] = langue.detecter((a.get("titre") or "") + " " + (a.get("description") or ""))
        a["signaux"] = sorted(set(signaux_automatiques(a, medianes.get(a.get("type")))) |
                              set(a.get("signaux_manuels", [])))
        a["veracite"] = veracite.evaluer(a)
        a["dispo"] = disponibilite(a)
        a["tranche_prix"] = tranche_prix(_nombre(a.get("prix_chf")), criteres["tranches_prix"])
        a["resume_fr"] = resume_fr(a)
        if i % 20 == 0:
            print(f"  {i}/{len(base)}…", file=sys.stderr)

    base.sort(key=lambda a: (a.get("trajet", {}).get("minutes") or 999,
                             -(a.get("veracite", {}).get("score") or 0)))

    F_ANNONCES.write_text(json.dumps({
        "genere_le": datetime.datetime.now().isoformat(timespec="seconds"),
        "campus_reference": campus["campus_principal"],
        "sejour": {"debut": SEJOUR_DEBUT.isoformat(), "fin": SEJOUR_FIN.isoformat(),
                   "duree_mois": 6, "libelle": "octobre 2026 → mars 2027"},
        "mediane_chf_par_m2": round(mediane_m2, 1) if mediane_m2 else None,
        "loyer_max_chf": plafond,
        "retirees_genre": len(registre),
        "tranches_prix": criteres["tranches_prix"],
        "medianes_par_type": {c: round(v, 1) for c, v in medianes.items()},
        "_unite_medianes": "CHF/m² sauf SHARED = loyer mensuel médian",
        "annonces": base,
    }, ensure_ascii=False, indent=2))
    print(f"{len(base)} annonces enrichies → {F_ANNONCES}")


if __name__ == "__main__":
    main(local="--local" in sys.argv)
