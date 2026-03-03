---
description: Analyze a city zone for short-term rental potential
argument-hint: [zone-name] [city]
---

Analyze a specific neighborhood for short-term rental investment potential using real market data.

Load the short-term-rental-analyzer skill from this plugin. Use it to run market analysis on the specified zone.

Parse arguments:
- First argument: zone/neighborhood name (required - ask if not provided)
- Second argument: city (default: Milan)

Execute these steps:
1. Run market_analyzer.py for the zone: download InsideAirbnb data, filter by zone and bedrooms (default: 2), calculate occupancy and pricing stats
2. Present zone analysis: average nightly rate, median rate, occupancy rate, competitor count, price percentiles (25th-90th)
3. Compare against scoring thresholds from the property-acquisition-tracker skill references
4. Provide a zone attractiveness assessment: is this zone worth targeting for investment?

Format output as a concise report with the key numbers and a clear verdict on zone viability.
