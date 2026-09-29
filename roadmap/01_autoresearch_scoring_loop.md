# PRD — Autoresearch scoring loop

**Status:** Planned
**Created:** 2026-04-28
**Owner:** Glody
**Inspired by:** [karpathy/autoresearch](https://github.com/karpathy/autoresearch)

## Problem

The `property-acquisition-tracker` skill scans rental portals and ranks listings via a fixed `quick_score` formula defined in `skills/property-acquisition-tracker/references/scoring.md`. The formula has hand-picked weights and thresholds (Hot ≥30, Review 25-29, Watch 20-24). Nobody knows if those numbers are good. Tuning them by hand means running a scan, eyeballing the top results, guessing a tweak, repeating. Slow, manual, biased.

Karpathy's autoresearch repo describes a pattern that fits this problem: an autonomous overnight loop with a fixed time budget, a single metric, and one editable artifact. The agent iterates, measures, keeps or discards, logs everything. You wake up to a tuned configuration and a log of what worked.

This task adapts that pattern to property scoring.

## Outcome

After running the loop overnight, the user wakes up to:

1. A log of N experiments (target ~50 in 8 hours), each with: changed parameters, metric value, kept/discarded decision, timestamp.
2. A `best_config.json` containing the parameter set that produced the highest metric.
3. A short summary: starting metric value, final metric value, top-3 parameter changes that moved the needle.

Loop must run unattended. No prompts to user mid-run.

## Architecture (Karpathy mapping)

| Karpathy | This task |
|----------|-----------|
| `program.md` (human-edited, agent instructions) | `roadmap/autoresearch/program.md` — describes the loop protocol, what to change, how to measure |
| `train.py` (agent-edited, single experimentable artifact) | `roadmap/autoresearch/scoring_config.py` — extracted parameters of the `quick_score` formula and Hot/Review/Watch thresholds. The agent ONLY edits this file |
| `prepare.py` (fixed setup, dataloader, eval) | `roadmap/autoresearch/runner.py` — runs a scan against a frozen test set, computes the metric, logs result. NOT modified by the agent |
| `val_bpb` (single metric) | `metric_top10_avg_score`: average `quick_score` of the top-10 listings in the frozen test set. Higher is better |
| 5-min budget per experiment | 5-min budget per experiment (wall clock, excluding startup) |

## Files to create

```
roadmap/autoresearch/
├── program.md             # Agent baseline instructions (human-edited)
├── scoring_config.py      # Tunable parameters (agent-edited)
├── runner.py              # Frozen scan + metric calc (do not modify)
├── test_set.json          # Frozen listings dataset for reproducible eval
├── experiments.jsonl      # Append-only log: one line per experiment
└── best_config.json       # Snapshot of best config so far (auto-updated)
```

## What the agent CAN modify

Scope: **A — pesi formula + soglie**.

In `scoring_config.py`, the agent may change:

- The coefficient `20` in `(zone_avg_nightly_rate × 20) / total_monthly_cost × 10` (occupancy proxy)
- The multiplier `10` (scaling factor)
- Hot/Review/Watch thresholds (currently 30/25/20)
- Any new term added to the formula MUST take its inputs from fields already extracted by the skill (price, sqm, zone, rooms, floor, condo fees). No new data sources.

The agent CANNOT:
- Add new portals or zones
- Change the test set
- Touch `runner.py` or the metric definition
- Read or write outside `roadmap/autoresearch/`

## Metric

```
metric = mean(quick_score of top-10 listings, ranked by quick_score, on test_set.json)
```

Why this metric:
- Bounded above (score has a natural ceiling on the test set)
- Vocab-independent equivalent: works regardless of formula structure
- Top-10 because it reflects the practical decision (which apartments to actually contact)

The metric is computed on a **frozen test set** (`test_set.json`, ~200 listings) collected once via the existing skill and stored. Same input every run = comparable across experiments.

## Loop protocol

1. Read current `scoring_config.py`
2. Run `runner.py` → produces baseline metric
3. Propose a change to `scoring_config.py` (one parameter at a time, small step)
4. Run `runner.py` again with new config (5-min budget; for this task probably <5 sec since no training, but keep the budget contract for future heavier metrics)
5. If metric improved: keep change, append `{kept: true, ...}` to `experiments.jsonl`, update `best_config.json`
6. If metric regressed: revert, append `{kept: false, ...}`
7. Repeat for the configured number of iterations or until time budget exhausted

## Acceptance criteria

The task is "done" when ALL of these hold:

- [ ] `roadmap/autoresearch/` contains all 6 files listed above
- [ ] `runner.py` executes end-to-end on `test_set.json` and produces a metric value with a single command (`python runner.py`)
- [ ] `program.md` is self-contained: a fresh Claude/Codex instance can read it and start the loop with no extra context
- [ ] Running the loop for 30 minutes produces ≥10 experiments logged in `experiments.jsonl`, with at least one `kept: true`
- [ ] `best_config.json` is updated when a new best is found
- [ ] A dry-run section in `program.md` documents how to run a single experiment manually before kicking off the autonomous loop (Karpathy's "if the above commands all work ok, your setup is working")

## Out of scope

Explicitly NOT in this task:

- Multi-portal parallel scanning
- Live scraping during the loop (use frozen test set only)
- Telegram/Notion notifications
- Web dashboard
- Integrating `short-term-rental-analyzer` (ROI projection) — that's the natural Phase 2
- Letting the agent modify zones, portals, or extracted fields — that's Phase 3 (scope C in original brainstorm)
- Multi-objective optimization (we optimize one metric)

## Open decisions

| # | Question | Default | Decided |
|---|----------|---------|---------|
| 1 | How is the test set collected? | Run skill once on Milan, save first 200 unique listings to `test_set.json` | open |
| 2 | What's the "small step" for parameter changes? | ±10% of current value, agent's choice within that range | open |
| 3 | Stop condition? | Iteration count (default 50) OR time budget (default 8 hours), whichever first | open |
| 4 | Random seed for tie-breaks? | Yes, document in `runner.py` | open |
| 5 | How to handle agent infinite loops / stuck experiments? | Watchdog: if `runner.py` runs >2× the budget, kill and mark experiment as failed | open |

## Phases

- **Phase 1 (this task):** Scope A — pesi/soglie of `quick_score`
- **Phase 2 (future):** Replace metric with ROI mediano top-10 via integration with `short-term-rental-analyzer`. Requires occupancy estimates per zone.
- **Phase 3 (future):** Scope B/C — let agent propose new zones or new score dimensions

## References

- [karpathy/autoresearch README](https://github.com/karpathy/autoresearch) — original pattern
- `skills/property-acquisition-tracker/SKILL.md` — current skill, Step 5 has the formula
- `skills/property-acquisition-tracker/references/scoring.md` — current parameters
- Conversation context (2026-04-28): Karpathy autoresearch evaluation, defaults chosen B + A
