---
description: Scan rental portals for investment-grade apartments
argument-hint: [city] [max-price]
---

Scan Italian rental portals (Immobiliare.it, Idealista) for apartments matching short-term rental investment criteria.

Load the property-acquisition-tracker skill from this plugin. Use it to execute the full scouting workflow.

If user provides arguments, parse them:
- First argument: city (default: Milan)
- Second argument: max monthly price in EUR (default: 1500)

Ask the user for any additional filter preferences before starting: target zones, size range, minimum rooms.

Execute the 7-step workflow from the skill: configure parameters, navigate portals, extract data, deduplicate, score, save to ~~project tracker, report summary.

Present results as a clean summary table at the end, grouped by investment status (Hot, Review, Watch).
