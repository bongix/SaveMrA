#!/usr/bin/env python3
"""Temps de trajet réel domicile -> campus ETH via l'API publique transport.opendata.ch
(données CFF/ZVV, horaires réels, pas d'estimation à vol d'oiseau, pas de clé API).

Usage:
    python3 scripts/commute.py "Zürich, Oerlikon"
    python3 scripts/commute.py --toutes    # recalcule toutes les annonces
"""
import json, sys, time, urllib.parse, urllib.request, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
CACHE_F = RACINE / "data" / "cache_trajets.json"
API = "https://transport.opendata.ch/v1"

# Mardi ordinaire, arrivée au labo pour 09:00 -> le pire cas réaliste du quotidien.
JOUR_REF = "2026-09-08"
HEURE_REF = "09:00"


def _charger_cache():
    if CACHE_F.exists():
        return json.loads(CACHE_F.read_text())
    return {}


def _sauver_cache(c):
    CACHE_F.write_text(json.dumps(c, ensure_ascii=False, indent=2))


# transport.opendata.ch est gratuit mais throttlé : on s'auto-limite au lieu
# de se faire jeter en 429 au milieu d'un lot.
_INTERVALLE_MIN = 0.8
_dernier_appel = [0.0]


def _get(chemin, params):
    url = f"{API}/{chemin}?" + urllib.parse.urlencode(params, doseq=True)
    for tentative in range(6):
        attente = _INTERVALLE_MIN - (time.time() - _dernier_appel[0])
        if attente > 0:
            time.sleep(attente)
        _dernier_appel[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SaveMrA/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and tentative < 5:
                time.sleep(5 * (tentative + 1))
                continue
            if tentative == 5:
                raise
            time.sleep(2 * (tentative + 1))
        except Exception:
            if tentative == 5:
                raise
            time.sleep(2 * (tentative + 1))


def _duree_en_min(txt):
    # format "00d00:19:00"
    jours, reste = txt.split("d")
    h, m, s = reste.split(":")
    return int(jours) * 1440 + int(h) * 60 + int(m)


def trajet(depart, arrivee, cache=None, force=False):
    """Retourne {minutes, changements, resume} pour un trajet arrivant à HEURE_REF."""
    cle = f"{depart}||{arrivee}"
    cache = _charger_cache() if cache is None else cache
    if not force and cle in cache:
        return cache[cle]

    d = _get("connections", {
        "from": depart, "to": arrivee, "date": JOUR_REF, "time": HEURE_REF,
        "isArrivalTime": 1, "limit": 4,
    })
    cx = d.get("connections") or []
    if not cx:
        res = {"minutes": None, "changements": None, "resume": "aucune liaison trouvée",
               "erreur": "introuvable"}
    else:
        meilleure = min(cx, key=lambda c: _duree_en_min(c["duration"]))
        lignes = [s["journey"]["category"] + " " + str(s["journey"].get("number") or "")
                  for s in meilleure["sections"] if s.get("journey")]
        res = {
            "minutes": _duree_en_min(meilleure["duration"]),
            "changements": meilleure.get("transfers"),
            "resume": " → ".join(l.strip() for l in lignes) or "à pied",
            "depuis": meilleure["from"]["station"]["name"],
            "vers": meilleure["to"]["station"]["name"],
        }
    cache[cle] = res
    _sauver_cache(cache)
    return res


def tranche(minutes, tranches):
    if minutes is None:
        return {"code": "?", "label": "inconnu", "couleur": "#888", "verdict": "trajet non calculé"}
    for t in tranches:
        if minutes <= t["max_min"]:
            return t
    return tranches[-1]



def arret_le_plus_proche(lat, lon, cache=None):
    """Arrêt CFF/ZVV le plus proche d'un point + distance en mètres."""
    cle = f"stop@{round(lat,4)},{round(lon,4)}"
    cache = _charger_cache() if cache is None else cache
    if cle in cache:
        return cache[cle]
    d = _get("locations", {"x": lat, "y": lon, "type": "station"})
    stations = [s for s in d.get("stations", []) if s.get("id")]
    res = {"nom": None, "distance_m": None}
    if stations:
        s0 = min(stations, key=lambda s: s.get("distance") or 9e9)
        res = {"nom": s0["name"], "distance_m": round(s0.get("distance") or 0)}
    cache[cle] = res
    _sauver_cache(cache)
    return res


def minutes_a_pied(metres):
    """~80 m/min = 4.8 km/h, le pas d'un piéton pressé un matin de semaine."""
    if not metres:
        return 0
    return max(1, round(metres / 80))


def enrichir(annonce, campus, tranches, cache):
    """Ajoute annonce['trajet'] : temps porte-à-porte vers les deux campus ETH.

    Porte-à-porte = marche jusqu'à l'arrêt le plus proche + liaison ZVV/CFF
    réelle (arrivée 09:00 un mardi) + marche finale déjà comprise dans la
    liaison quand l'arrêt d'arrivée est celui du campus.
    """
    marche = 0
    origine = None
    if annonce.get("lat") and annonce.get("lon"):
        a = arret_le_plus_proche(annonce["lat"], annonce["lon"], cache=cache)
        origine = a["nom"]
        marche = minutes_a_pied(a["distance_m"])
        annonce["arret_proche"] = origine
        annonce["marche_min"] = marche
    if not origine:
        origine = annonce.get("arret_proche") or annonce.get("adresse") or annonce.get("quartier")
    if not origine:
        return annonce
    if "zürich" not in origine.lower() and "," not in origine:
        origine = f"Zürich, {origine}"

    res = {}
    for cle, c in campus["campus"].items():
        r = dict(trajet(origine, c["arret"], cache=cache))
        if r.get("minutes") is not None:
            r["minutes_transit"] = r["minutes"]
            r["minutes"] = r["minutes"] + marche
        res[cle] = r
    principal = campus["campus_principal"]
    mins = res[principal]["minutes"]
    t = tranche(mins, tranches["tranches"])
    res["origine_utilisee"] = origine
    res["marche_initiale_min"] = marche
    res["campus_reference"] = principal
    res["minutes"] = mins
    res["minutes_autre_campus"] = res["hoenggerberg" if principal == "zentrum" else "zentrum"]["minutes"]
    res["tranche"] = t["code"]
    res["tranche_label"] = t["label"]
    res["tranche_couleur"] = t["couleur"]
    annonce["trajet"] = res
    return annonce


if __name__ == "__main__":
    campus = json.loads((RACINE / "data" / "campus.json").read_text())
    tr = json.loads((RACINE / "data" / "tranches.json").read_text())
    if len(sys.argv) > 1 and sys.argv[1] != "--toutes":
        origine = " ".join(sys.argv[1:])
        for cle, c in campus["campus"].items():
            r = trajet(origine, c["arret"])
            print(f"{c['nom']:35s} {str(r['minutes']):>4s} min  ({r['changements']} chgt)  {r['resume']}")
    else:
        f = RACINE / "data" / "annonces.json"
        data = json.loads(f.read_text())
        cache = _charger_cache()
        for a in data["annonces"]:
            enrichir(a, campus, tr, cache)
            m = a.get("trajet", {}).get("minutes")
            print(f"[{a.get('trajet',{}).get('tranche','?')}] {str(m):>4} min  {a['titre'][:60]}")
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2))
