---
description: Generate a full business plan for a specific apartment
argument-hint: [rent] [zone]
---

Generate a complete business plan with ROI projections for a specific apartment investment.

Load the short-term-rental-analyzer skill from this plugin. Use it to run the full business plan workflow.

Collect these inputs from the user (ask for anything not provided):
- Monthly rent (EUR)
- Condo fees (EUR, default: 0)
- Zone/neighborhood name
- City (default: Milan)
- Number of bedrooms (default: 2)
- Commission model: split-fee 3% (default) or host-only 15.5%
- Tax rate: 21% first property (default) or 26% second property

Execute these steps:
1. Run market analysis for the zone to get real occupancy and pricing data
2. Calculate full business plan projection using business_plan_calculator.py
3. Run scenario analysis at 80%, 100%, and 120% of base occupancy
4. Generate go/no-go recommendation against the three decision thresholds (break-even, ROI, revenue-to-rent ratio)
5. Create Excel business plan spreadsheet using create_template.py
6. Present findings with monthly breakdown, annual projections, and clear recommendation

The final output must include: monthly net profit, annual ROI, break-even nights, revenue-to-rent ratio, confidence level, and the generated Excel file for the user to download.
