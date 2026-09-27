"""
Digital Heritage Archive - Smart Search View
Combines keyword indexing with FAISS dense semantic embeddings
for intelligent discovery of ancient manuscripts, edicts, and charters.
"""

import streamlit as st
from config import ARCHIVAL_ERAS, ARCHIVAL_CATEGORIES
from core.search_engine import HybridSearchEngine


def render_smart_search():
    st.markdown("## 🔍 Smart Hybrid & Semantic Search")
    st.markdown(
        "Search through centuries of historical records using exact keywords, names, or abstract cultural and legal concepts."
    )

    # Search Bar and Filters
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input(
            "Search Query",
            placeholder="e.g. 'Religious harmony and tolerance', 'Chola land grant', 'Akbar Sulh-i-Kul', 'Freedom struggle'",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("🔎 Search Archive", use_container_width=True)

    with st.expander("🎯 Faceted Filters & Search Controls", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            era_filter = st.selectbox("Filter by Era", ["All"] + ARCHIVAL_ERAS)
        with fcol2:
            cat_filter = st.selectbox("Filter by Category", ["All"] + ARCHIVAL_CATEGORIES)
        with fcol3:
            top_k = st.slider("Max Results", min_value=3, max_value=20, value=8)

    if query or search_clicked:
        if not query.strip():
            st.info("Please enter a query term or concept.")
            return

        engine = HybridSearchEngine()
        with st.spinner("Searching SQLite catalog & FAISS vector embeddings..."):
            results = engine.hybrid_search(
                query=query,
                era_filter=era_filter,
                category_filter=cat_filter,
                top_k=top_k,
            )

        st.markdown(f"### Found {len(results)} Matching Archival Records")

        if not results:
            st.warning("No records matched your search query. Try broader keywords or clearing filters.")
            return

        for doc in results:
            score = doc.get("semantic_score", 0.0)
            match_type = doc.get("match_type", "Hybrid")
            snippet = doc.get("cleaned_text") or doc.get("extracted_text") or ""
            if len(snippet) > 280:
                snippet = snippet[:280] + "..."

            st.markdown(
                f"""
                <div class="heritage-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #fbbf24;">{doc.get('title')}</h4>
                        <span class="heritage-badge">⚡ Match: {match_type} (Score: {score:.2f})</span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span class="heritage-badge">🏛️ {doc.get('era')}</span>
                        <span class="heritage-badge">🏷️ {doc.get('category')}</span>
                        <span class="heritage-badge">📍 {doc.get('origin_region', 'India')}</span>
                        <span class="heritage-badge">📅 {doc.get('approx_year', 'N/A')}</span>
                        <span class="heritage-badge">🆔 {doc.get('accession_number')}</span>
                    </div>
                    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin: 0;">
                        "{snippet}"
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
