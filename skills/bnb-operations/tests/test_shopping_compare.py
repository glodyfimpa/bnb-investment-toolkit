"""Tests for shopping_compare.py — comparing an Amazon candidate against the Notion Shopping List.

The module's job: given a freshly-researched Amazon candidate and the current
Shopping List items (read from Notion via MCP and passed as plain dicts), decide
- whether the candidate matches an existing list item (so we update, not duplicate),
- whether the candidate is worth buying versus what's already tracked,
- and produce a structured verdict the skill can act on without re-deriving logic.

These are behavioural tests: they pin WHAT the function decides, not how. The
matching is intentionally fuzzy (titles vary between Amazon and the list) but
must never silently merge two genuinely different items.
"""

import sys
from pathlib import Path

import pytest

# The script lives one directory up, under scripts/. Add it to the path so the
# test can import it whether run from the repo root or the skill folder.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import shopping_compare as sc  # noqa: E402


# --- price normalisation -------------------------------------------------

def test_parse_price_handles_italian_format():
    # Amazon.it shows "19,99 €" — comma decimal, euro suffix.
    assert sc.parse_price("19,99 €") == pytest.approx(19.99)


def test_parse_price_handles_thousands_separator():
    # "1.299,00 €" is 1299 euros, not 1.299.
    assert sc.parse_price("1.299,00 €") == pytest.approx(1299.00)


def test_parse_price_returns_none_for_missing():
    assert sc.parse_price("") is None
    assert sc.parse_price(None) is None


# --- matching candidate to an existing list item -------------------------

def test_match_finds_item_by_shared_keywords():
    items = [
        {"Voce": "Cuscini decorativi divano", "Modello": "Topfinel", "Prezzo EUR": 18.99},
        {"Voce": "Tovaglioli di stoffa", "Modello": "Utopia", "Prezzo EUR": 17.99},
    ]
    candidate = {"title": "Topfinel set 4 cuscini decorativi 45x45", "price": "21,99 €"}
    match = sc.find_match(candidate, items)
    assert match is not None
    assert match["Voce"] == "Cuscini decorativi divano"


def test_match_returns_none_when_no_item_is_similar():
    items = [{"Voce": "Asciugacapelli", "Modello": "", "Prezzo EUR": 0}]
    candidate = {"title": "Set 6 bicchieri da vino in cristallo", "price": "24,90 €"}
    assert sc.find_match(candidate, items) is None


def test_match_does_not_merge_different_items_sharing_one_word():
    # "porta" appears in both but they are unrelated objects.
    items = [{"Voce": "Porta asciugamani da bagno", "Modello": "", "Prezzo EUR": 12.0}]
    candidate = {"title": "Porta sapone in ceramica bianca", "price": "8,99 €"}
    assert sc.find_match(candidate, items) is None


# --- verdict -------------------------------------------------------------

def test_verdict_flags_new_item_when_no_match():
    items = [{"Voce": "Tovaglioli", "Modello": "Utopia", "Prezzo EUR": 17.99}]
    candidate = {"title": "Tappetino antiscivolo doccia", "price": "13,50 €"}
    verdict = sc.compare(candidate, items)
    assert verdict["action"] == "add_new"
    assert verdict["matched_voce"] is None


def test_verdict_flags_cheaper_when_candidate_beats_tracked_price():
    items = [{"Voce": "Cuscini decorativi", "Modello": "Topfinel", "Prezzo EUR": 25.00}]
    candidate = {"title": "Topfinel cuscini decorativi set", "price": "18,99 €"}
    verdict = sc.compare(candidate, items)
    assert verdict["action"] == "update_cheaper"
    assert verdict["matched_voce"] == "Cuscini decorativi"
    assert verdict["delta_eur"] == pytest.approx(-6.01)


def test_verdict_flags_already_tracked_when_not_cheaper():
    items = [{"Voce": "Cuscini decorativi", "Modello": "Topfinel", "Prezzo EUR": 18.99}]
    candidate = {"title": "Topfinel cuscini decorativi", "price": "21,99 €"}
    verdict = sc.compare(candidate, items)
    assert verdict["action"] == "already_tracked"
    assert verdict["matched_voce"] == "Cuscini decorativi"


def test_verdict_skips_items_already_bought():
    # An item marked "Comprato" should not be proposed again as a buy.
    items = [{"Voce": "Cuscini decorativi", "Modello": "Topfinel",
              "Prezzo EUR": 18.99, "Stato": "Comprato"}]
    candidate = {"title": "Topfinel cuscini decorativi", "price": "16,00 €"}
    verdict = sc.compare(candidate, items)
    assert verdict["action"] == "already_bought"


# --- CLI -----------------------------------------------------------------

def test_cli_compares_candidate_against_list_file(tmp_path, capsys):
    # The CLI reads a JSON file {"candidate": {...}, "items": [...]} and prints
    # the verdict as JSON, so the workflow can shell out to it if it prefers.
    import json
    payload = {
        "candidate": {"title": "Topfinel cuscini decorativi", "price": "18,99 €"},
        "items": [{"Voce": "Cuscini decorativi", "Modello": "Topfinel", "Prezzo EUR": 25.00}],
    }
    f = tmp_path / "in.json"
    f.write_text(json.dumps(payload), encoding="utf-8")
    rc = sc.main([str(f)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["action"] == "update_cheaper"
