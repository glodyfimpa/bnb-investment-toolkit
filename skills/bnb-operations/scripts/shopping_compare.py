#!/usr/bin/env python3
"""Compare an Amazon candidate against the current Notion Shopping List.

Why this exists: when researching a BnB purchase on Amazon, the slow, error-prone
step is reconciling the candidate with what's already tracked in the Shopping List
on Notion. Done by eye it produces duplicate rows ("Cuscini" added twice with
different wording) and missed savings (a cheaper option ignored because the price
wasn't compared). This module makes that reconciliation deterministic so the skill
can act on a verdict instead of re-judging each time.

It is a pure function of its inputs. It does NOT talk to Notion or Amazon: the
candidate comes from the researcher's browser step, the list items come from
Claude reading the Notion DB via MCP. The Notion DB stays the single source of
truth — see memory `feedback_bnb_acquisti_source_of_truth`.

Candidate shape:   {"title": str, "price": str (Amazon.it format), "url": str?}
List item shape:   {"Voce": str, "Modello": str, "Prezzo EUR": float, "Stato": str?}
                   (same keys as the Notion data source used by generate_dashboard.py)
"""

from __future__ import annotations

import re
import unicodedata

# Words too generic to carry matching signal: matching on them alone would merge
# "porta asciugamani" with "porta sapone". Tuned for Italian household items.
_STOPWORDS = {
    "di", "da", "del", "della", "dei", "delle", "in", "con", "per", "il", "la",
    "lo", "le", "gli", "un", "una", "set", "kit", "the", "and", "of", "x",
    "pz", "pezzi", "cm", "ml", "porta", "casa", "bnb",
}

# A candidate must share at least this many meaningful keywords with a list item
# to count as the same thing. One shared significant word is too weak.
_MIN_SHARED_KEYWORDS = 2


def parse_price(raw):
    """Parse an Amazon.it price string ("1.299,00 €") into a float.

    Italian convention: '.' groups thousands, ',' is the decimal separator.
    Returns None when there's nothing to parse, so callers can distinguish
    "free / not priced" from "priced at zero".
    """
    if not raw:
        return None
    cleaned = str(raw).replace("€", "").strip()
    cleaned = re.sub(r"[^0-9.,]", "", cleaned)
    if not cleaned:
        return None
    # Drop thousands dots, then turn the decimal comma into a dot.
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _keywords(text):
    """Lowercase, strip accents, split into meaningful keyword set."""
    if not text:
        return set()
    norm = unicodedata.normalize("NFKD", str(text))
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    tokens = re.findall(r"[a-z0-9]+", norm.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 1}


def find_match(candidate, items):
    """Return the list item the candidate most plausibly refers to, or None.

    Scores each item by keyword overlap with the candidate title (and the item's
    Modello, since the model name — "Topfinel" — is often the strongest signal).
    Requires _MIN_SHARED_KEYWORDS overlap to avoid merging unrelated items that
    happen to share a single word.
    """
    cand_kw = _keywords(candidate.get("title"))
    if not cand_kw:
        return None

    best_item = None
    best_score = 0
    for item in items:
        item_kw = _keywords(item.get("Voce")) | _keywords(item.get("Modello"))
        shared = cand_kw & item_kw
        if len(shared) >= _MIN_SHARED_KEYWORDS and len(shared) > best_score:
            best_score = len(shared)
            best_item = item
    return best_item


def compare(candidate, items):
    """Produce a verdict for what to do with this candidate.

    Returns a dict the skill acts on directly:
        action: one of
            "add_new"        — no match in the list, propose adding it
            "already_bought" — matches an item already marked Comprato, skip
            "update_cheaper" — matches a tracked item AND beats its price
            "already_tracked"— matches a tracked item but isn't cheaper
        matched_voce: the "Voce" of the matched item, or None
        delta_eur: candidate price minus tracked price (negative = cheaper),
                   present only when both prices are known
    """
    match = find_match(candidate, items)
    if match is None:
        return {"action": "add_new", "matched_voce": None}

    voce = match.get("Voce")

    if (match.get("Stato") or "").strip().lower() == "comprato":
        return {"action": "already_bought", "matched_voce": voce}

    cand_price = parse_price(candidate.get("price"))
    tracked_price = match.get("Prezzo EUR")
    try:
        tracked_price = float(tracked_price) if tracked_price is not None else None
    except (TypeError, ValueError):
        tracked_price = None

    if cand_price is not None and tracked_price not in (None, 0) and cand_price < tracked_price:
        return {
            "action": "update_cheaper",
            "matched_voce": voce,
            "delta_eur": round(cand_price - tracked_price, 2),
        }

    return {"action": "already_tracked", "matched_voce": voce}


def main(argv=None):
    """CLI: read {"candidate": {...}, "items": [...]} from a JSON file, print the verdict.

    Lets the workflow shell out instead of importing, if that's more convenient:
        python3 scripts/shopping_compare.py input.json
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Compare an Amazon candidate against the Shopping List.")
    parser.add_argument("input", help='JSON file: {"candidate": {...}, "items": [...]}')
    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as fh:
        payload = json.load(fh)

    verdict = compare(payload["candidate"], payload.get("items", []))
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
