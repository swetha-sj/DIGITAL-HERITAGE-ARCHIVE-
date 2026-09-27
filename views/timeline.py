"""
Digital Heritage Archive - Interactive Historical Heritage Timeline
Chronological discovery mapping ancient manuscripts, royal decrees, speeches,
and cultural records across millennia.

Display hierarchy per milestone:
Year
↓
Historical Event / Record
↓
Title
↓
Short Description
↓
View Document (Inline Inspector & Full Viewer)
↓
View Source (Dublin Core Metadata & Download)

Filterable by:
- All
- Life
- Writings
- Speeches
- Constitution
- Legacy
"""

import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import textwrap
from core.timeline_builder import (
    TimelineBuilder,
    TIMELINE_CATEGORIES,
    CATEGORY_ICONS,
    CATEGORY_COLORS,
)
from core.storage import get_all_records, get_record_by_id
from core.tts_engine import render_interactive_audio_player


def render_timeline():
    # Page Header
    header_html = textwrap.dedent("""
    <div style="text-align: center; margin-bottom: 22px;">
        <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">
            ⏳ INTERACTIVE HERITAGE TIMELINE
        </h1>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
            Chronological Discovery &bull; Year-Indexed Archival Milestones &bull; Categorical Filter Suite
        </p>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # 1. Fetch all timeline items to compute category counts
    all_items = TimelineBuilder.get_timeline_records(category_filter="All")

    if not all_items:
        st.info("No records to display on timeline yet. Use **Admin** to upload archival materials or load sample data.")
        return

    # Compute category counts
    cat_counts = {cat: 0 for cat in TIMELINE_CATEGORIES}
    cat_counts["All"] = len(all_items)
    for it in all_items:
        c = it.get("category", "Writings")
        if c in cat_counts:
            cat_counts[c] += 1

    # 2. CATEGORY FILTER BAR: All, Life, Writings, Speeches, Constitution, Legacy
    st.markdown("##### 🏛️ Filter Timeline by Archival Theme:")
    
    # Initialize active category in session state
    if "active_timeline_category" not in st.session_state:
        st.session_state["active_timeline_category"] = "All"

    selected_cat = st.session_state["active_timeline_category"]

    # Render category buttons in columns
    cat_cols = st.columns(len(TIMELINE_CATEGORIES))
    for idx, cat_name in enumerate(TIMELINE_CATEGORIES):
        icon = CATEGORY_ICONS.get(cat_name, "📜")
        count = cat_counts.get(cat_name, 0)
        label = f"{icon} {cat_name} ({count})"
        is_active = (selected_cat == cat_name)

        with cat_cols[idx]:
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"cat_filter_btn_{cat_name}", type=btn_type, use_container_width=True):
                st.session_state["active_timeline_category"] = cat_name
                st.rerun()

    active_category = st.session_state["active_timeline_category"]

    # Optional Search and Sorting
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        timeline_search = st.text_input(
            "🔍 Search timeline milestones by title, author, event, or accession:",
            placeholder="e.g. 'Ashoka', 'Farman', 'Constitution', 'Chola', '300 BCE'...",
            key="timeline_search_input",
        )
    with col_sort:
        sort_order = st.selectbox(
            "Sort Chronology:",
            ["Chronological (Oldest First)", "Reverse (Newest First)"],
            key="timeline_sort_order",
        )

    # 3. Retrieve filtered records
    filtered_items = TimelineBuilder.get_timeline_records(
        category_filter=active_category,
        search_query=timeline_search,
    )

    if sort_order == "Reverse (Newest First)":
        filtered_items = list(reversed(filtered_items))

    # 4. Interactive Plotly Visual Timeline Graph
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("📊 Interactive Chronological Map & Distribution", expanded=True):
        fig = TimelineBuilder.build_plotly_timeline(filtered_items, selected_category=active_category)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # 5. Timeline Header Statistics
    st.markdown("---")
    scol1, scol2, scol3 = st.columns([2, 1, 1])
    with scol1:
        st.markdown(
            f"<h3 style='color: #fbbf24; margin: 0; font-family: Cinzel, serif;'>📜 Chronological Archival Milestones — {active_category} ({len(filtered_items)} Records)</h3>",
            unsafe_allow_html=True,
        )
    with scol2:
        earliest_yr = filtered_items[0]["year"] if filtered_items else "N/A"
        st.caption(f"⏳ **Earliest Milestone:** {earliest_yr}")
    with scol3:
        latest_yr = filtered_items[-1]["year"] if filtered_items else "N/A"
        st.caption(f"⌛ **Latest Milestone:** {latest_yr}")

    if not filtered_items:
        st.warning(f"No records found matching filter '{active_category}' and query '{timeline_search}'.")
        return

    st.markdown("<br/>", unsafe_allow_html=True)

    # 6. VISUAL HERITAGE TIMELINE CARDS
    # Exact required display hierarchy:
    # Year
    # ↓
    # Historical Event / Record
    # ↓
    # Title
    # ↓
    # Short Description
    # ↓
    # View Document
    # ↓
    # View Source
    for idx, item in enumerate(filtered_items, start=1):
        doc_id = item["id"]
        year_str = item["year"]
        event_str = item["historical_event"]
        title_str = item["title"]
        short_desc = item["short_description"]
        category = item["category"]
        creator = item["creator"]
        institution = item["institution"]
        accession = item["accession_number"]
        rights = item["rights"]
        raw_path = item.get("saved_file_path")
        doc_type = item.get("document_type", "Archival Record")
        lang = item.get("language", "Historical Script")
        transcript = item.get("cleaned_text") or item.get("full_description") or ""

        cat_badge_color = CATEGORY_COLORS.get(category, "#fbbf24")
        cat_icon = CATEGORY_ICONS.get(category, "📜")

        with st.container():
            # Build the card HTML without leading whitespace to prevent Markdown code-block parsing
            card_html = textwrap.dedent(f"""
            <div style="background: rgba(15, 23, 42, 0.9); border-radius: 8px; border: 1px solid rgba(251, 191, 36, 0.25); border-left: 5px solid {cat_badge_color}; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid #fbbf24; font-size: 1.15rem; font-weight: 700; padding: 4px 14px; border-radius: 6px; font-family: 'Cinzel', serif;">
                            📅 {year_str}
                        </span>
                        <span style="background: {cat_badge_color}22; color: {cat_badge_color}; border: 1px solid {cat_badge_color}; font-size: 0.84rem; font-weight: 600; padding: 4px 12px; border-radius: 12px;">
                            {cat_icon} {category}
                        </span>
                    </div>
                    <span style="color: #94a3b8; font-size: 0.82rem; font-family: monospace;">
                        Accession: {accession}
                    </span>
                </div>
                <div style="color: #6ee7b7; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                    🏛️ {event_str}
                </div>
                <h3 style="color: #fbbf24; margin: 0 0 10px 0; font-family: 'Cinzel', serif; font-size: 1.3rem;">
                    {title_str}
                </h3>
                <p style="color: #cbd5e1; font-size: 0.96rem; line-height: 1.6; margin: 0 0 12px 0;">
                    {short_desc}
                </p>
                <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.85rem; color: #94a3b8;">
                    <span>👑 <strong>Creator:</strong> {creator}</span>
                    <span>📄 <strong>Type:</strong> {doc_type}</span>
                    <span>🌐 <strong>Language:</strong> {lang}</span>
                    <span>🏛️ <strong>Holding:</strong> {institution}</span>
                </div>
            </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)

            # Action Bar: View Document, Quick Inspect / TTS, and View Source
            btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1, 1])

            with btn_col1:
                # 5. VIEW DOCUMENT - Direct navigation to Full Document Viewer
                if st.button(
                    f"📜 View Document #{doc_id}",
                    key=f"timeline_view_doc_btn_{doc_id}_{idx}",
                    type="primary",
                    use_container_width=True,
                    help="Opens this archival record in the full Digital Document Viewer with zoom, translation, and Dublin Core metadata.",
                ):
                    st.session_state["selected_doc_id"] = doc_id
                    st.session_state["nav_target"] = "Document Viewer"
                    st.session_state["_sidebar_nav_radio_widget"] = "Document Viewer"
                    st.session_state["current_page"] = "Document Viewer"
                    st.rerun()

            with btn_col2:
                # Quick Inline Preview & TTS Expander
                with st.expander("🔍 Quick Preview & TTS", expanded=False):
                    if raw_path and Path(raw_path).exists() and not raw_path.lower().endswith(".pdf"):
                        try:
                            img = Image.open(raw_path)
                            st.image(img, use_container_width=True, caption=f"{title_str} ({year_str})")
                        except Exception:
                            st.info(f"📁 Artifact: `{Path(raw_path).name}`")
                    else:
                        st.info(f"📄 Artifact File: `{Path(raw_path).name if raw_path else 'Primary Document'}`")

                    st.markdown("##### 🎙️ Audio Narration (TTS):")
                    render_interactive_audio_player(
                        text=transcript[:400] if transcript else short_desc,
                        lang_code="en",
                        key_prefix=f"tl_audio_{doc_id}_{idx}",
                    )

            with btn_col3:
                # 6. VIEW SOURCE (Dublin Core Metadata & Download)
                with st.expander("🏛️ View Source", expanded=False):
                    src_html = textwrap.dedent(f"""
                    <div style="background: rgba(10, 15, 26, 0.9); padding: 10px; border-radius: 6px; border: 1px solid rgba(251, 191, 36, 0.25); font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">
                        <strong style="color: #fbbf24;">🏛️ Institution:</strong> {institution}<br/>
                        <strong style="color: #fbbf24;">🆔 Accession:</strong> <code>{accession}</code><br/>
                        <strong style="color: #fbbf24;">🛡️ Rights:</strong> {rights}<br/>
                        <strong style="color: #fbbf24;">📄 Format:</strong> {doc_type} ({lang})<br/>
                        <strong style="color: #fbbf24;">📁 Path:</strong> <code>{raw_path or 'data/raw_documents/'}</code>
                    </div>
                    """)
                    st.markdown(src_html, unsafe_allow_html=True)
                    
                    if raw_path and Path(raw_path).exists():
                        f_bytes = Path(raw_path).read_bytes()
                        st.download_button(
                            label=f"📥 Download ({Path(raw_path).name})",
                            data=f_bytes,
                            file_name=Path(raw_path).name,
                            mime="image/png" if raw_path.endswith(".png") else "application/pdf",
                            key=f"timeline_dl_src_{doc_id}_{idx}",
                            use_container_width=True,
                        )

            st.markdown("<br/>", unsafe_allow_html=True)
