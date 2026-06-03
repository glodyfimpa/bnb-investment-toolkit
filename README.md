```
 ____        ____    ___                     _                        _
| __ ) _ __ | __ )  |_ _|_ ____   _____  ___| |_ _ __ ___   ___ _ __ | |_
|  _ \| '_ \|  _ \   | || '_ \ \ / / _ \/ __| __| '_ ` _ \ / _ \ '_ \| __|
| |_) | | | | |_) |  | || | | \ V /  __/\__ \ |_| | | | | |  __/ | | | |_
|____/|_| |_|____/  |___|_| |_|\_/ \___||___/\__|_| |_| |_|\___|_| |_|\__|
 _____           _ _    _ _
|_   _|__   ___ | | | _(_) |_
  | |/ _ \ / _ \| | |/ / | __|
  | | (_) | (_) | |   <| | |_
  |_|\___/ \___/|_|_|\_\_|\__|
```

A Claude Code plugin for short-term rentals in Italy, end to end.

Scout apartments from rental portals, evaluate zones with real market data, calculate ROI projections, generate business plans with go/no-go recommendations. Then run the rental once it's live: research supplies on Amazon.it and sync them to the Notion Shopping List, write the listing copy, draft guest messages, and regenerate a read-only purchases dashboard. Built around Italian tax rules (cedolare secca), LT/CAV compliance, and InsideAirbnb data.

## Install

Inside a Claude Code session:

```
/plugin marketplace add glodyfimpa/bnb-investment-toolkit
/plugin install bnb-investment-toolkit@bnb-investment-toolkit
```

Or from the terminal:

```bash
claude plugin marketplace add glodyfimpa/bnb-investment-toolkit
claude plugin install bnb-investment-toolkit@bnb-investment-toolkit
```

Or interactively inside Claude Code:

```
/plugin marketplace add glodyfimpa/bnb-investment-toolkit
/plugin
```

Then go to the **Discover** tab, select `bnb-investment-toolkit`, and choose a scope (user, project, or local).

Verify with `/plugin list` (or `claude plugin list`). You should see `bnb-investment-toolkit@bnb-investment-toolkit — Status: ✔ enabled`. Restart Claude Code after installing so the new slash commands are registered.

## Update

```
/plugin marketplace update bnb-investment-toolkit
```

To receive updates automatically:

1. Run `/plugin`
2. Go to the **Marketplaces** tab
3. Select `bnb-investment-toolkit`
4. Select **Enable auto-update**

### Team setup

Pre-enable the plugin in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bnb-investment-toolkit@bnb-investment-toolkit": true
  },
  "extraKnownMarketplaces": {
    "bnb-investment-toolkit": {
      "source": {
        "source": "github",
        "repo": "glodyfimpa/bnb-investment-toolkit"
      }
    }
  }
}
```

## Prerequisites

Before using the plugin, connect:

1. A **project tracker** (Notion, Airtable, or Google Sheets) with write access for saving scouted properties
2. **Browser access** for navigating rental portals (Immobiliare.it, Idealista, Casa.it)

The property tracker uses `~~project tracker` as a tool-agnostic placeholder. See `CONNECTORS.md` for setup details and database schema.

## Commands

| Command | Does |
|---------|------|
| `/scan-apartments [city] [max-price]` | Navigate rental portals, extract listings, deduplicate, score, save qualified properties to project tracker |
| `/analyze-zone [zone-name] [city]` | Pull InsideAirbnb data for a specific neighborhood: occupancy, nightly rates, competitor count, price percentiles |
| `/business-plan [rent] [zone]` | Full financial projection with scenario analysis at 80/100/120% occupancy, Excel spreadsheet, go/no-go recommendation |

## How it works

Three skills cover the lifecycle: two for acquiring a property, one for running it once it's live.

**Property acquisition tracker** automates the grunt work of apartment hunting. It navigates Immobiliare.it and Idealista with configurable filters (price, size, zone, contract type), extracts listing data, checks for subletting restrictions, deduplicates across portals, calculates a quick investment score, and saves qualified listings to your project tracker. Upper floors without elevator get skipped. Transitorio contracts get skipped. Listings that mention "no sublocazione" or "vietato Airbnb" get skipped. What remains is worth evaluating.

**Short-term rental analyzer** takes a zone or a specific apartment and runs the numbers. It downloads real market data from InsideAirbnb (nightly rates, occupancy, competitor density), feeds it into a financial model that accounts for cedolare secca, Airbnb commission structure (3% split-fee or 15.5% host-only), and all operating costs. The output is a monthly projection, an annual ROI calculation, and a recommendation based on three thresholds that all need to pass.

