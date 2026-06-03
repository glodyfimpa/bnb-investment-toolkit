# Shopping Researcher

Research a purchase for a live short-term rental on Amazon.it, verify it on the
real product page, compare it against what's already tracked in the Notion
Shopping List, and update the list without creating duplicates.

This is the most-used operations workflow: a BnB constantly needs small items
(cushions, napkins, placemats, kitchenware, safety devices). Done by hand it
wastes 20+ minutes per item on dead-end candidates and ends with a Shopping List
full of near-duplicate rows. This workflow exists to make it fast and clean.

## Step 0 — Gather requirements BEFORE opening a browser (mandatory)

Do not start searching until you know what "good" means for this item. Skipping
this produces a confident search for the wrong thing. Ask the user, in one
`AskUserQuestion` round, only what you can't infer:

- **Budget** — a ceiling, or "cheapest that's decent", or "quality over price"
- **Use / context** — guest-facing decor, consumable, safety compliance, kitchen?
- **Deal-breakers** — color, material, must-have size, delivery deadline

Infer the rest from the Shopping List row and the project context; don't ask what
you can read. If the user already gave budget and use in the request, skip the
question and state the assumptions you're running with.

Do NOT impose requirements the user didn't state. "Cushions" does not mean
"45×45 cushions" unless they said so. Sample the real market first, then narrow.
(See gotcha `feedback_product_search_rigid_requirements` in the user's CLAUDE.md.)

## Step 1 — Read the current Shopping List from Notion

The Shopping List is the source of truth, not a local file. Fetch the relevant
rows for this item from the Notion database (the project's Daily Tracker /
Shopping List DB) via MCP. You need at least: `Voce`, `Modello`, `Prezzo EUR`,
`Stato`. Keep these — `shopping_compare.py` consumes exactly this shape.

If the item is already marked `Comprato`, stop and tell the user; don't research
something already bought.

## Step 2 — Search and sample, don't filter prematurely

Search Amazon.it for the item. Browser tooling: Playwright MCP (browser reale
bypassa il 503 anti-bot), Chrome MCP on the user's logged-in profile, or
WebSearch + trovaprezzi.it as fallback. (Amazon.it WebFetch is reliably blocked
with HTTP 503 — see `feedback_amazon` gotchas.)

Pull the **top 6-8 candidates** and present them as a sample of what the market
offers, then narrow with the user. Resist the urge to score-and-filter down to
one "winner" before the user has seen the spread — descriptive beats prescriptive
here, and the user can spot the right trade-off faster than a formula can.

## Step 3 — Verify each shortlisted candidate on its real product page (never trust the search page)

The search/listing page lies: prices shown there can be stale, for a different
variant, or for a bundle. Before recommending any candidate, navigate to its
product page (PDP) and confirm against the live page:

- **Price** present on the PDP. If the ASIN redirects elsewhere or the title no
  longer matches what the search promised, discard it.
- **Title / variant** matches the size, color, quantity you actually want.
- **Reviews** — read real ones. If login-walled, use the `/product-reviews/`
  page as a no-login fallback.

This single rule (verify on PDP, never trust search-page price) prevents most
bad recommendations. A candidate that can't be confirmed on its own page is not
a candidate.

## Step 4 — Check the real delivery date, not the logged-out one

A logged-out Playwright session shows pessimistic "guest" delivery dates (often
3-5 days out) even on Prime items the user would actually receive tomorrow. Do
not discard a candidate for a slow date seen from a logged-out browser.

- Look for the **"oppure consegna più rapida"** line under the standard delivery
  row — there's often a faster option the first line hides.
- If timing is the deciding factor, ask the user what their Prime account shows,
  or read it from their logged-in Chrome profile. Don't conclude "nothing
  arrives in time" from a logged-out session — that's a systematic false negative.

(Gotchas: `feedback_amazon_logged_out_delivery`, `feedback_amazon_check_express_delivery`.)

## Step 5 — Compare against the list with shopping_compare.py

For each verified candidate, run the comparison so the decision is deterministic:

```bash
python3 scripts/shopping_compare.py   # used as a module — see below
```

In practice, call it inline:

```python
import sys; sys.path.insert(0, "scripts")
import shopping_compare as sc
verdict = sc.compare(candidate, list_items)
```

`candidate` = `{"title": ..., "price": "19,99 €", "url": ...}`.
`list_items` = the rows fetched in Step 1.

`verdict["action"]` tells you what to do:

| action | meaning | what you do |
|---|---|---|
| `add_new` | nothing similar tracked | propose a NEW Shopping List row |
| `already_bought` | matches an item marked Comprato | stop, report, don't re-buy |
| `update_cheaper` | matches a tracked item AND beats its price | update the existing row (price + link), report the saving in `delta_eur` |
| `already_tracked` | matches a tracked item, not cheaper | update only the link/model if useful, never add a duplicate row |

The `find_match` logic is intentionally fuzzy on wording but refuses to merge two
items that share only one generic word. If it returns `add_new` for something you
believe is a duplicate, the wording diverged too far — tell the user and confirm
before adding.

## Step 6 — Sync the Notion Shopping List (don't forget this)

Whatever the verdict, the final state must land in Notion, because the Shopping
List is the source of truth and any HTML dashboard is just a regenerated view.
A common failure is recommending a purchase and leaving the Notion row stale at
"Da comprare / Canale=IKEA". Close the loop:

- `add_new` → create the row (Voce, Modello, Prezzo EUR, Link, Stato="Da comprare", Categoria, Canale="Amazon").
- `update_cheaper` / `already_tracked` → update the matched row in place.
- After the user buys → set `Stato="Comprato"`. Then regenerate the acquisti view
  (see `acquisti-view.md`).

Report to the user: what you found, the verdict, the saving if any, and confirm
the Notion row is updated.

## Pattern credits

Step 0 (mandatory requirements gathering) and Step 3 (verify on PDP, never trust
search page) are adapted from the methodology of
[jlave-dev/agent-skills@amazon-shopping](https://github.com/jlave-dev/agent-skills/tree/main/skills/amazon-shopping),
retargeted from amazon.com/Chrome-DevTools to amazon.it/Playwright with Prime
delivery checks and a Notion sync step.
