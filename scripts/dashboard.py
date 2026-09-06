#!/usr/bin/env python3
"""Génère le tableau de bord SaveMrA (web/index.html).

Le fichier produit est autonome : pas de CDN, pas de fetch. Il s'ouvre tel quel
dans un navigateur et se publie tel quel comme Artifact.
"""
import json, html, pathlib, datetime, collections, string

RACINE = pathlib.Path(__file__).resolve().parent.parent
# À la racine du dépôt : c'est ce que GitHub Pages sert comme page d'accueil.
SORTIE = RACINE / "index.html"

TYPE_FR = {"SHARED": "Colocation", "ROOM": "Chambre", "APARTMENT": "Appartement",
           "STUDIO": "Studio"}


def e(x):
    return html.escape(str(x if x is not None else ""))


def carte(a):
    t = a.get("trajet") or {}
    v = a.get("veracite") or {}
    lg = a.get("langue") or {}
    d = a.get("dispo") or {}
    mins = t.get("minutes")
    autre = t.get("minutes_autre_campus")
    score = v.get("score")
    prix = a.get("prix_chf")
    alerte = v.get("bloquants") or []

    am = a.get("ameublement") or {}
    puces = []
    if a.get("temporaire"):
        puces.append("temporaire")
    if a.get("charges_incluses"):
        puces.append("charges comprises")
    if a.get("surface_m2"):
        sm = int(float(a["surface_m2"]))
        puces.append(f"logement {sm} m²" if a.get("type") == "SHARED" and sm > 40 else f"{sm} m²")

    motifs_pos = "".join(f"<li>{e(p['texte'])}</li>" for p in (v.get("positifs") or []))
    motifs_neg = "".join(f"<li>{e(p['texte'])}</li>" for p in (v.get("negatifs") or []))

    return f"""
<article class="fiche{' fiche--alerte' if alerte else ''}"
         data-bande="{e(t.get('tranche','?'))}"
         data-verac="{score if score is not None else 0}"
         data-langue="{e(lg.get('code','?'))}"
         data-type="{e(a.get('type',''))}"
         data-prix="{prix or 0}"
         data-tprix="{e((a.get('tranche_prix') or {}).get('code','P?'))}"
         data-dispo="{e(d.get('code','inconnu'))}"
         data-meuble="{e(am.get('code','a_confirmer'))}">
  <div class="fiche__minutes" style="--bande:{e(t.get('tranche_couleur','#888'))}">
    <b>{e(mins) if mins is not None else '—'}</b><span>min</span>
  </div>
  <div class="fiche__corps">
    <h3><a href="{e(a.get('url'))}" target="_blank" rel="noopener">{e(a.get('titre'))}</a></h3>
    <p class="resume">{e(a.get('resume_fr'))}</p>
    <p class="lieu">{' · '.join(x for x in [
        e(a.get('adresse')),
        f"arrêt <b>{e(a.get('arret_proche'))}</b> ({e(a.get('marche_min', 0))} min à pied)"
            if a.get('arret_proche') else '',
        e(t.get('resume', '')),
        f"ETH Zentrum {e(autre)} min" if autre is not None else '',
    ] if x)}</p>
    <ul class="puces">
      <li class="puce-meuble{'' if am.get('sur') else ' puce-meuble--flou'}"
          style="--c:{e(am.get('couleur', '#888'))}"
          title="{e(am.get('source', ''))}">{e(am.get('label', 'ameublement inconnu'))}</li>
      {''.join(f'<li>{e(p)}</li>' for p in puces)}
    </ul>
    {'<p class="ameub">' + e(am['note']) + '</p>' if am.get('note') else ''}
    <p class="dispo dispo--{e(d.get('code','inconnu'))}">{e(d.get('label'))} — {e(d.get('detail'))}</p>
    {'<p class="alerte">⚠ ' + ' · '.join(e(x) for x in alerte) + '</p>' if alerte else ''}
    {'<p class="genre">Préférence féminine annoncée — ' + ' · '.join(e(m) for m in (a.get('genre') or {}).get('motifs', [])) + '. Candidature possible, mais les chances sont faibles.</p>' if (a.get('genre') or {}).get('niveau') == 'preference' else ''}
    <details class="pourquoi">
      <summary>Pourquoi ce score</summary>
      <div class="pourquoi__grille">
        <div><h4>En faveur</h4><ul>{motifs_pos or '<li class="rien">rien de relevé</li>'}</ul></div>
        <div><h4>Contre</h4><ul>{motifs_neg or '<li class="rien">rien de relevé</li>'}</ul></div>
      </div>
    </details>
  </div>
  <div class="fiche__flanc">
    <span class="langue" title="Langue de l'annonce">{lg.get('drapeau','🏳️')} {e(lg.get('nom'))}</span>
    <div class="prix">{('CHF ' + format(int(prix), ',').replace(',', "'")) if prix else '—'}</div>
    <div class="verac">
      <div class="verac__barre"><i style="width:{score or 0}%;background:{e(v.get('couleur','#888'))}"></i></div>
      <span class="verac__txt" style="color:{e(v.get('couleur','#888'))}">
        {e(score) if score is not None else '—'} % · {e(v.get('niveau'))}
      </span>
      {'<span class="plafond" title="Plafonné : personne n\'a encore contacté le bailleur">plafond métadonnées</span>' if v.get('plafonne_sans_contact') else ''}
    </div>
    <span class="cat">{e(TYPE_FR.get(a.get('type'), a.get('type')))}</span>
  </div>
</article>"""


