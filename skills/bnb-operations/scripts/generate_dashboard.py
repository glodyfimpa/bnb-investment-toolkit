#!/usr/bin/env python3
"""Generate a read-only purchases dashboard (HTML) from a BnB Shopping List.

This is a pure transformation: Shopping List items (JSON) in -> HTML out. It does
NOT hold Notion credentials and does NOT query Notion itself: the data arrives
from Claude (read via MCP) as a JSON file. The Notion database stays the single
source of truth; the dashboard is a regenerated view with no state of its own —
no localStorage, no hardcoded decisions. Change the Stato in Notion and regenerate.

Why parametric (house_name / source_url): this script lives in the reusable
bnb-investment-toolkit plugin, so it must not be hardwired to one apartment.

Usage:
    python3 generate_dashboard.py <items.json> <output.html> [house_name] [source_url]

items.json format: list of objects with the Notion data-source keys:
    Voce, Modello, Qty, "Prezzo EUR", Stato, Categoria, Canale, Link, Note
"""

import html
import json
import sys
from datetime import datetime

STATO_ORDER = {
    "Da comprare": 0,
    "In carrello": 1,
    "Comprato": 2,
    "Già in loco": 3,
    "Scartato": 4,
}
STATO_COLOR = {
    "Da comprare": "#f85149",
    "In carrello": "#d29922",
    "Comprato": "#3fb950",
    "Già in loco": "#388bfd",
    "Scartato": "#8b949e",
}
CATEGORIA_ORDER = ["Arredo & comfort", "Sicurezza", "Kit cortesia", "Dopo avvio"]


def euro(n):
    return f"€ {n:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def esc(s):
    return html.escape(str(s if s is not None else ""))


