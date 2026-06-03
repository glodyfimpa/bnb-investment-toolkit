# Acquisti View

Generate a read-only HTML dashboard of the BnB's purchases from the Notion
Shopping List: totals (to-buy / in-cart / bought), breakdown by category and
channel, and the full item table.

The key design rule: this view holds NO state of its own. No localStorage, no
hardcoded decisions. The Notion Shopping List is the single source of truth; the
HTML is a snapshot you regenerate whenever the data changes. A localStorage-backed
dashboard traps state in one browser, breaks across devices and paths, and can't
be read by a daily automation — which is why an earlier version was rejected. See
the user's gotcha `feedback_bnb_acquisti_source_of_truth`.

## Workflow

### 1. Read the Shopping List from Notion

Fetch the items from the project's Shopping List database via MCP. Each item
needs these keys (the same shape `shopping_compare.py` and the dashboard expect):

```
Voce, Modello, Qty, "Prezzo EUR", Stato, Categoria, Canale, Link, Note
```

`Stato` is one of: `Da comprare`, `In carrello`, `Comprato`, `Già in loco`,
`Scartato`. Save the items to a JSON file (a list of objects).

### 2. Generate the HTML

```bash
python3 scripts/generate_dashboard.py items.json acquisti.html "<House Name>" "<Notion DB URL>"
```

- `items.json` — the list you just saved
- `acquisti.html` — output path
- `<House Name>` (optional) — e.g. "Via Braida"; defaults to "BnB"
- `<Notion DB URL>` (optional) — the source-of-truth link shown in the banner

The script recomputes every total from the data — it never trusts a stored total.
Items priced at 0 (already on site) stay in the checklist but don't count toward
spend; `Scartato` items render struck-through and are excluded from spend.

### 3. Open and report

`open acquisti.html`. Tell the user the spend so far, what's left to buy, and that
the view is read-only — to change anything, edit the Notion row and regenerate.

## Why this lives here

The script is the generalized version of the one built for Via Braida
(`projects/via-braida/dashboard-generator/`), parametrized on house name and
source URL so it works for any apartment in the toolkit. It's covered by tests in
`tests/test_generate_dashboard.py` (totals recomputed, no localStorage, parametric
title, zero-priced kept in checklist).
