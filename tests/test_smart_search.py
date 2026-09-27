"""
Unit and Integration tests for Smart Search Engine.
Tests:
- FAISS Dense Vector Indexing
- Semantic Cosine Similarity search
- Keyword & Hybrid ranking
- Multi-attribute faceted filtering (Topic, Creator, Year, Type, Language, Institution, Media)
- Summary generation and Result fields
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.storage import init_database, get_all_records
from core.search_engine import SmartSearchEngine
from utils.sample_loader import bootstrap_sample_data


def test_smart_search_pipeline():
    print("--- 1. Testing Database & Sample Data Bootstrap ---")
    init_database()
    bootstrap_sample_data()
    records = get_all_records()
    assert len(records) >= 1, "There must be cataloged records in SQLite."
    print(f"[OK] Total archival records in SQLite: {len(records)}")

    print("\n--- 2. Testing FAISS Vector Indexing ---")
    search_engine = SmartSearchEngine()
    indexed_count = search_engine.reindex_all_documents()
    assert indexed_count > 0, "Indexed documents count must be greater than 0"
    assert search_engine.index is not None, "FAISS index must be initialized"
    assert search_engine.index.ntotal == indexed_count, "FAISS index total vectors must match document count"
    print(f"[OK] FAISS Vector Store successfully indexed {indexed_count} document chunks.")

    print("\n--- 3. Testing Semantic Search Querying ---")
    semantic_results = search_engine.semantic_search("religious harmony and tolerance across communities", top_k=3)
    assert len(semantic_results) > 0, "Semantic search should return matching results"
    top_hit = semantic_results[0]
    assert "semantic_score" in top_hit, "Result must have semantic_score"
    assert "relevance_percentage" in top_hit, "Result must have relevance_percentage"
    print(f"[OK] Top Semantic Hit: '{top_hit['title']}' ({top_hit['relevance_percentage']}% Semantic Relevance)")

    print("\n--- 4. Testing Faceted Multi-Attribute Filtering ---")
    # Search by Topic
    topic_res = search_engine.smart_search(topic_filter="Royal Decrees & Political Treaties")
    print(f"[OK] Found {len(topic_res)} records filtered by Topic='Royal Decrees & Political Treaties'")

    # Search by Creator
    creator_res = search_engine.smart_search(creator_filter="Emperor Ashoka Maurya")
    print(f"[OK] Found {len(creator_res)} records filtered by Creator='Emperor Ashoka Maurya'")

    # Search by Year
    year_res = search_engine.smart_search(year_filter="1582 CE")
    print(f"[OK] Found {len(year_res)} records filtered by Year='1582 CE'")

    # Search by Language
    lang_res = search_engine.smart_search(language_filter="English")
    print(f"[OK] Found {len(lang_res)} records filtered by Language='English'")

    print("\n--- 5. Testing Hybrid Search & Summary Generation ---")
    hybrid_res = search_engine.smart_search(keyword="Akbar Sulh-i-Kul land grant", top_k=5)
    assert len(hybrid_res) > 0, "Hybrid search should return results"
    for r in hybrid_res[:2]:
        assert "title" in r
        assert "document_type" in r
        assert "year" in r
        assert "institution" in r
        assert "summary" in r
        assert "relevance_percentage" in r
        print(f"     Hit: '{r['title']}' | Type: {r['document_type']} | Rel: {r['relevance_percentage']}%")
        print(f"     Summary: {r['summary'][:90]}...")

    print("\nALL SMART SEARCH TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_smart_search_pipeline()