**BnB operations** handles the day-to-day once the rental is live, routing to four jobs. *Shopping researcher* searches Amazon.it for a needed item, gathers requirements first, verifies each candidate on its real product page (never trusting the search-page price), checks the real Prime delivery date, then compares against the Notion Shopping List with `shopping_compare.py` so you update the right row instead of creating a duplicate. *Listing copywriter* writes the Airbnb title, description, access note, neighborhood pitch, and house rules. *Guest templates* drafts the six-message stay sequence (booking, self check-in, in-home info, check-out, review) in Italian and English. *Acquisti view* regenerates a read-only purchases dashboard from the Shopping List with `generate_dashboard.py` — no localStorage, Notion stays the source of truth. The whole module keeps listing copy and guest messaging consistent with Italian LT compliance (a recurring personal service would reclassify the rental as CAV/B&B).

## Decision criteria

A property gets a GO recommendation only when all three metrics clear their minimum:

| Metric | Minimum | Optimal |
|--------|---------|---------|
| Break-even | <= 10 days/month | <= 8 days/month |
| ROI | >= 40% annual | >= 60% annual |
| Revenue-to-Rent Ratio | >= 2.5x | >= 3x |

The break-even counts how many occupied nights per month cover all fixed costs. ROI measures annual net profit against annual rent paid. Revenue-to-rent ratio is gross monthly revenue (after platform fees) divided by monthly rent. Properties that hit all three optimal thresholds get an "Excellent" confidence rating.

## Tax rules

The calculator uses cedolare secca, Italy's flat tax on short-term rental income. First property: 21%. Second property: 26% on the lower-earning one, 21% on the higher. Operating expenses are not deductible under this regime. Three or more properties require P.IVA registration and a different tax structure entirely.

Airbnb commission defaults to 3% (split-fee model for individual hosts). Hosts using a PMS or host-only pricing pay 15.5% instead. The calculator accepts both via a parameter.

## Market coverage

Milan is pre-configured with zone-level average nightly rates (Centro Storico through Citta Studi) and InsideAirbnb data URLs. To add another Italian city, add its InsideAirbnb URL to the `CITY_DATA_URLS` dictionary in `scripts/market_analyzer.py`. For non-Italian markets, adjust tax rates accordingly.

## Project tracker schema

When setting up the database in Notion, Airtable, or similar:

| Field | Type |
|-------|------|
| Name | Title |
| URL | URL |
| Price | Number (EUR) |
| Size (m2) | Number |
| Zone | Text |
| Rooms | Number |
| Floor | Text |
| Condo Fees | Number (EUR) |
| Score | Number |
| Investment Status | Select (Hot, Review, Watch, Skip) |
| Source | Select (Immobiliare, Idealista, Casa.it) |
| Scan Date | Date |
| Notes | Text |

## Structure

```
bnb-investment-toolkit/                              the plugin
├── .claude-plugin/
│   └── plugin.json                                 plugin manifest
├── commands/
│   ├── scan-apartments.md                          portal scouting entry point
│   ├── analyze-zone.md                             zone market analysis
│   └── business-plan.md                            full financial projection
├── skills/
│   ├── short-term-rental-analyzer/
│   │   ├── SKILL.md                                zone analysis + business plan workflow
│   │   └── scripts/
│   │       ├── market_analyzer.py                  InsideAirbnb data pull + zone stats
│   │       ├── business_plan_calculator.py         ROI, break-even, scenario analysis
│   │       └── create_template.py                  Excel business plan generator
│   ├── property-acquisition-tracker/
│   │   ├── SKILL.md                                portal scouting workflow
│   │   └── references/
│   │       ├── portals.md                          URL patterns, filters, extraction rules
│   │       └── scoring.md                          thresholds, formulas, zone rates
│   └── bnb-operations/                             running the live rental
│       ├── SKILL.md                                router across the four jobs
│       ├── references/
│       │   ├── shopping-researcher.md              Amazon.it research + Notion sync
│       │   ├── listing-copywriter.md               Airbnb listing copy
│       │   ├── guest-templates.md                  guest message sequence
│       │   └── acquisti-view.md                    purchases dashboard workflow
│       ├── scripts/
│       │   ├── shopping_compare.py                 candidate vs Shopping List verdict (tested)
│       │   └── generate_dashboard.py               JSON to read-only HTML (tested)
│       ├── assets/
│       │   └── guest-messages-it.md                fill-in message templates IT/EN
│       └── tests/                                  pytest suite for the two scripts
├── CONNECTORS.md                                   tool-agnostic connector docs
└── README.md
```

3 commands, 3 skills, 5 Python scripts, 6 reference/asset files. No hooks, no agents.

## License

MIT