def build(items, generated_at, house_name="BnB", source_url=""):
    # Totali ricalcolati dai dati del DB (le "somme che fanno capire i costi").
    # Asciugacapelli/voci a 0 restano fuori dalla spesa ma dentro la checklist.
    spesa_items = [
        i for i in items
        if i.get("Stato") != "Scartato" and float(i.get("Prezzo EUR") or 0) > 0
    ]
    tot_generale = sum(float(i.get("Prezzo EUR") or 0) for i in spesa_items)

    def somma_stato(stato):
        return sum(
            float(i.get("Prezzo EUR") or 0)
            for i in spesa_items if i.get("Stato") == stato
        )

    tot_da_comprare = somma_stato("Da comprare")
    tot_carrello = somma_stato("In carrello")
    tot_comprato = somma_stato("Comprato")

    # Subtotali per canale (totale semplice) e per categoria (con split
    # speso/da spendere, perché il controllo costi è la priorità).
    per_canale = {}
    per_cat = {}  # cat -> {"tot":x, "speso":y, "resta":z}
    for i in spesa_items:
        c = i.get("Categoria") or "—"
        ch = i.get("Canale") or "—"
        prezzo = float(i.get("Prezzo EUR") or 0)
        per_canale[ch] = per_canale.get(ch, 0) + prezzo
        slot = per_cat.setdefault(c, {"tot": 0, "speso": 0, "resta": 0})
        slot["tot"] += prezzo
        if i.get("Stato") == "Comprato":
            slot["speso"] += prezzo
        else:
            slot["resta"] += prezzo

    n_comprato = sum(1 for i in items if i.get("Stato") == "Comprato")
    n_tot = len([i for i in items if i.get("Stato") != "Scartato"])

    def cat_key(i):
        c = i.get("Categoria") or "zzz"
        return (CATEGORIA_ORDER.index(c) if c in CATEGORIA_ORDER else 99,
                STATO_ORDER.get(i.get("Stato"), 9),
                -float(i.get("Prezzo EUR") or 0),
                i.get("Voce") or "")

    rows = []
    for i in sorted(items, key=cat_key):
        stato = i.get("Stato") or "—"
        col = STATO_COLOR.get(stato, "#8b949e")
        prezzo = float(i.get("Prezzo EUR") or 0)
        prezzo_txt = euro(prezzo) if prezzo > 0 else "—"
        qty = i.get("Qty")
        qty_txt = f"× {int(qty)}" if qty and float(qty) > 1 else ""
        link = i.get("Link")
        voce_cell = esc(i.get("Voce"))
        if link:
            voce_cell = f'<a href="{esc(link)}" target="_blank" rel="noopener">{voce_cell}</a>'
        rows.append(f"""      <tr class="stato-{STATO_ORDER.get(stato, 9)}">
        <td class="voce">{voce_cell} <span class="qty">{esc(qty_txt)}</span></td>
        <td class="modello">{esc(i.get('Modello'))}</td>
        <td class="cat">{esc(i.get('Categoria'))}</td>
        <td class="canale">{esc(i.get('Canale'))}</td>
        <td class="prezzo">{esc(prezzo_txt)}</td>
        <td class="stato"><span class="badge" style="background:{col}1a;color:{col};border-color:{col}55">{esc(stato)}</span></td>
        <td class="note">{esc(i.get('Note'))}</td>
      </tr>""")

    def kv_rows(d):
        return "".join(
            f'<div class="kv"><span>{esc(k)}</span><strong>{esc(euro(v))}</strong></div>'
            for k, v in sorted(d.items(), key=lambda x: -x[1]) if v > 0
        )

    def cat_rows(d):
        out = []
        for k, s in sorted(d.items(), key=lambda x: -x[1]["tot"]):
            if s["tot"] <= 0:
                continue
            out.append(
                f'<div class="catrow">'
                f'<div class="catname">{esc(k)}<strong>{esc(euro(s["tot"]))}</strong></div>'
                f'<div class="catsplit">'
                f'<span class="sp">speso {esc(euro(s["speso"]))}</span>'
                f'<span class="rs">resta {esc(euro(s["resta"]))}</span>'
                f'</div></div>'
            )
        return "".join(out)

    # Source-of-truth link in the banner. Parametric: a configured Notion URL
    # becomes a link, otherwise a plain label, so the view never points at the
    # wrong apartment's database.
    if source_url:
        source_link = (
            f'<a href="{esc(source_url)}" target="_blank" rel="noopener">'
            f"database Shopping List Notion</a>"
        )
    else:
        source_link = "database Shopping List su Notion"

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(house_name)} — Dashboard Acquisti (vista generata)</title>
<style>
  :root {{ --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#e6edf3; --faint:#8b949e; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
  .container {{ max-width:1200px; margin:0 auto; padding:24px; }}
  .banner {{ background:#1c2128; border:1px solid #f0883e; border-left-width:4px; border-radius:6px; padding:12px 16px; margin-bottom:20px; font-size:13px; color:#f0883e; }}
  .banner a {{ color:#f0883e; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .sub {{ color:var(--faint); margin-bottom:24px; font-size:13px; }}
  .totals {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:20px; }}
  .tcard {{ background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:16px; }}
  .tcard .lbl {{ color:var(--faint); font-size:12px; text-transform:uppercase; letter-spacing:.5px; }}
  .tcard .val {{ font-size:24px; font-weight:700; margin-top:6px; }}
  .breakdown {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:24px; }}
  .bd {{ background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:16px; }}
  .bd h3 {{ margin:0 0 10px; font-size:13px; color:var(--faint); text-transform:uppercase; }}
  .kv {{ display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid var(--border); }}
  .kv:last-child {{ border:0; }}
  .catrow {{ padding:8px 0; border-bottom:1px solid var(--border); }}
  .catrow:last-child {{ border:0; }}
  .catname {{ display:flex; justify-content:space-between; font-weight:600; }}
  .catsplit {{ display:flex; justify-content:space-between; margin-top:3px; font-size:12px; }}
  .catsplit .sp {{ color:#3fb950; }}
  .catsplit .rs {{ color:#f85149; }}
  table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--border); border-radius:8px; overflow:hidden; }}
  th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--border); vertical-align:top; }}
  th {{ background:#1c2128; color:var(--faint); font-size:12px; text-transform:uppercase; position:sticky; top:0; }}
  td.prezzo {{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }}
  td.voce a {{ color:#58a6ff; text-decoration:none; }}
  td.voce a:hover {{ text-decoration:underline; }}
  .qty {{ color:var(--faint); font-size:12px; }}
  .modello,.note {{ color:var(--faint); font-size:12.5px; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:10px; border:1px solid; font-size:11.5px; font-weight:600; white-space:nowrap; }}
  tr.stato-2 td.voce {{ text-decoration:line-through; opacity:.55; }}
  tr.stato-4 {{ opacity:.4; }}
  .foot {{ margin-top:20px; color:var(--faint); font-size:12px; }}
</style>
</head>
<body>
<div class="container">
  <div class="banner">
    <strong>Vista generata da Notion</strong> il {generated_at} — sola lettura.
    La fonte di verità è il {source_link}.
    Non modificare qui: cambia lo Stato su Notion e rigenera. Nessun dato è salvato in questo file.
  </div>

  <h1>{esc(house_name)} — Dashboard Acquisti</h1>
  <div class="sub">{n_comprato}/{n_tot} voci comprate · {len(items)} voci totali nel database</div>

  <div class="totals">
    <div class="tcard"><div class="lbl">Da comprare</div><div class="val" style="color:#f85149">{euro(tot_da_comprare)}</div></div>
    <div class="tcard"><div class="lbl">In carrello</div><div class="val" style="color:#d29922">{euro(tot_carrello)}</div></div>
    <div class="tcard"><div class="lbl">Comprato</div><div class="val" style="color:#3fb950">{euro(tot_comprato)}</div></div>
  </div>
  <div class="tcard" style="margin-bottom:20px;text-align:center">
    <div class="lbl">Totale stimato (tutte le voci a costo &gt; 0)</div>
    <div class="val">{euro(tot_generale)}</div>
  </div>

  <div class="breakdown">
    <div class="bd"><h3>Per categoria</h3>{cat_rows(per_cat)}</div>
    <div class="bd"><h3>Per canale</h3>{kv_rows(per_canale)}</div>
  </div>

  <table>
    <thead><tr>
      <th>Voce</th><th>Modello</th><th>Categoria</th><th>Canale</th>
      <th style="text-align:right">Prezzo</th><th>Stato</th><th>Note</th>
    </tr></thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>

  <div class="foot">
    Generato da <code>dashboard-generator/generate_dashboard.py</code> ·
    dati estratti dal database Notion via MCP · voci a € 0 escluse dai totali di spesa.
  </div>
</div>
</body>
</html>"""


def main():
    if not 3 <= len(sys.argv) <= 5:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        items = json.load(f)
    house_name = sys.argv[3] if len(sys.argv) >= 4 else "BnB"
    source_url = sys.argv[4] if len(sys.argv) >= 5 else ""
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    out = build(items, generated_at, house_name=house_name, source_url=source_url)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK: {len(items)} voci -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
