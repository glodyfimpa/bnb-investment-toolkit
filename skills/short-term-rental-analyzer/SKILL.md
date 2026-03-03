---
name: short-term-rental-analyzer
description: |
  Analyze short-term rental investment opportunities by evaluating specific zones within a city and calculating detailed business plans with ROI projections. Use this skill when evaluating apartments for Airbnb or similar platforms, deciding which neighborhoods to invest in, or determining if rental economics make sense. Triggers include: "analyze zone for short-term rentals", "calculate ROI for Airbnb apartment", "is this neighborhood good for rentals", "create business plan", or providing apartment details with location and costs. Currently optimized for Italian cities with InsideAirbnb data, expandable to other markets.
version: 0.1.0
---

# Short-Term Rental Analyzer

Evaluate investment opportunities for short-term rental properties using real market data and financial projections. Combines zone analysis with detailed business planning to support go/no-go decisions.

## Core Workflow

Collect property details from the user. Pull market data, calculate financial projections, generate business plan spreadsheet, provide recommendation based on three key thresholds.

### Step 1: Market Analysis

Run `${CLAUDE_PLUGIN_ROOT}/skills/short-term-rental-analyzer/scripts/market_analyzer.py` to pull real data from InsideAirbnb for the target zone:

```python
from scripts.market_analyzer import MarketAnalyzer

analyzer = MarketAnalyzer(city="milan")
analyzer.load_data()
result = analyzer.analyze_zone("Navigli", bedrooms=2)
```

Output includes average nightly rate, median rate, estimated occupancy percentage, total competitor count, property type distribution, price ranges from 25th to 90th percentile.

### Step 2: Business Plan Calculation

Feed market data into `${CLAUDE_PLUGIN_ROOT}/skills/short-term-rental-analyzer/scripts/business_plan_calculator.py` along with cost structure:

```python
from scripts.business_plan_calculator import BusinessPlanCalculator, PropertyCosts, MarketData

costs = PropertyCosts(
    monthly_rent=1200,
    condo_fees=150,
    utilities=80,
    wifi=30,
    cleaning_per_stay=60,
    supplies=50,
    insurance=40,
    property_mgmt_percent=0.10
)

market = MarketData(
    avg_price_per_night=85,
    occupancy_rate=0.70
)

calculator = BusinessPlanCalculator(costs, market)  # defaults to 3% split-fee commission
projection = calculator.calculate_monthly_projection()
recommendation = calculator.generate_decision_recommendation()
```

Calculator applies Italian tax structure. Cedolare secca at 21% is applied to gross rental income (net of platform commission). Operating expenses are NOT deductible under cedolare secca. Platform commission defaults to 3% (split-fee model for individual hosts); use `commission_rate=0.155` for hosts with PMS or host-only pricing.

The recommendation engine scores properties against three thresholds:

| Metric | Minimum | Optimal |
|--------|---------|---------|
| Break-even | ≤ 10 days | ≤ 8 days |
| ROI (profit/total costs) | ≥ 40% | ≥ 60% |
| Revenue-to-Rent Ratio | ≥ 2.5x | ≥ 3x |

Properties must meet ALL THREE minimum criteria for GO recommendation.

### Step 3: Excel Business Plan Generation

Create formatted spreadsheet using the template script:

```python
from scripts.create_template import create_business_plan_template
template_path = create_business_plan_template()
```

Template includes three sheets: Inputs (editable parameters), Calculations (formulas), Summary (key metrics with pass/fail indicators). Users can modify input values directly in Excel to run scenario analyses.

### Step 4: Present Findings

Combine market analysis with business plan projections into a recommendation report. Include zone competitiveness assessment, pricing positioning, monthly financial breakdown, sensitivity analysis for occupancy variations, final go/no-go recommendation with rationale.

## Commission Models

**Split fee (default):** Individual hosts without PMS. Host pays ~3%, guest pays ~14% separately.

```python
calculator = BusinessPlanCalculator(costs, market)  # defaults to 3%
```

**Host-only fee:** Hosts with PMS or host-only pricing. Host pays 15.5%, guest pays nothing. Mandatory for PMS-connected hosts since October 2025.

```python
calculator = BusinessPlanCalculator(costs, market, commission_rate=0.155)
```

## Italian Tax Rules (Cedolare Secca)

| Properties | Tax Treatment |
|------------|---------------|
| 1st property | 21% cedolare secca (flat tax) |
| 2nd property | 26% on lower-earning, 21% on higher-earning |
| 3+ properties | Requires P.IVA, different tax regime |

Pass `tax_rate=0.26` for second property evaluation. For 3+ properties, consult a commercialista.

## Key Assumptions

- Average booking stay length: 3 nights
- Airbnb commission: 3% split-fee (default) or 15.5% host-only (configurable)
- Tax rate: 21% cedolare secca on gross rental income (configurable)
- Monthly occupancy calculated from 30-day period
- Cleaning occurs once per stay, not per night

## Expanding to New Cities

Add city URLs from http://insideairbnb.com/get-the-data/ to the `CITY_DATA_URLS` dictionary in `market_analyzer.py`. Adjust tax rates for non-Italian markets.

## Scripts Reference

- `scripts/market_analyzer.py` - Downloads InsideAirbnb data, filters by zone and property type, calculates occupancy and price statistics
- `scripts/business_plan_calculator.py` - Financial projections, tax/commission rates, scenario analyses, go/no-go recommendations
- `scripts/create_template.py` - Excel template with linked sheets, formatted headers, currency formatting, decision indicators