GABARIT = """<meta charset="utf-8">
<title>SaveMrA Zurich</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Barlow+Semi+Condensed:wght@400;500;600&display=swap">
<style>
:root{
  --ground:#F3F4F1; --surface:#FFFFFF; --surface2:#EAECE7;
  --ink:#171A1C; --ink2:#5A6360; --ligne:#D7DAD4;
  --accent:#0F5A6E; --accent-doux:#E1EDF0; --ombre:0 1px 2px rgba(23,26,28,.06);
  --f-titre:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
  --f-data:'Barlow Semi Condensed','Archivo',system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#14171A; --surface:#1C2024; --surface2:#23282C;
    --ink:#E9EBE7; --ink2:#98A19D; --ligne:#2F3539;
    --accent:#63C4D9; --accent-doux:#16323A; --ombre:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --ground:#14171A; --surface:#1C2024; --surface2:#23282C;
  --ink:#E9EBE7; --ink2:#98A19D; --ligne:#2F3539;
  --accent:#63C4D9; --accent-doux:#16323A; --ombre:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:var(--f-titre);font-size:15px;line-height:1.5;
  -webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.page{max-width:1120px;margin:0 auto;padding:clamp(20px,4vw,48px) clamp(14px,3vw,28px) 72px}

/* ── en-tête ─────────────────────────────────────────── */
.tete{display:flex;flex-wrap:wrap;gap:18px 32px;align-items:flex-end;
  justify-content:space-between;padding-bottom:20px;border-bottom:2px solid var(--ink)}
.tete h1{font-size:clamp(28px,4.4vw,42px);font-weight:700;letter-spacing:-.02em;
  margin:0;text-wrap:balance}
.tete .sous{color:var(--ink2);margin:6px 0 0;max-width:62ch;font-size:14.5px}
.meta{font-family:var(--f-data);font-size:14px;color:var(--ink2);text-align:right;
  line-height:1.65;font-variant-numeric:tabular-nums}
.meta b{color:var(--ink);font-weight:600}

/* ── tuiles ──────────────────────────────────────────── */
.tuiles{display:grid;gap:10px;margin:22px 0 26px;
  grid-template-columns:repeat(auto-fit,minmax(132px,1fr))}
.tuile{background:var(--surface);border:1px solid var(--ligne);border-radius:3px;
  padding:14px 16px;box-shadow:var(--ombre);display:flex;flex-direction:column;gap:2px}
.tuile b{font-family:var(--f-data);font-size:38px;font-weight:600;line-height:1;
  font-variant-numeric:tabular-nums}
.tuile span{font-size:13.5px;font-weight:500}
.tuile i{font-style:normal;font-size:12.5px;color:var(--ink2)}

/* ── filtres ─────────────────────────────────────────── */
.filtres{position:sticky;top:0;z-index:5;background:var(--ground);
  border-top:1px solid var(--ligne);border-bottom:1px solid var(--ligne);
  padding:12px 0;margin-bottom:26px;display:flex;flex-wrap:wrap;gap:10px 20px;
  align-items:center}
.grp{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.grp>label{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink2);font-weight:600}
.bouton{font:inherit;font-size:13px;padding:4px 11px;border:1px solid var(--ligne);
  background:var(--surface);color:var(--ink);border-radius:999px;cursor:pointer;
  transition:background .12s,border-color .12s}
.bouton:hover{border-color:var(--accent)}
.bouton b{font-family:var(--f-data);font-weight:600;opacity:.6;margin-left:1px}
.bouton[aria-pressed="true"] b{opacity:.85}
.bouton[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);
  color:var(--surface)}
:root[data-theme="dark"] .bouton[aria-pressed="true"]{color:#0F1518}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .bouton[aria-pressed="true"]{color:#0F1518}
  :root:not([data-theme="light"]) .dispo--ideal,
  :root:not([data-theme="light"]) .dispo--immediat{color:#5FBF9B}
  :root:not([data-theme="light"]) .alerte{color:#F08A8A}
  :root:not([data-theme="light"]) .genre{color:#E0B057}
}
.bouton:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
select,input[type=range]{font:inherit;font-size:13px;color:var(--ink);
  background:var(--surface);border:1px solid var(--ligne);border-radius:3px;padding:3px 6px}
input[type=range]{padding:0;accent-color:var(--accent);width:112px}
.val{font-family:var(--f-data);font-variant-numeric:tabular-nums;font-size:14px;
  min-width:44px;font-weight:600}

/* ── bandes ──────────────────────────────────────────── */
.bande{margin:0 0 34px;scroll-margin-top:70px}
.bande__tete{display:flex;align-items:baseline;gap:12px;padding:0 0 8px 14px;
  border-left:5px solid var(--bande);position:relative}
.bande__code{font-family:var(--f-data);font-weight:600;font-size:13px;
  background:var(--bande);color:#fff;border-radius:2px;padding:1px 7px;letter-spacing:.06em}
.bande__tete h2{font-size:19px;margin:0;font-weight:600;letter-spacing:-.01em}
.bande__tete p{margin:0;color:var(--ink2);font-size:13.5px;flex:1}
.bande__nb{font-family:var(--f-data);font-size:22px;font-weight:600;color:var(--ink2);
  font-variant-numeric:tabular-nums}
.bande__liste{display:flex;flex-direction:column;gap:8px}

/* ── fiche ───────────────────────────────────────────── */
.fiche{display:grid;grid-template-columns:76px 1fr 152px;gap:16px;
  background:var(--surface);border:1px solid var(--ligne);border-left:5px solid var(--bande);
  border-radius:3px;padding:13px 16px 13px 12px;box-shadow:var(--ombre)}
.fiche--alerte{border-color:#A11D1D;background:linear-gradient(0deg,rgba(161,29,29,.045),rgba(161,29,29,.045)),var(--surface)}
.fiche__minutes{--bande:#888;display:flex;flex-direction:column;align-items:center;
  justify-content:center;border-right:1px solid var(--ligne);padding-right:12px}
.fiche__minutes b{font-family:var(--f-data);font-size:38px;font-weight:600;line-height:.95;
  color:var(--bande);font-variant-numeric:tabular-nums}
.fiche__minutes span{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2)}
.fiche__corps{min-width:0}
.fiche h3{margin:0 0 3px;font-size:15.5px;font-weight:600;line-height:1.3}
.fiche h3 a{text-decoration:none;color:var(--ink);border-bottom:1px solid transparent}
.fiche h3 a:hover{border-bottom-color:var(--accent);color:var(--accent)}
.resume{margin:0 0 4px;font-family:var(--f-data);font-size:15px;color:var(--ink)}
.lieu{margin:0 0 6px;font-size:12.5px;color:var(--ink2)}
.lieu b{color:var(--ink);font-weight:500}
.puces{display:flex;flex-wrap:wrap;gap:5px;list-style:none;margin:0 0 6px;padding:0}
.puces li{font-size:11.5px;background:var(--surface2);border-radius:2px;padding:1px 7px;color:var(--ink2)}
.puce-meuble{color:#fff;background:var(--c);font-weight:500}
.puce-meuble--flou{background:transparent;color:var(--c);border:1px dashed currentColor}
.ameub{margin:5px 0 0;font-size:12.5px;color:var(--ink2);font-style:italic}
.dispo{margin:0;font-size:12.5px;color:var(--ink2)}
.dispo--ideal,.dispo--immediat{color:#12805C}
:root[data-theme="dark"] .dispo--ideal,:root[data-theme="dark"] .dispo--immediat{color:#5FBF9B}
.dispo--tardif,.dispo--hors_periode{color:#B5560F}
.alerte{margin:6px 0 0;font-size:12.5px;font-weight:600;color:#A11D1D}
.genre{margin:6px 0 0;font-size:12.5px;color:#8A5A12;background:var(--surface2);
  border-left:3px solid #C9962B;padding:4px 9px;border-radius:0 2px 2px 0}
:root[data-theme="dark"] .genre{color:#E0B057}
:root[data-theme="dark"] .alerte{color:#F08A8A}
.pourquoi{margin-top:7px}
.pourquoi summary{font-size:12px;color:var(--accent);cursor:pointer;width:max-content}
.pourquoi__grille{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:7px;
  padding:10px 12px;background:var(--surface2);border-radius:3px}
.pourquoi h4{margin:0 0 4px;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink2)}
.pourquoi ul{margin:0;padding-left:15px;font-size:12.5px;color:var(--ink)}
.pourquoi .rien{color:var(--ink2);list-style:none;margin-left:-15px}

.fiche__flanc{display:flex;flex-direction:column;align-items:flex-end;gap:5px;text-align:right}
.langue{font-size:12px;color:var(--ink2);white-space:nowrap}
.prix{font-family:var(--f-data);font-size:24px;font-weight:600;line-height:1;
  font-variant-numeric:tabular-nums}
.verac{width:100%}
.verac__barre{height:5px;background:var(--surface2);border-radius:999px;overflow:hidden}
.verac__barre i{display:block;height:100%}
.verac__txt{font-family:var(--f-data);font-size:12.5px;font-weight:600;display:block;margin-top:2px}
.cat{font-size:11.5px;color:var(--ink2)}
.plafond{font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink2);
  border:1px dashed var(--ligne);border-radius:2px;padding:0 5px;display:block;width:max-content}
.vide{padding:26px;text-align:center;color:var(--ink2);border:1px dashed var(--ligne);border-radius:3px}

footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--ligne);
  color:var(--ink2);font-size:13px;max-width:70ch}
footer h3{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink);margin:0 0 6px}
@media (max-width:760px){
  .fiche{grid-template-columns:60px 1fr;gap:12px}
  .fiche__flanc{grid-column:1/-1;flex-direction:row;align-items:center;justify-content:space-between;
    text-align:left;border-top:1px solid var(--ligne);padding-top:8px}
  .verac{width:42%}
  .pourquoi__grille{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="page">
  <header class="tete">
    <div>
      <h1>SaveMrA — logements Zurich</h1>
      <p class="sous">Stage à l'ETH, $sejour. Chaque annonce est classée par
      <b>temps de trajet réel</b> porte-à-porte vers le campus, notée sur un
      <b>indice de véracité</b> anti-arnaque, et étiquetée par langue avec un
      résumé en français.</p>
    </div>
    <p class="meta">
      <b>$total</b> annonces · mis à jour le <b>$maj</b><br>
      Labo : <b>$ref</b><br>
      Budget : <b>≤ CHF $plafond</b> charges comprises<br>
      Médiane du lot : <b>$mediane CHF/m²</b><br>
      Langues : $langues
    </p>
  </header>

  <div class="tuiles">$tuiles</div>

  <div class="filtres" role="group" aria-label="Filtres">
    <div class="grp"><label>Trajet</label>
      <button class="bouton" data-f="bande" data-v="A" aria-pressed="false">≤15</button>
      <button class="bouton" data-f="bande" data-v="B" aria-pressed="false">16–30</button>
      <button class="bouton" data-f="bande" data-v="C" aria-pressed="false">31–45</button>
      <button class="bouton" data-f="bande" data-v="D" aria-pressed="false">46–60</button>
      <button class="bouton" data-f="bande" data-v="E" aria-pressed="false">&gt;60</button>
    </div>
    <div class="grp"><label for="fv">Véracité min.</label>
      <input id="fv" type="range" min="0" max="100" step="10" value="0">
      <span class="val" id="fvv">0 %</span>
    </div>
    <div class="grp"><label>Loyer</label>$boutons_prix</div>
    <div class="grp"><label for="fl">Langue</label>
      <select id="fl"><option value="">toutes</option><option value="de">Allemand</option>
      <option value="gsw">Suisse allemand</option><option value="en">Anglais</option>
      <option value="fr">Français</option><option value="it">Italien</option></select>
    </div>
    <div class="grp"><label>Ameublement</label>
      <button class="bouton" data-f="meuble" data-v="meuble" aria-pressed="false">Meublé</button>
      <button class="bouton" data-f="meuble" data-v="partiel" aria-pressed="false">Partiel</button>
      <button class="bouton" data-f="meuble" data-v="non_meuble" aria-pressed="false">Non meublé</button>
      <button class="bouton" data-f="meuble" data-v="a_confirmer" aria-pressed="false">À confirmer</button>
    </div>
    <div class="grp"><label for="ft">Type</label>
      <select id="ft"><option value="">tous</option><option value="SHARED">Colocation</option>
      <option value="APARTMENT">Appartement</option><option value="ROOM">Chambre</option>
      <option value="STUDIO">Studio</option></select>
    </div>
    <div class="grp">
      <button class="bouton" id="fd" aria-pressed="false">Libre pour octobre</button>
      <button class="bouton" id="fr" aria-pressed="false">Masquer les suspectes</button>
    </div>
  </div>

  <main id="listes">$sections</main>

  <footer>
    <h3>Comment lire cette page</h3>
    <p>Le <b>temps en minutes</b> à gauche est un itinéraire ZVV/CFF réel
    (arrivée 9 h un mardi), marche jusqu'à l'arrêt comprise — pas une distance à
    vol d'oiseau. L'<b>indice de véracité</b> part de 50 % et applique les signaux
    documentés d'arnaque locative ; cinq signaux rédhibitoires le plafonnent à 8 %.
    Il signale où regarder, il ne remplace pas une visite.</p>
    <p><b>Aucun paiement avant d'avoir vu le logement.</b> C'est la seule règle qui
    protège vraiment.</p>
    <p>Les annonces <b>réservées aux femmes</b> sont retirées automatiquement de
    cette page ($retirees écartées à la dernière collecte). Celles qui expriment une
    simple préférence sont conservées et signalées en orange : le choix revient
    à qui postule, pas à l'outil.</p>
    <p><b>Ameublement :</b> la case « meublé » du portail est fausse une fois sur
    sept, et décochée ne veut pas dire vide — seulement non renseignée. La
    mention affichée croise donc la case et le texte de l'annonce, et assume un
    état « à confirmer » quand aucun des deux ne le dit. Pour six mois, meubler
    un logement vide coûte plus cher que l'écart de loyer : c'est la première
    question à poser.</p>
    <h3>Le reste du dossier</h3>
    <p><a href="https://github.com/bongix/SaveMrA/blob/main/docs/CANDIDATURE.md">Le message à envoyer et le dossier à préparer</a> ·
    <a href="https://github.com/bongix/SaveMrA/blob/main/docs/GLOSSAIRE.md">Décoder une annonce en allemand</a> ·
    <a href="https://github.com/bongix/SaveMrA/blob/main/docs/ANTI-ARNAQUE.md">Les six questions de contrôle à poser</a> ·
    <a href="https://github.com/bongix/SaveMrA/blob/main/docs/SOURCES.md">Où chercher ailleurs</a> ·
    <a href="https://github.com/bongix/SaveMrA">Le code</a></p>
  </footer>
</div>

<script>
(function(){
  var etat={bande:new Set(),tprix:new Set(),meuble:new Set(),verac:0,langue:"",type:"",dispo:false,fiables:false};
  var fiches=[].slice.call(document.querySelectorAll(".fiche"));
  function appliquer(){
    fiches.forEach(function(f){
      var d=f.dataset, ok=true;
      if(etat.bande.size && !etat.bande.has(d.bande)) ok=false;
      if(+d.verac < etat.verac) ok=false;
      if(etat.tprix.size && !etat.tprix.has(d.tprix)) ok=false;
      if(etat.meuble.size && !etat.meuble.has(d.meuble)) ok=false;
      if(etat.langue && d.langue!==etat.langue) ok=false;
      if(etat.type && d.type!==etat.type) ok=false;
      if(etat.dispo && !(d.dispo==="ideal"||d.dispo==="immediat"||d.dispo==="trop_tot")) ok=false;
      if(etat.fiables && +d.verac<40) ok=false;
      f.hidden=!ok;
    });
    document.querySelectorAll(".bande").forEach(function(s){
      var n=s.querySelectorAll(".fiche:not([hidden])").length;
      s.hidden=(n===0);
      s.querySelector(".bande__nb").textContent=n;
    });
    var total=document.querySelectorAll(".fiche:not([hidden])").length;
    var vide=document.getElementById("vide");
    if(!vide){vide=document.createElement("p");vide.id="vide";vide.className="vide";
      vide.textContent="Aucune annonce ne passe ces filtres. Élargissez le trajet ou le loyer.";
      document.getElementById("listes").appendChild(vide);}
    vide.hidden=(total>0);
  }
  ["bande","tprix","meuble"].forEach(function(cle){
    document.querySelectorAll("[data-f="+cle+"]").forEach(function(b){
      b.addEventListener("click",function(){
        var on=b.getAttribute("aria-pressed")==="true";
        b.setAttribute("aria-pressed",String(!on));
        if(on) etat[cle].delete(b.dataset.v); else etat[cle].add(b.dataset.v);
        appliquer();});
    });
  });
  function bascule(id,cle){var b=document.getElementById(id);
    b.addEventListener("click",function(){var on=b.getAttribute("aria-pressed")==="true";
      b.setAttribute("aria-pressed",String(!on));etat[cle]=!on;appliquer();});}
  bascule("fd","dispo"); bascule("fr","fiables");
  var fv=document.getElementById("fv");
  fv.addEventListener("input",function(){etat.verac=+fv.value;
    document.getElementById("fvv").textContent=fv.value+" %";appliquer();});
  document.getElementById("fl").addEventListener("change",function(e){etat.langue=e.target.value;appliquer();});
  document.getElementById("ft").addEventListener("change",function(e){etat.type=e.target.value;appliquer();});
  appliquer();
})();
</script>
"""


