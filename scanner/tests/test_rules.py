"""Tester för regelöversättningarna.

Rapporten är produkten. En regel utan svensk text visas som sitt rå-id —
"aria-required-parent" mitt i ett dokument en kund betalat 19 900 kr för. Det
här testet gör att sådana luckor syns direkt i stället för i en kundleverans.
"""

from __future__ import annotations

import pytest

from a11yscan.rules import CUSTOM_RULES, IMPACT_SV, RULES, slå_upp

# De regler som faktiskt förekommit vid skanning av svenska e-handelssajter,
# med antal element vid det tillfället. Listan är hämtad ur skarpa körningar,
# inte gissad. Lägg till nya allteftersom de dyker upp.
SEDDA_I_SKARP_DRIFT = [
    "color-contrast", "link-name", "image-alt", "button-name", "label",
    "select-name", "html-has-lang", "meta-viewport", "region",
    "landmark-one-main", "list", "listitem", "link-in-text-block",
    "nested-interactive", "aria-required-parent", "aria-required-children",
    "aria-allowed-attr", "aria-prohibited-attr", "aria-input-field-name",
    "aria-roles", "aria-valid-attr-value", "aria-hidden-focus",
    "aria-required-attr", "document-title", "frame-title",
    "scrollable-region-focusable", "duplicate-id-active",
]


@pytest.mark.parametrize("regel_id", SEDDA_I_SKARP_DRIFT)
def test_regler_fran_skarp_drift_har_svensk_text(regel_id: str):
    info = slå_upp(regel_id)
    assert info is not None, (
        f"{regel_id} har förekommit på en riktig sajt men saknar svensk text. "
        "Den visas då som sitt rå-id i rapporten."
    )


@pytest.mark.parametrize("regel_id,info", sorted((RULES | CUSTOM_RULES).items()))
def test_varje_regel_ar_fardigskriven(regel_id: str, info):
    """Rubrik, konsekvens och WCAG-referens ska alla vara ifyllda och rimliga."""
    assert info.rubrik and not info.rubrik.startswith(("aria-", "wcag")), (
        f"{regel_id}: rubriken ser ut som ett regel-id"
    )
    assert len(info.konsekvens) > 30, f"{regel_id}: konsekvensen är för kort"
    assert info.konsekvens.rstrip().endswith("."), f"{regel_id}: saknar punkt"
    assert info.wcag[0].isdigit(), f"{regel_id}: WCAG-referensen saknar nummer"
    assert info.wcag.rstrip().endswith(("(A)", "(AA)")), (
        f"{regel_id}: nivån ska vara A eller AA — EN 301 549 kräver inte AAA"
    )


def test_alla_allvarlighetsgrader_har_svensk_benamning():
    for nivå in ("critical", "serious", "moderate", "minor"):
        assert nivå in IMPACT_SV


def test_okand_regel_ger_none():
    assert slå_upp("den-har-finns-inte") is None
