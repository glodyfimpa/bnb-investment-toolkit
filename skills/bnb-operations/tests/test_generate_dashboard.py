"""Tests for generate_dashboard.py — the read-only acquisti view.

The dashboard is a pure transformation: Shopping List items (read from Notion via
MCP, passed as dicts) in, self-contained HTML out. It holds no state of its own —
no localStorage, no hardcoded decisions — because the Notion DB is the single
source of truth and the HTML is just a regenerated view.

These tests pin the behaviour that matters operationally: spend totals are
recomputed from the data (never trusted from a stale field), zero-priced items
stay in the checklist but out of the spend total, scartato items are excluded
from spend, and the output is parametric (not hardcoded to one apartment).
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_dashboard as gd  # noqa: E402


FIXED_TIME = "03/06/2026 18:00"


def _items():
    return [
        {"Voce": "Cuscini", "Prezzo EUR": 18.99, "Stato": "Da comprare", "Categoria": "Arredo & comfort", "Canale": "Amazon"},
        {"Voce": "Tovaglioli", "Prezzo EUR": 17.99, "Stato": "Comprato", "Categoria": "Arredo & comfort", "Canale": "Amazon"},
        {"Voce": "Estintore", "Prezzo EUR": 35.00, "Stato": "In carrello", "Categoria": "Sicurezza", "Canale": "Amazon"},
        {"Voce": "Asciugacapelli", "Prezzo EUR": 0, "Stato": "Già in loco", "Categoria": "Arredo & comfort", "Canale": "—"},
        {"Voce": "Lampada scartata", "Prezzo EUR": 99.00, "Stato": "Scartato", "Categoria": "Arredo & comfort", "Canale": "IKEA"},
    ]


def test_build_returns_self_contained_html():
    out = gd.build(_items(), FIXED_TIME)
    assert out.lstrip().startswith("<!DOCTYPE html>")
    assert "</html>" in out


def test_no_localstorage_or_client_state():
    # The whole point: the view carries no state. No localStorage, no inline JS state.
    out = gd.build(_items(), FIXED_TIME).lower()
    assert "localstorage" not in out


def test_spend_total_excludes_scartato_and_zero_priced():
    # Spend total = 18.99 + 17.99 + 35.00 = 71.98. The 99€ scartato and the 0€
    # item are excluded from spend. The scartato row still RENDERS in the table
    # (struck through), it just doesn't inflate the spend figure — so we assert
    # the computed total, not the absence of the string.
    out = gd.build(_items(), FIXED_TIME)
    assert "71,98" in out
    # The scartato item is present but marked as such (stato-4 row class).
    assert "Lampada scartata" in out
    assert "stato-4" in out


def test_zero_priced_item_still_in_checklist():
    # Asciugacapelli is 0€ but must still appear as a tracked row.
    out = gd.build(_items(), FIXED_TIME)
    assert "Asciugacapelli" in out


def test_generated_at_is_injected_not_now():
    # build() must take the timestamp as an argument (testable), not call now() itself.
    out = gd.build(_items(), FIXED_TIME)
    assert FIXED_TIME in out


def test_house_name_is_parametric():
    # The view must not be hardcoded to one apartment. A house_name flows into the title.
    out = gd.build(_items(), FIXED_TIME, house_name="Casa Test", source_url="https://example.com/db")
    assert "Casa Test" in out
    assert "https://example.com/db" in out
