# Investment Scoring Criteria

Evaluation thresholds for short-term rental investments. Properties must meet ALL minimum criteria for GO recommendation.

## Decision Thresholds

| Metric | Minimum | Optimal |
|--------|---------|---------|
| Break-even | <= 10 days | <= 8 days |
| ROI (profit/total costs) | >= 40% | >= 60% |
| Revenue-to-Rent Ratio | >= 2.5x | >= 3x |

## Scoring Formulas

**Break-even days:**

```
monthly_costs = rent + condo_fees + utilities + wifi + insurance + (cleaning x stays_per_month) + maintenance_monthly
break_even_days = monthly_costs / net_daily_rate
net_daily_rate = avg_nightly_rate x (1 - airbnb_commission) x (1 - tax_rate)
```

**ROI:**

```
annual_revenue = avg_nightly_rate x occupied_nights_per_year x (1 - airbnb_commission)
annual_costs = (rent + condo_fees) x 12 + utilities_annual + cleaning_annual + maintenance + insurance_annual
annual_profit = annual_revenue x (1 - tax_rate) - annual_costs
roi = annual_profit / annual_costs
```

**Revenue-to-Rent Ratio:**

```
monthly_gross_revenue = avg_nightly_rate x occupied_nights_per_month
ratio = monthly_gross_revenue / monthly_rent
```

## Cost Parameters (Italy 2025-2026)

| Item | Default Value |
|------|---------------|
| Cleaning fee | 50 EUR/stay |
| Airbnb commission | 3% (split-fee) or 15.5% (host-only) |
| Utilities | 4 EUR/night occupied |
| Maintenance | 500 EUR/year |
| Cedolare secca | 21% (1st property), 26% (2nd) |
| Average stay length | 3 nights |
| Target occupancy | 67% (20 days/month) |

Adjust these values for your specific market and circumstances.

## Quick Score (Rapid Filtering)

For rapid filtering without full calculation:

```
estimated_revenue = zone_avg_nightly_rate x 20 days (67% occupancy)
quick_score = estimated_revenue / total_monthly_cost x 10
```

Where `total_monthly_cost = rent + condo_fees`

Interpretation:
- Score >= 30: High potential ("Hot")
- Score 25-29: Moderate potential ("Review")
- Score 20-24: Worth monitoring ("Watch")
- Score < 20: Skip unless exceptional location

## Zone Average Rates (Milan 2026, bilocale 4 guests)

| Zone | Range | Midpoint |
|------|-------|----------|
| Centro storico/Brera/Duomo | 130-200 EUR/night | 155 EUR |
| Navigli/Isola/Garibaldi | 100-160 EUR/night | 125 EUR |
| Porta Romana/Buenos Aires/Porta Venezia | 90-140 EUR/night | 110 EUR |
| Citta Studi/Lambrate/Nolo | 65-110 EUR/night | 85 EUR |

These rates are Milan-specific. For other cities, pull fresh data using the short-term-rental-analyzer skill or check InsideAirbnb.

## Default Property Requirements

- Type: Bilocale (2 locali)
- Size: 50-65 m2
- Capacity: 4 guests (1 bedroom + sofa-bed)
- Budget: Target 1,300 EUR/month total, max 1,500 EUR
- Contract: 4+4 (canone libero) ONLY
- Elevator: Required for floors above ground level
- Subletting: SKIP if prohibited

All parameters are user-overridable.
