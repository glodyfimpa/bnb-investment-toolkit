# Portal Navigation Guide

Instructions for extracting rental listings from Italian real estate portals.

## Immobiliare.it

**Base URL for Milan rentals:**

```
https://www.immobiliare.it/affitto-case/milano/
```

**Filter parameters:**
- `criterio=rilevanza` - Sort by relevance
- `prezzoMinimo=X` - Minimum price
- `prezzoMassimo=X` - Maximum price
- `superficieMinima=X` - Minimum sqm
- `superficieMassima=X` - Maximum sqm
- `locpiualiMin=2` - Minimum rooms (2 = bilocale)
- `locpiualiMax=2` - Maximum rooms
- `contratto=libero` - Contract type 4+4 (canone libero)

**Data extraction from listing page:**
- Price: Look for element with class `in-price__price` or similar price container
- Address: Title usually contains street and neighborhood
- Size: Look for `m2` or `mq` values in features section
- Rooms: Look for `locali` count
- Floor: Look for `piano` in features (e.g., "Piano terra", "1", "2 su 5")
- Elevator: Look for `ascensore` - if floor > 0 and no elevator, SKIP listing
- Contract type: Look for `tipologia contratto` - accept only "4+4" or "Libero", skip "Transitorio", "Uso foresteria", "3+2"
- Condo fees: Look for `spese condominio` or `spese condominiali`
- Energy class: Look for `classe energetica` badge

**Listing URL pattern:**

```
https://www.immobiliare.it/annunci/[ID]/
```

## Idealista

**Base URL for Milan rentals:**

```
https://www.idealista.it/affitto-case/milano-milano/
```

**Filter parameters (URL path based):**
- `con-prezzo-fino_X` - Maximum price
- `con-prezzo-da_X` - Minimum price
- `con-dimensione-da_X` - Minimum sqm
- `con-dimensione-fino_X` - Maximum sqm
- `2-locali/` - Bilocale filter

**Data extraction from listing page:**
- Price: Element with `info-data-price` or price span
- Address: In listing title and location section
- Size: Look for `m2` value
- Rooms: Listed in features as `habitaciones` or `locali`
- Floor: Look for `planta` or `piano`
- Elevator: Look for `ascensor` or `ascensore` in features
- Contract type: Look in listing details for "Tipo contratto"
- Condo fees: May appear in expenses section
- Energy class: Energy certificate section

**Listing URL pattern:**

```
https://www.idealista.it/immobile/[ID]/
```

## Casa.it

**Base URL for Milan rentals:**

```
https://www.casa.it/affitto/residenziale/milano/
```

Use the site's filter interface to set parameters, then work with filtered results.

## Deduplication Logic

Before saving any listing, check for duplicates:

1. **Primary match**: Normalize address (lowercase, remove punctuation, standardize abbreviations like "via" vs "v.") and compare
2. **Secondary confirmation**: If addresses match, verify with sqm (+/-5 tolerance) and price (+/-50 EUR tolerance)
3. **URL check**: Extract listing ID from URL and check against already-saved URLs

Address normalization examples:
- "Via Savona, 25" -> "via savona 25"
- "V. Savona 25" -> "via savona 25"
- "Corso Buenos Aires, 35/A" -> "corso buenos aires 35a"

## Zone Filtering (Milan Defaults)

**Priority zones (centro storico):**
Duomo, Brera, Quadrilatero, Magenta, Porta Venezia

**High-demand zones:**
Navigli, Isola, Centrale, Buenos Aires, Porta Romana, Ticinese, Sempione, Garibaldi

**Strategic extensions:**
Citta Studi, Lambrate, Lodi-Brenta, Loreto, Turro

**Exclude:**
Rogoredo, Bisceglie, Baggio, Quarto Oggiaro, extreme periphery

These zones are Milan-specific defaults. Override with user-specified zones for other cities.

## Contract Type Filtering

**REQUIRED: Only accept 4+4 contracts (canone libero)**

Accept: "4+4", "Libero", "Canone libero"
Skip: "Transitorio", "Uso foresteria", "3+2", "Concordato", "Studenti"

When contract type is not specified, check detail page. If still unclear, save with null contract type and flag for manual review.

## Floor and Elevator Filtering

Ground floor ("Piano terra", "Piano rialzato", "T", "R") does not require elevator.
Upper floors ("1", "2", "3", etc.) REQUIRE elevator.

BnB guests arrive with luggage. Walking up stairs significantly impacts reviews and booking rates.

## Subletting Restrictions Detection

**CRITICAL: SKIP any listing that prohibits subletting or short-term rentals**

Scan the entire listing text for these keywords (case-insensitive):

- "no sublocazione" / "vietata sublocazione"
- "no subaffitto" / "vietato subaffitto"
- "no affitti brevi" / "affitti brevi non ammessi"
- "no Airbnb" / "vietato Airbnb"
- "no B&B" / "no BnB" / "vietato uso B&B"
- "solo residenziale" / "uso esclusivamente residenziale"
- "no attivita ricettiva" / "vietata attivita ricettiva"
- "divieto di sublocazione"
- "no locazione turistica"

Also check for condominium rules, owner restrictions, and contract clauses mentioning these restrictions.

If ANY phrase detected: SKIP listing immediately, do not save.
