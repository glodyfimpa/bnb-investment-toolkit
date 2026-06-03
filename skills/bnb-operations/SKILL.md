---
name: bnb-operations
description: >-
  Operations toolkit for a short-term rental that is already live (post go-live),
  as opposed to acquiring or evaluating a property. Use this whenever the user is
  running an existing Airbnb/BnB and needs to: research and buy supplies on
  Amazon.it for the apartment (cushions, napkins, kitchenware, safety devices) and
  sync them to the Notion Shopping List without duplicates; write or rewrite the
  public listing copy (title, description, house rules, neighborhood pitch); draft
  guest messages (booking confirmation, self check-in instructions, in-home info
  sheet, check-out reminder, review request) in Italian and English; or generate a
  read-only purchases dashboard from the Notion Shopping List. Trigger on phrases
  like "cerca su Amazon per il BnB", "aggiorna la shopping list", "scrivi
  l'annuncio Airbnb", "messaggio per l'ospite", "istruzioni check-in", "dashboard
  acquisti BnB", "messaggio di benvenuto", "richiesta recensione". This is for
  running a live rental; for deciding whether to buy a property, ROI, or scouting
  listings to acquire, use short-term-rental-analyzer or property-acquisition-tracker
  instead.
---

# BnB Operations

The day-to-day work of running a short-term rental that's already live. Four
distinct jobs, each with its own reference. Read this router, decide which job
the user needs, then open that reference and follow it.

This is operations, not acquisition. The sibling skills in this plugin
(`short-term-rental-analyzer`, `property-acquisition-tracker`) decide *whether to
buy a property*. This skill handles *running the one you have*.

## Pick the job

| User wants to... | Open |
|---|---|
| Find & buy supplies on Amazon.it, update the Shopping List | `references/shopping-researcher.md` |
| Write/rewrite the Airbnb listing copy | `references/listing-copywriter.md` |
| Draft guest messages (check-in, info, check-out, review) | `references/guest-templates.md` (+ `assets/guest-messages-it.md`) |
| Generate the read-only purchases dashboard | `references/acquisti-view.md` |

If the request spans more than one (e.g. "I bought new cushions, update
everything"), do them in order and keep Notion as the source of truth throughout.

## The one rule that ties it together: Notion is the source of truth

Every job here reads from or writes to the project's Notion Shopping List / Daily
Tracker. The recurring failure mode is doing the visible work (recommending a
product, generating a dashboard) and leaving the Notion row stale. Don't. After
any change:

- A purchase decision → the Shopping List row reflects it (price, link, Stato).
- An item bought → `Stato = Comprato`, then regenerate the acquisti view.
- Guest/listing copy → consistent with the apartment's real facts and legal setup.

The HTML dashboard is a regenerated view, never a place to store state. (See the
user's gotchas `feedback_bnb_acquisti_source_of_truth`,
`feedback_bnb_tracker_source_of_truth`.)

## Bundled code

- `scripts/shopping_compare.py` — deterministic verdict comparing an Amazon
  candidate to the Shopping List (add_new / update_cheaper / already_tracked /
  already_bought). Used by the shopping researcher. Tested.
- `scripts/generate_dashboard.py` — pure JSON→HTML transformation for the acquisti
  view, parametric on house name and Notion URL. Tested.

Both have tests in `tests/`. Run them with pytest before relying on changes.

## Italian short-term-rental compliance (applies across jobs)

For an Italian locazione turistica (LT non imprenditoriale), a one-time courtesy
kit at check-in is fine. A recurring personal service (daily breakfast, daily
cleaning, fridge restocking) can reclassify the rental as CAV/B&B, which carries
SUAP/SCIA/insurance obligations. Keep listing copy, guest messages, and the
operational setup consistent with the LT category. When in doubt, surface it to
the user rather than promising a recurring service in writing.
