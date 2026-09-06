#!/usr/bin/env python3
"""Collecte Flatfox → annonces normalisées SaveMrA.

L'API publique /api/v1/public-listing/ ignore tous les filtres serveur : elle
renvoie le catalogue suisse entier trié par pk croissant (donc chronologique).
On remonte donc les dernières pages et on filtre côté client sur Zurich.

Usage: python3 scripts/collecte_flatfox.py [jours]     (défaut 21)
"""
import json, sys, pathlib, urllib.request, datetime, time

RACINE = pathlib.Path(__file__).resolve().parent.parent
API = "https://flatfox.ch/api/v1/public-listing/"
PAGE = 500
NPA_ZH = tuple(str(n) for n in range(8000, 8065))          # ville de Zurich
NPA_AGGLO = ("8046","8048","8050","8051","8052","8055","8057","8064","8600","8802",
             "8803","8810","8038","8032","8044","8047","8049","8053","8003","8005",
             "8006","8008","8037","8004","8002","8001","8092","8093","8305","8404",
             "8700","8702","8706","8712","8902","8952","8953","8957","8105","8107",
             "8117","8152","8302","8304","8600","8602","8604","8606","8623","8134")
CATS = {"SHARED", "ROOM", "APARTMENT", "STUDIO"}
LOYER_MAX = json.loads((RACINE / "data" / "criteres.json").read_text())["loyer_max_chf"]


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SaveMrA/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def collecter(jours=21, loyer_max=LOYER_MAX):
    total = _get(f"{API}?limit=1")["count"]
    limite = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=jours)
    # Les pk ne sont pas strictement chronologiques : une page peut contenir
    # quelques vieilles annonces au milieu de récentes. S'arrêter à la première
    # ancienne tronquait la moisson de façon imprévisible (145 annonces une
    # fois, 67 la suivante). On ne s'arrête qu'après PAGES_VIDES pages
    # consécutives sans une seule annonce dans la fenêtre.
    PAGES_VIDES = 3
    offset = max(0, total - PAGE)
    brut, vides = [], 0
    while offset >= 0 and vides < PAGES_VIDES:
        page = _get(f"{API}?limit={PAGE}&offset={offset}")["results"]
        recentes = 0
        for r in page:
            pub = r.get("published") or r.get("created")
            if not pub:
                continue
            if datetime.datetime.fromisoformat(pub) >= limite:
                brut.append(r)
                recentes += 1
        vides = 0 if recentes else vides + 1
        print(f"  offset {offset:>6}  +{recentes:>3} → {len(brut)} annonces dans la fenêtre",
              file=sys.stderr)
        if offset == 0:
            break
        offset = max(0, offset - PAGE)
        time.sleep(0.4)

    out = []
    for r in brut:
        npa = str(r.get("zipcode") or "")
        if not (npa in NPA_ZH or npa in NPA_AGGLO):
            continue
        if r.get("object_category") not in CATS:
            continue
        prix = r.get("price_display") or r.get("rent_gross") or r.get("rent_net")
        if prix and prix > loyer_max:
            continue
        rue = (r.get("street") or "").strip()
        ville = (r.get("city") or "").strip()
        out.append({
            "id": f"flatfox-{r['pk']}",
            "source": "Flatfox",
            "url": "https://flatfox.ch" + (r.get("url") or ""),
            "titre": r.get("public_title") or r.get("short_title") or "(sans titre)",
            "description": (r.get("description") or "")[:2500],
            "prix_chf": prix,
            "charges_incluses": r.get("price_display_type") == "TOTAL",
            "pieces": r.get("number_of_rooms"),
            "surface_m2": r.get("surface_living") or r.get("livingspace"),
            "meuble": bool(r.get("is_furnished")),
            "temporaire": bool(r.get("is_temporary")),
            "type": r.get("object_category"),
            "adresse": f"{rue}, {npa} {ville}".strip(", ") if rue else f"{npa} {ville}",
            "quartier": f"{npa} {ville}",
            "arret_proche": None,
            "lat": r.get("latitude"), "lon": r.get("longitude"),
            "date_emmenagement": r.get("moving_date"),
            "publiee_le": (r.get("published") or "")[:10],
            "photos": len(r.get("images") or []),
            "regie": (r.get("agency") or {}).get("name") if isinstance(r.get("agency"), dict) else None,
            "signaux": [],
        })
    return out


if __name__ == "__main__":
    jours = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    res = collecter(jours)
    f = RACINE / "data" / "collecte_flatfox.json"
    f.write_text(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"{len(res)} annonces Zurich retenues → {f}")