def construire():
    d = json.loads((RACINE / "data" / "annonces.json").read_text())
    tranches = json.loads((RACINE / "data" / "tranches.json").read_text())["tranches"]
    campus = json.loads((RACINE / "data" / "campus.json").read_text())
    ann = d["annonces"]
    sejour = d.get("sejour", {})

    par_bande = collections.OrderedDict((t["code"], []) for t in tranches)
    par_bande["?"] = []
    for a in ann:
        par_bande.setdefault((a.get("trajet") or {}).get("tranche", "?"), []).append(a)

    n_fiables = sum(1 for a in ann if (a.get("veracite") or {}).get("score", 0) >= 60)
    n_suspects = sum(1 for a in ann if (a.get("veracite") or {}).get("score", 100) < 40)
    n_dispo = sum(1 for a in ann if (a.get("dispo") or {}).get("ok"))
    n_proche = len(par_bande.get("A", [])) + len(par_bande.get("B", []))
    n_ameuble = sum(1 for a in ann if (a.get("ameublement") or {}).get("code") == "meuble")
    langues = collections.Counter((a.get("langue") or {}).get("nom", "?") for a in ann)

    tuiles = [
        (n_proche, "à 30 min ou moins", "du campus de référence"),
        (n_fiables, "annonces crédibles", "véracité ≥ 60 %"),
        (n_dispo, "libres à temps", sejour.get("libelle", "")),
        (n_ameuble, "meublés", "confirmé par l'annonce"),
        (n_suspects, "à écarter", "véracité < 40 %"),
    ]

    sections = ""
    for t in tranches + [{"code": "?", "label": "Trajet non calculé", "couleur": "#8A8F8B",
                          "verdict": "adresse insuffisante pour un itinéraire"}]:
        lot = par_bande.get(t["code"], [])
        if not lot:
            continue
        sections += f"""
<section class="bande" id="bande-{t['code']}" style="--bande:{t['couleur']}">
  <header class="bande__tete">
    <span class="bande__code">{t['code']}</span>
    <h2>{e(t['label'])}</h2>
    <p>{e(t['verdict'])}</p>
    <span class="bande__nb">{len(lot)}</span>
  </header>
  <div class="bande__liste">{''.join(carte(a) for a in lot)}</div>
</section>"""

    tp = d.get("tranches_prix", [])
    compte_tp = collections.Counter((a.get("tranche_prix") or {}).get("code") for a in ann)
    boutons_prix = "".join(
        f'<button class="bouton" data-f="tprix" data-v="{t["code"]}" aria-pressed="false" '
        f'title="{e(t["verdict"])}">{e(t["label"])} <b>{compte_tp.get(t["code"], 0)}</b></button>'
        for t in tp)

    ref = campus["campus"][d.get("campus_reference", "zentrum")]["nom"]
    maj = datetime.datetime.fromisoformat(d["genere_le"]).strftime("%d.%m.%Y à %H:%M")
    lang_txt = " · ".join(f"{n} {k.lower()}" for k, n in langues.most_common())

    return string.Template(GABARIT).substitute(
        maj=maj, ref=e(ref), total=len(ann), sejour=e(sejour.get("libelle", "")),
        mediane=d.get("mediane_chf_par_m2") or "—",
        langues=e(lang_txt),
        tuiles="".join(f'<div class="tuile"><b>{n}</b><span>{e(l)}</span><i>{e(sub)}</i></div>'
                       for n, l, sub in tuiles),
        sections=sections,
        boutons_prix=boutons_prix,
        plafond=d.get("loyer_max_chf", "—"),
        retirees=d.get("retirees_genre", 0),
    )


if __name__ == "__main__":
    SORTIE.write_text(construire())
    print(f"→ {SORTIE}  ({SORTIE.stat().st_size // 1024} Ko)")
