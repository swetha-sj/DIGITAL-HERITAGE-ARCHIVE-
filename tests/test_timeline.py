"""
Unit and Integration tests for Interactive Heritage Timeline.
Tests:
1. Year/Date parsing into continuous timeline numbers (BCE & CE).
2. Thematic classification into Life, Writings, Speeches, Constitution, Legacy.
3. Chronological sorting by continuous year.
4. Category filtering for All, Life, Writings, Speeches, Constitution, Legacy.
5. Display hierarchy verification (Year -> Event -> Title -> Short Description -> View Document -> View Source).
6. Plotly interactive visual chart generation.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.timeline_builder import (
    TimelineBuilder,
    TIMELINE_CATEGORIES,
    CATEGORY_ICONS,
    CATEGORY_COLORS,
)
from utils.sample_loader import bootstrap_sample_data


def test_timeline_pipeline():
    print("--- 1. Testing Sample Data Bootstrap & Synchronization ---")
    total_docs = bootstrap_sample_data()
    assert total_docs > 0, "There must be cataloged archival documents."
    print(f"[OK] Total archival records in catalog: {total_docs}")

    print("\n--- 2. Testing Chronological Year Parsing ---")
    assert TimelineBuilder.parse_chronological_year("300 BCE") == -300.0
    assert TimelineBuilder.parse_chronological_year("257 BCE") == -257.0
    assert TimelineBuilder.parse_chronological_year("375 CE") == 375.0
    assert TimelineBuilder.parse_chronological_year("1010 CE") == 1010.0
    assert TimelineBuilder.parse_chronological_year("1582 CE") == 1582.0
    assert TimelineBuilder.parse_chronological_year("1942") == 1942.0
    assert TimelineBuilder.parse_chronological_year("1949 CE") == 1949.0
    print("[OK] Chronological parsing verified for negative BCE and positive CE eras.")

    print("\n--- 3. Testing Category Classification (Life, Writings, Speeches, Constitution, Legacy) ---")
    sample_ashoka = {"title": "Major Rock Edict XII of Ashoka", "topic": "Speeches", "description": "Speech on harmony"}
    sample_akbar = {"title": "Imperial Farman of Emperor Akbar on Sulh-i-Kul", "topic": "Royal Decrees", "description": "Farman"}
    sample_kautilya = {"title": "Kautilya's Arthashastra", "topic": "Treatises", "description": "Manuscript treatise"}
    sample_samudragupta = {"title": "Samudragupta Allahabad Pillar Inscription", "topic": "Dynasties", "description": "Accession & reign"}
    sample_chola = {"title": "Thanjavur Brihadisvara Temple Copper Plate Grant", "topic": "Temple Endowments", "description": "Endowment"}

    assert TimelineBuilder.classify_category(sample_ashoka) == "Speeches"
    assert TimelineBuilder.classify_category(sample_akbar) == "Constitution"
    assert TimelineBuilder.classify_category(sample_kautilya) == "Writings"
    assert TimelineBuilder.classify_category(sample_samudragupta) == "Life"
    assert TimelineBuilder.classify_category(sample_chola) == "Legacy"
    print("[OK] Automatic category classification verified across all 5 themes.")

    print("\n--- 4. Testing Filtering by All 6 Timeline Categories ---")
    for cat in TIMELINE_CATEGORIES:
        records = TimelineBuilder.get_timeline_records(category_filter=cat)
        assert isinstance(records, list), f"Records for {cat} must be a list"
        print(f"     Category '{cat}' ({CATEGORY_ICONS.get(cat, '📜')}): {len(records)} records found.")
        if cat != "All":
            for r in records:
                assert r["category"] == cat, f"Record category must match filter {cat}"

    print("\n--- 5. Testing Display Hierarchy Fields ---")
    all_records = TimelineBuilder.get_timeline_records(category_filter="All")
    assert len(all_records) > 0, "All records must not be empty"

    # Verify chronological sorting
    plot_years = [r["plot_year"] for r in all_records]
    assert plot_years == sorted(plot_years), "Timeline items must be strictly sorted by chronological plot_year"
    print(f"[OK] Chronological ordering verified from earliest ({all_records[0]['year']}) to latest ({all_records[-1]['year']}).")

    # Verify all 6 display hierarchy components
    for idx, r in enumerate(all_records[:3], start=1):
        assert "year" in r and r["year"], "Must display Year"
        assert "historical_event" in r and r["historical_event"], "Must display Historical Event / Record"
        assert "title" in r and r["title"], "Must display Title"
        assert "short_description" in r and r["short_description"], "Must display Short Description"
        assert "record_id" in r, "Must have ID for View Document"
        assert "accession_number" in r, "Must have Accession for View Source"
        assert "institution" in r, "Must have Institution for View Source"
        print(f"     [Card {idx}] Year: {r['year']} | Event: {r['historical_event'][:35]}... | Title: {r['title'][:30]}...")

    print("\n--- 6. Testing Plotly Timeline Graph Generation ---")
    fig = TimelineBuilder.build_plotly_timeline(all_records, selected_category="All")
    assert fig is not None, "Plotly figure should be successfully generated"
    assert len(fig.data) > 0, "Figure must contain plot data traces"
    print("[OK] Interactive Plotly Visual Timeline generated successfully.")

    print("\n[SUCCESS] ALL INTERACTIVE HERITAGE TIMELINE TESTS PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    test_timeline_pipeline()
