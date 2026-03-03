---
name: property-acquisition-tracker
description: |
  Automated property scouting for short-term rental investments. Use when scanning rental portals (Immobiliare.it, Idealista, Casa.it) for apartments, filtering listings by investment criteria, calculating quick scores, and saving qualified properties to ~~project tracker. Triggers include: "scan for apartments", "find rental properties", "search listings for BnB", "scout properties in Milan", or requests to automate property research. Works with browser automation to navigate portals, extract listing data, deduplicate across platforms, apply scoring criteria, and save to database with structured fields.
version: 0.1.0
---

# Property Acquisition Tracker

Automate rental property scouting for short-term rental investments. Navigate real estate portals, extract listing data, apply investment scoring, deduplicate across platforms, save qualified properties to ~~project tracker.

## Prerequisites

Before running, verify:
1. Browser access to target real estate portals
2. ~~project tracker connector enabled with write access to a property database
3. Investment criteria from `references/scoring.md` loaded

## Workflow

### Step 1: Configure Search Parameters

Default search criteria (customizable by user):
- Property type: Bilocale (2 locali)
- Size: 50-65 m2
- Price range: 800-1,500 EUR/month total (rent + condo fees combined)
- Contract type: 4+4 (canone libero) - REQUIRED, skip transitorio/uso foresteria
- Floor: Ground floor OK; upper floors REQUIRE elevator
- Subletting: SKIP if listing prohibits sublocazione, affitti brevi, or Airbnb
- Zones: Configurable target zones (see `references/portals.md` for Milan defaults)

User can override any parameter. If user specifies different criteria, use those instead.

See `references/scoring.md` for investment scoring formulas and cost parameters.

### Step 2: Navigate Portals

For each portal (Immobiliare.it first, then Idealista):

1. Open portal search page with filters applied
2. Set location
3. Apply property type and size filters
4. Apply price range filter
5. Navigate through results pages (max 5 pages per portal to avoid overload)

See `references/portals.md` for URL structures and filter parameters.

### Step 3: Extract Listing Data

For each listing in search results, extract:

| Field | Required |
|-------|----------|
| Title | Yes |
| URL | Yes |
| Price (monthly rent) | Yes |
| Size (m2) | Yes |
| Rooms (locali) | Yes |
| Zone | Yes |
| Contract type | Yes |
| Floor | Yes |
| Elevator | Yes (if floor > 0) |
| Subletting restrictions | Yes |
| Condo fees | No |
| Energy class | No |

Skip listings that fail filter criteria: outside target zones, exceed price cap, wrong size range, wrong contract type, no elevator on upper floors, subletting restrictions detected.

### Step 4: Deduplicate

Before processing any listing, check for duplicates:

1. Normalize address: lowercase, remove punctuation, standardize abbreviations ("via" = "v.", "corso" = "c.so")
2. Compare against already-extracted listings in current session
3. If address matches (fuzzy, 90% similarity), check sqm (+/-5) and price (+/-50 EUR)
4. If duplicate found, skip and note which portal had it first

### Step 5: Calculate Quick Score

For each unique listing, calculate quick investment score using total monthly cost (rent + condo fees):

```
quick_score = (zone_avg_nightly_rate x 20) / total_monthly_cost x 10
```

Score interpretation:
- >=30: High potential, save with status "Hot"
- 25-29: Moderate potential, save with status "Review"
- 20-24: Worth monitoring, save with status "Watch"
- <20: Skip unless exceptional location

Zone average rates and detailed scoring in `references/scoring.md`.

### Step 6: Save to ~~project tracker

For qualified listings, save to ~~project tracker database with structured fields:

- Name: Listing title (e.g., "Bilocale via Savona 25, Navigli, Milano | 2 locali | 55 m2")
- URL: Full listing URL
- Price: Monthly rent (number)
- Size: Square meters (number)
- Zone: Neighborhood name
- Rooms: Room count
- Floor: Floor info
- Condo fees: If available
- Score: Calculated quick score
- Investment Status: "Hot", "Review", "Watch", or "Skip"
- Source: Portal name
- Scan Date: Current date
- Notes: Mini-report with key data summary

### Step 7: Report Summary

After completing scan, provide summary with total listings scanned per portal, duplicates skipped, listings saved (by status), listings skipped (with reason counts).

## Error Handling

If portal blocks access or shows captcha: pause 30 seconds, retry once, skip to next portal if still blocked.

If ~~project tracker write fails: log listing data locally, continue with remaining listings, report failed writes in summary.

## Usage Examples

- "Scan Milan portals for bilocali under 1,300 EUR"
- "Find apartments in Navigli and Isola only"
- "Search Immobiliare and Idealista for 2-room apartments, 50-60 m2, max 1,200 EUR rent, Porta Romana area"
