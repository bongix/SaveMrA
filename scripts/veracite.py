#!/usr/bin/env python3
"""Indice de véracité d'une annonce (0-100 %). Grille dérivée des mises en garde
de comparis.ch, newhome.ch et du Housing Office UZH/ETH.

Principe : on part de 50 % (annonce inconnue, ni bonne ni mauvaise), on applique
des signaux pondérés, et cinq signaux « rédhibitoires » plafonnent le score à 8 %
quelle que soit la qualité du reste — ce sont les schémas d'arnaque documentés,
pas de simples doutes.
"""

# Signaux négatifs : clé -> (poids, explication FR)
DRAPEAUX_ROUGES = {
    "bailleur_a_etranger":      (-45, "Le bailleur dit être à l'étranger et ne peut pas faire visiter"),
    "cle_par_la_poste":         (-45, "Propose d'envoyer les clés par la poste avant paiement"),
    "acompte_avant_visite":     (-45, "Demande caution / 1er loyer avant toute visite"),
    "paiement_intracable":      (-50, "Western Union, crypto, cartes cadeaux, virement à l'étranger"),
    "aucune_visite_possible":   (-30, "Refuse ou esquive toute visite sur place"),
    "prix_trop_bas":            (-25, "Prix >30 % sous le marché du quartier pour cette surface"),
    "photos_suspectes":         (-25, "Photos de catalogue ou retrouvées ailleurs (recherche d'image inversée)"),
    "hors_plateforme_immediat": (-15, "Bascule tout de suite sur WhatsApp / e-mail perso"),
    "pas_adresse_precise":      (-12, "Aucune adresse ni rue, seulement « centre de Zurich »"),
    "texte_traduit_machine":    (-10, "Texte visiblement traduit automatiquement, incohérences"),
    "compte_neuf":              (-10, "Compte créé récemment, aucun historique"),
    "aucune_photo":             (-15, "Aucune photo du logement"),
    "urgence_artificielle":     (-12, "Pression : « 20 personnes intéressées, réservez aujourd'hui »"),
    "contrat_avant_visite":     (-20, "Envoie un bail à signer avant même la visite"),
}

# Signaux positifs
DRAPEAUX_VERTS = {
    "portail_verifie":          (18, "Publiée sur un portail à comptes vérifiés (Flatfox, Homegate, ImmoScout24, wohnen.ethz.ch)"),
    "regie_identifiable":       (20, "Régie / agence inscrite au registre du commerce, adresse et IDE vérifiables"),
    "visite_proposee":          (20, "Visite ou journée portes ouvertes proposée d'emblée"),
    "adresse_verifiee":         (15, "Adresse exacte donnée et cohérente avec les photos (Street View)"),
    "prix_coherent":            (10, "Prix dans la fourchette du marché pour le quartier et la surface"),
    "colocs_joignables":        (15, "Colocataires actuels joignables / profils réels"),
    "annonce_detaillee":        (8,  "Annonce détaillée : surface, étage, charges, date, règles"),
    "recommandation_reseau":    (22, "Vient du réseau ETH (labo, Housing Office, bouche-à-oreille)"),
}

REDHIBITOIRES = {"bailleur_a_etranger", "cle_par_la_poste", "acompte_avant_visite",
                 "paiement_intracable", "contrat_avant_visite"}


# Un score élevé bâti uniquement sur des métadonnées de portail ne dit qu'une
# chose : « rien de suspect dans la fiche ». Les signaux qui séparent vraiment
# une vraie annonce d'une arnaque (visite proposée, colocataires joignables,
# bailleur qui esquive) ne s'observent qu'au contact. Tant que personne n'a
# écrit au bailleur, on plafonne à 75 % — « probablement OK », jamais « fiable ».
PLAFOND_SANS_CONTACT = 75


def evaluer(annonce):
    signaux = annonce.get("signaux", [])
    contact = bool(annonce.get("signaux_manuels")) or bool(annonce.get("contact_etabli"))
    score = 50
    detail_neg, detail_pos, bloquants = [], [], []

    for s in signaux:
        if s in DRAPEAUX_ROUGES:
            poids, txt = DRAPEAUX_ROUGES[s]
            score += poids
            detail_neg.append({"cle": s, "poids": poids, "texte": txt})
            if s in REDHIBITOIRES:
                bloquants.append(txt)
        elif s in DRAPEAUX_VERTS:
            poids, txt = DRAPEAUX_VERTS[s]
            score += poids
            detail_pos.append({"cle": s, "poids": poids, "texte": txt})

    score = max(0, min(100, score))
    plafonne = False
    if not contact and score > PLAFOND_SANS_CONTACT:
        score, plafonne = PLAFOND_SANS_CONTACT, True
    if bloquants:
        score = min(score, 8)

    if score >= 80:      niveau, couleur = "fiable", "#12805c"
    elif score >= 60:    niveau, couleur = "probablement OK", "#3d7a2e"
    elif score >= 40:    niveau, couleur = "à vérifier", "#a8770f"
    elif score >= 20:    niveau, couleur = "douteux", "#b5560f"
    else:                niveau, couleur = "arnaque probable", "#a11d1d"

    non_renseigne = not signaux
    return {
        "score": score,
        "plafonne_sans_contact": plafonne,
        "contact_etabli": contact,
        "niveau": "non évaluée" if non_renseigne else niveau,
        "couleur": "#888" if non_renseigne else couleur,
        "bloquants": bloquants,
        "positifs": detail_pos,
        "negatifs": detail_neg,
        "a_verifier": [k for k in ("adresse_verifiee", "visite_proposee",
                                   "prix_coherent", "colocs_joignables")
                       if k not in signaux],
    }
