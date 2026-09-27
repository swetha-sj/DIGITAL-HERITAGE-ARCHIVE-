"""
Digital Heritage Archive - Home Hub View
Featuring Dr. B. R. Ambedkar & National Heritage collections, interactive search bar with tag chips,
6 feature cards, Dublin Core metrics, and recently cataloged archival treasures.
"""

import streamlit as st
import textwrap
from pathlib import Path
from PIL import Image
from config import ASSETS_DIR
from core.storage import get_all_records, get_stats
from core.auth import get_current_user


def render_home():
    """Renders the creative National Heritage homepage."""
    current_user = get_current_user()

    # -------------------------------------------------------------------------
    # 1. TOP HERO BANNER & SEARCH BAR
    # -------------------------------------------------------------------------
    hero_col_text, hero_col_img = st.columns([1.6, 1.0], gap="medium")

    with hero_col_text:
        st.markdown(
            """
            <div style="padding: 10px 0;">
                <div class="auth-brand-badge">
                    🏛️ National Heritage Digital Repository • Ministry of Culture
                </div>
                <h1 style="font-family: 'Cinzel', serif; font-size: 2.3rem; color: #fef08a; margin: 8px 0 12px 0; line-height: 1.2;">
                    Explore Dr. B. R. Ambedkar’s & National Digital Heritage
                </h1>
                <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">
                    Discover writings, speeches, rare manuscripts, high-resolution photographs, and epigraphic records that shaped a democratic and egalitarian nation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick Instant Search Bar
        with st.container():
            col_search_inp, col_search_btn = st.columns([3.5, 1.0])
            with col_search_inp:
                quick_query = st.text_input(
                    "Search Query",
                    placeholder="🔍 Search documents, speeches, topics, creators...",
                    label_visibility="collapsed",
                    key="home_quick_search_input",
                )
            with col_search_btn:
                search_clicked = st.button("Search", type="primary", use_container_width=True, key="home_quick_search_btn")

            if search_clicked and quick_query.strip():
                st.session_state["search_keyword"] = quick_query.strip()
                st.session_state["current_page"] = "Search"
                st.rerun()

            # Search Filter Tag Chips
            st.markdown(
                """
                <div style="font-size: 0.8rem; color: #94a3b8; margin: 10px 0 4px 0;">
                    Popular Discovery Topics:
                </div>
                """,
                unsafe_allow_html=True,
            )

            chip_cols = st.columns(6)
            topics = [
                ("Constitution", "Constitution"),
                ("Education", "Education"),
                ("Social Justice", "Social Justice"),
                ("Women Rights", "Women"),
                ("Historic Speeches", "Speech"),
                ("Writings", "Manuscript"),
            ]
            for c_idx, (t_label, t_query) in enumerate(topics):
                with chip_cols[c_idx]:
                    if st.button(t_label, key=f"home_chip_{c_idx}", use_container_width=True):
                        st.session_state["search_keyword"] = t_query
                        st.session_state["current_page"] = "Search"
                        st.rerun()

    with hero_col_img:
        portrait_file = ASSETS_DIR / "ambedkar_portrait.jpg"
        if portrait_file.exists():
            try:
                p_img = Image.open(portrait_file)
                st.image(p_img, use_container_width=True, caption="Dr. B. R. Ambedkar • Chief Architect of the Constitution")
            except Exception:
                pass

    st.markdown("<hr style='margin: 24px 0; border-color: rgba(212, 175, 55, 0.25);'/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. SIX CORE CAPABILITY CARDS
    # -------------------------------------------------------------------------
    st.markdown("### 🧭 Explore Archival Systems & Capabilities")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">📖</div>
                <h4 style="color: #fbbf24; margin: 0 0 6px 0;">Explore Archives</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Browse primary documents, rare books, copper plates, and imperial farmans.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Document Viewer ➔", key="btn_card_viewer", use_container_width=True):
            st.session_state["current_page"] = "Document Viewer"
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🔍</div>
                <h4 style="color: #60a5fa; margin: 0 0 6px 0;">Smart Search</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Find historical evidence via 384-dim FAISS semantic vector retrieval.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Smart Search ➔", key="btn_card_search", use_container_width=True):
            st.session_state["current_page"] = "Search"
            st.rerun()

    with c3:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🤖</div>
                <h4 style="color: #34d399; margin: 0 0 6px 0;">AI Research Assistant</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Ask natural questions and receive source-grounded citations with zero hallucination.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ask AI Assistant ➔", key="btn_card_ai", use_container_width=True):
            st.session_state["current_page"] = "AI Assistant"
            st.rerun()

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🌐</div>
                <h4 style="color: #f472b6; margin: 0 0 6px 0;">Translate & Listen</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Translate ancient and modern texts to Hindi, Kannada, Tamil and synthesize audio.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Multilingual & TTS ➔", key="btn_card_multi", use_container_width=True):
            st.session_state["current_page"] = "Multilingual Access"
            st.rerun()

    with c5:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">⏳</div>
                <h4 style="color: #a78bfa; margin: 0 0 6px 0;">Interactive Timeline</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Explore chronological milestones across BCE and CE eras with category filtering.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Timeline ➔", key="btn_card_timeline", use_container_width=True):
            st.session_state["current_page"] = "Timeline"
            st.rerun()

    with c6:
        st.markdown(
            """
            <div class="heritage-card" style="height: 180px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🎙️</div>
                <h4 style="color: #fb923c; margin: 0 0 6px 0;">Audio-Visual Archive</h4>
                <p style="color: #94a3b8; font-size: 0.86rem; margin: 0 0 12px 0;">
                    Watch archival videos, listen to historic speeches, and view rare photographs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Media Gallery ➔", key="btn_card_av", use_container_width=True):
            st.session_state["current_page"] = "Audio-Visual"
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. NATIONAL METRICS & REPOSITORY HEALTH
    # -------------------------------------------------------------------------
    stats = get_stats()
    records = get_all_records()

    st.markdown("### 📊 National Catalog Overview & Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Cataloged Records", stats.get("total_documents", len(records)))
    with m2:
        st.metric("Audio-Visual Media Items", stats.get("total_multimedia", 14))
    with m3:
        unique_insts = len(set(r["institution"] for r in records)) if records else 0
        st.metric("Participating Institutions", unique_insts)
    with m4:
        st.metric("Search & Vector Engine", "FAISS 384-dim")

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. INSPIRING ARCHIVAL QUOTE BANNER
    # -------------------------------------------------------------------------
    st.markdown(
        """
        <div class="heritage-quote-card" style="text-align: center; margin: 15px 0 25px 0;">
            <div style="font-size: 2.2rem; color: #fbbf24; margin-bottom: 4px;">“</div>
            <div class="quote-text" style="font-size: 1.3rem; margin-bottom: 8px;">
                Be educated, be organized and be agitated.
            </div>
            <div class="quote-author" style="text-align: center;">
                — Dr. B. R. Ambedkar
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # 5. RECENTLY CATALOGED ARCHIVAL MATERIALS
    # -------------------------------------------------------------------------
    st.markdown("### 📜 Recently Cataloged Archival Materials")
    if not records:
        st.info("No documents cataloged yet. Navigate to **Admin** to upload your first document.")
    else:
        for idx, rec in enumerate(records[:5], start=1):
            with st.container():
                recent_card_html = textwrap.dedent(f"""
                <div class="heritage-card" style="margin-bottom: 8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap: wrap;">
                        <h4 style="margin:0; color:#fbbf24;">#{rec['id']}. {rec['title']}</h4>
                        <span class="heritage-badge">Year: {rec['year']}</span>
                    </div>
                    <p style="color:#94a3b8; font-size:0.9rem; margin:6px 0;">
                        👤 <strong>Creator:</strong> {rec['creator']} | 🏷️ <strong>Type:</strong> {rec['document_type']} | 🌐 <strong>Language:</strong> {rec['language']} | 🏛️ <strong>Institution:</strong> {rec['institution']}
                    </p>
                    <p style="color:#cbd5e1; font-size:0.9rem; margin:0;">
                        {rec['description'] or 'Archival document record.'}
                    </p>
                </div>
                """)
                st.markdown(recent_card_html, unsafe_allow_html=True)
                if st.button(
                    f"🔍 View Document #{rec['id']} in 13-Point Inspector",
                    key=f"home_view_btn_{rec['id']}_{idx}",
                    use_container_width=True,
                ):
                    st.session_state["selected_doc_id"] = rec["id"]
                    st.session_state["current_page"] = "Document Viewer"
                    st.rerun()
                st.markdown("<br/>", unsafe_allow_html=True)
