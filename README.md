# BnB Investment Toolkit

Analyze and scout short-term rental investment opportunities in Italy. Combines market data analysis, automated property scouting from rental portals, ROI projections, and business plan generation.

## Components

### Skills

**short-term-rental-analyzer** - Evaluate zones using InsideAirbnb market data. Calculate financial projections with Italian tax rules (cedolare secca). Generate Excel business plans with scenario analysis. Go/no-go recommendations based on break-even, ROI, and revenue-to-rent thresholds.

**property-acquisition-tracker** - Automated scouting from Immobiliare.it, Idealista, and Casa.it. Filters by contract type, elevator, subletting restrictions, zone, price, and size. Deduplicates across portals. Scores listings and saves qualified properties to your project tracker.

### Commands

- `/scan-apartments [city] [max-price]` - Scan rental portals for investment-grade apartments
- `/analyze-zone [zone-name] [city]` - Analyze a neighborhood for short-term rental potential
- `/business-plan [rent] [zone]` - Generate a full business plan with ROI projections

## Setup

1. Install the plugin
2. Connect a project tracker (Notion, Airtable, or similar) for saving scouted properties
3. Ensure browser access for portal scanning

### Project Tracker Database Schema

If using Notion or similar, create a database with these fields:

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

## Market Coverage

Currently optimized for Italian cities using InsideAirbnb data. Milan zones are pre-configured with average nightly rates. Expandable to other cities by adding InsideAirbnb URLs in the market analyzer script.

## Italian Tax Rules

The calculator applies cedolare secca (flat tax on gross rental income): 21% for first property, 26% for second. Operating expenses are not deductible under this regime. For 3+ properties, a P.IVA (business registration) is required with a different tax structure.

## Decision Criteria

All three thresholds must be met for a GO recommendation:

| Metric | Minimum | Optimal |
|--------|---------|---------|
| Break-even | <= 10 days/month | <= 8 days/month |
| ROI | >= 40% annual | >= 60% annual |
| Revenue-to-Rent Ratio | >= 2.5x | >= 3x |
