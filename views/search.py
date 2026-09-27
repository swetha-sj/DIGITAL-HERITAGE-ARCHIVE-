"""
Digital Heritage Archive - Smart Search View
Hybrid Search combining Sentence Transformers dense embeddings, FAISS vector indexing,
and multi-attribute faceted filters with interactive Listen (TTS), Translate, View Source, and Save.
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import textwrap
from core.storage import get_all_records
from core.search_engine import SmartSearchEngine
from core.tts_engine import TTSEngine
from core.translator import HeritageTranslator
from core.ai_summarizer import ArchivalSummarizer
from config import SUPPORTED_LANGUAGES


def render_search():
    header_html = textwrap.dedent("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">SMART SEARCH</h1>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
            Dense Vector Semantic Embeddings &bull; FAISS Vector Search &bull; Faceted Multi-Attribute Discovery
        </p>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    records = get_all_records()
    if not records:
        st.info("No records in the database yet. Go to **Admin** to upload archival materials.")
        return

    # Initialize Saved Bookmarks in session state
    if "saved_bookmarks" not in st.session_state:
        st.session_state["saved_bookmarks"] = {}

    search_engine = SmartSearchEngine()

    # Section 1: Main Search Query Bar
    scol_q, scol_btn = st.columns([4, 1])
    with scol_q:
        user_query = st.text_input(
            "Natural Language Concept or Keyword Search:",
            placeholder="e.g. 'Religious harmony and speech restraint', 'Land endowments by Mughal emperor', 'Chola copper plate'",
            label_visibility="collapsed",
            key="smart_search_input",
        )
    with scol_btn:
        search_pressed = st.button("⚡ Smart Search", type="primary", use_container_width=True)

    # Section 2: Faceted Filters (Search by Topic, Person/Creator, Date/Year, Document Type, Language, Institution, Media Type)
    with st.expander("🎯 Faceted Multi-Attribute Filters (Topic, Creator, Year, Type, Language, Institution, Media)", expanded=False):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            topics = ["All"] + sorted(list(set(r["topic"] for r in records if r.get("topic"))))
            f_topic = st.selectbox("Topic / Subject:", topics)

            creators = ["All"] + sorted(list(set(r["creator"] for r in records if r.get("creator"))))
            f_creator = st.selectbox("Person / Creator:", creators)

        with fcol2:
            years = ["All"] + sorted(list(set(str(r["year"]) for r in records if r.get("year"))))
            f_year = st.selectbox("Date / Year / Era:", years)

            doc_types = ["All"] + sorted(list(set(r["document_type"] for r in records if r.get("document_type"))))
            f_type = st.selectbox("Document Type:", doc_types)

        with fcol3:
            languages = ["All"] + sorted(list(set(r["language"] for r in records if r.get("language"))))
            f_lang = st.selectbox("Language:", languages)

            institutions = ["All"] + sorted(list(set(r["institution"] for r in records if r.get("institution"))))
            f_inst = st.selectbox("Institution:", institutions)

        f_media = st.radio("Media Type:", ["All", "Image", "PDF"], horizontal=True)

    # Execute Smart Search Workflow
    with st.spinner("Executing FAISS vector semantic search and ranking archival records..."):
        results = search_engine.smart_search(
            keyword=user_query,
            topic_filter=f_topic,
            creator_filter=f_creator,
            year_filter=f_year,
            doc_type_filter=f_type,
            language_filter=f_lang,
            institution_filter=f_inst,
            media_type_filter=f_media,
            top_k=15,
        )

    # Top stats bar
    top_bar_col1, top_bar_col2 = st.columns([3, 1])
    with top_bar_col1:
        st.markdown(f"### 📚 Found {len(results)} Relevant Archival Records")
    with top_bar_col2:
        if st.button("🔄 Sync FAISS Vector Store", help="Recomputes dense embeddings for all SQLite records"):
            c = search_engine.reindex_all_documents()
            st.success(f"Indexed {c} records in FAISS!")

    if not results:
        st.warning("No records matched your search query. Try broader keywords or clearing filters.")
        return

    # Section 3: Render Result Cards
    for idx, rec in enumerate(results, start=1):
        rec_id = rec["id"]
        rel_pct = rec.get("relevance_percentage", 90.0)
        raw_path = rec.get("saved_file_path")
        proc_path = rec.get("processed_file_path")
        transcript = rec.get("cleaned_text") or rec.get("raw_ocr_text") or ""
        ai_summary = ArchivalSummarizer.generate_structured_summary(rec)
        summary_text = ai_summary.get("executive_summary") or rec.get("description") or "Historical archival record."

        with st.container():
            card_html = textwrap.dedent(f"""
            <div class="heritage-card" style="margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap: wrap; margin-bottom: 8px;">
                    <h3 style="margin:0; color:#fbbf24; font-size: 1.3rem;">
                        #{idx}. {rec['title']}
                    </h3>
                    <span class="heritage-badge badge-emerald">
                        ⚡ {rel_pct}% Semantic Relevance (FAISS)
                    </span>
                </div>
                <div style="margin-bottom: 10px;">
                    <span class="heritage-badge">📜 Type: <strong>{rec['document_type']}</strong></span>
                    <span class="heritage-badge">📅 Year: <strong>{rec['year']}</strong></span>
                    <span class="heritage-badge">👤 Creator: <strong>{rec['creator']}</strong></span>
                    <span class="heritage-badge">🏷️ Topic: <strong>{rec['topic']}</strong></span>
                    <span class="heritage-badge">🌐 Language: <strong>{rec['language']}</strong></span>
                    <span class="heritage-badge">🏛️ Institution: <strong>{rec['institution']}</strong></span>
                    <span class="heritage-badge">🛡️ Rights: <strong>{rec['rights']}</strong></span>
                    <span class="heritage-badge">🆔 Accession: <code>{rec['accession_number']}</code></span>
                </div>
                <div style="margin: 8px 0; color: #e2e8f0; font-size: 0.95rem; line-height: 1.5;">
                    <strong style="color: #fbbf24;">Description:</strong> {rec['description'] or 'No detailed description provided.'}
                </div>
                <div style="background: rgba(15, 23, 42, 0.75); padding: 12px 16px; border-left: 4px solid #fbbf24; border-radius: 4px; margin: 8px 0;">
                    <strong style="color: #fbbf24;">📑 AI Summary:</strong> {summary_text}
                </div>
            </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)

            # View Source Direct Launcher Action
            if st.button(f"🔍 View Source — Open in Digital Document Viewer (#{rec_id}: {rec['title'][:40]}...)", key=f"view_src_main_{rec_id}_{idx}", type="primary", use_container_width=True):
                st.session_state["selected_doc_id"] = rec_id
                st.session_state["nav_target"] = "Document Viewer"
                st.session_state["_sidebar_nav_radio_widget"] = "Document Viewer"
                st.session_state["current_page"] = "Document Viewer"
                st.rerun()

            # Interactive Action Tabs: View Source, Full Transcript, Listen, Translate, Save Source
            t1, t2, t3, t4, t5 = st.tabs([
                "🖼️ 1. Quick View Source (Scan & Rights)",
                "📝 2. Extracted OCR Text & Summary",
                "🔊 3. Listen (TTS Narration)",
                "🌐 4. Translate",
                "💾 5. Save Source",
            ])

            # Tab 1: View Source (Original document/image, Rights, Holding Institution)
            with t1:
                col_src1, col_src2 = st.columns([1, 1])
                with col_src1:
                    img_shown = False
                    if proc_path and Path(proc_path).exists():
                        try:
                            p_img = Image.open(proc_path)
                            st.image(p_img, caption="✨ Enhanced Preprocessed Scan", use_container_width=True)
                            img_shown = True
                        except Exception:
                            pass
                    
                    if not img_shown and raw_path and Path(raw_path).exists():
                        if not str(raw_path).lower().endswith(".pdf"):
                            try:
                                r_img = Image.open(raw_path)
                                st.image(r_img, caption=f"Original Scan: {rec['original_filename']}", use_container_width=True)
                            except Exception:
                                pass
                        else:
                            st.info("📄 Scanned PDF document cataloged in repository.")

                with col_src2:
                    st.markdown("#### 🏛️ Holding & Rights Information")
                    st.markdown(
                        f"""
                        - **Document Title:** {rec['title']}
                        - **Creator / Authority:** {rec['creator']}
                        - **Year / Era:** {rec['year']}
                        - **Document Type:** {rec['document_type']}
                        - **Language / Script:** {rec['language']}
                        - **Holding Institution:** {rec['institution']}
                        - **Rights / License:** `{rec['rights']}`
                        - **Accession Number:** `{rec['accession_number']}`
                        - **Storage Path:** `{rec['saved_file_path']}`
                        """
                    )
                    if raw_path and Path(raw_path).exists():
                        try:
                            f_data = Path(raw_path).read_bytes()
                            st.download_button(
                                label=f"📥 Download Original File ({rec['original_filename']})",
                                data=f_data,
                                file_name=rec['original_filename'],
                                mime="application/pdf" if str(raw_path).lower().endswith(".pdf") else "image/png",
                                key=f"src_dl_{rec_id}_{idx}",
                                use_container_width=True,
                            )
                        except Exception:
                            pass

            # Tab 2: Full Extracted OCR Transcript & AI Summary
            with t2:
                st.markdown("#### 📑 AI Historical Analysis & Transcript")
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.6); padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #10b981;">
                        <strong style="color: #6ee7b7;">Thematic Focus:</strong> {ai_summary['thematic_focus']}<br/>
                        <strong style="color: #6ee7b7;">Key Entities:</strong> {', '.join(ai_summary['entities'])}<br/>
                        <strong style="color: #6ee7b7;">OCR Quality Confidence:</strong> {rec.get('ocr_confidence', 95.0):.1f}%
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if transcript:
                    st.text_area(
                        "Verified Extracted OCR Text:",
                        value=transcript,
                        height=200,
                        disabled=True,
                        key=f"tx_area_{rec_id}_{idx}",
                    )
                else:
                    st.info("No text transcript attached to this record.")

            # Tab 3: Listen (Text-to-Speech)
            with t3:
                st.markdown("#### 🎙️ Voice Audio Narration")
                text_to_read = transcript or rec.get("description") or rec.get("title", "")
                
                lcol1, lcol2 = st.columns([2, 1])
                with lcol1:
                    tts_speed = st.slider("Speech Rate (WPM):", 100, 200, 140, 10, key=f"tts_sp_{rec_id}_{idx}")
                with lcol2:
                    tts_voice = st.selectbox("Voice Gender:", ["Female", "Male"], key=f"tts_vc_{rec_id}_{idx}")

                if st.button("🔊 Play Voice Reading", key=f"tts_btn_{rec_id}_{idx}", use_container_width=True):
                    tts_engine = TTSEngine()
                    with st.spinner("Synthesizing historical narration with SAPI COM..."):
                        tts_res = tts_engine.generate_audio(
                            text=text_to_read, rate=tts_speed, voice_gender=tts_voice.lower()
                        )
                        if tts_res.get("success") and tts_res.get("audio_path"):
                            st.audio(tts_res["audio_path"])
                            st.success("Voice reading generated successfully!")
                        else:
                            st.error(f"TTS Note: {tts_res.get('error', 'Audio generation failed.')}")

            # Tab 4: Translate
            with t4:
                st.markdown("#### 🌐 Instant Multilingual Translation")
                trans_text_src = transcript or rec.get("description") or rec.get("title", "")
                
                tr_col1, tr_col2 = st.columns([2, 1])
                with tr_col1:
                    target_lang_code = st.selectbox(
                        "Target Language:",
                        options=list(SUPPORTED_LANGUAGES.keys()),
                        format_func=lambda x: SUPPORTED_LANGUAGES[x],
                        index=1,  # Default Hindi
                        key=f"trans_sel_{rec_id}_{idx}",
                    )
                with tr_col2:
                    st.write("")
                    st.write("")
                    run_trans = st.button("Translate Text", key=f"trans_btn_{rec_id}_{idx}", use_container_width=True)

                if run_trans:
                    with st.spinner(f"Translating into {SUPPORTED_LANGUAGES[target_lang_code]}..."):
                        t_res = HeritageTranslator.translate_text(trans_text_src, target_lang=target_lang_code)
                        if t_res.get("success"):
                            st.markdown(
                                f"""
                                <div style="background: rgba(15, 23, 42, 0.9); padding: 14px; border-radius: 6px; border: 1px solid #fbbf24;">
                                    <strong style="color:#fbbf24;">Translation ({SUPPORTED_LANGUAGES[target_lang_code]}):</strong><br/>
                                    <p style="color: #f1f5f9; font-size: 0.95rem; margin-top: 6px; white-space: pre-wrap;">{t_res['translated_text']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.error(f"Translation Note: {t_res.get('error')}")

            # Tab 5: Save Source Button
            with t5:
                st.markdown("#### 💾 Save Source & Academic Citation")
                is_saved = rec_id in st.session_state["saved_bookmarks"]
                
                save_col1, save_col2 = st.columns([1, 1])
                with save_col1:
                    if not is_saved:
                        if st.button("⭐ Save Source to Bookmarks", key=f"save_btn_{rec_id}_{idx}", use_container_width=True):
                            st.session_state["saved_bookmarks"][rec_id] = rec
                            st.success(f"Saved '{rec['title']}' to your research collection!")
                            st.rerun()
                    else:
                        if st.button("❌ Remove Source from Bookmarks", key=f"unsave_btn_{rec_id}_{idx}", use_container_width=True):
                            st.session_state["saved_bookmarks"].pop(rec_id, None)
                            st.info("Removed from saved bookmarks.")
                            st.rerun()

                with save_col2:
                    citation_text = (
                        f"{rec['creator']} ({rec['year']}). {rec['title']} [{rec['document_type']}]. "
                        f"Holding Institution: {rec['institution']}. Accession: {rec['accession_number']}. Rights: {rec['rights']}."
                    )
                    st.text_input("Standard Archival Citation (Copy):", value=citation_text, key=f"cite_{rec_id}_{idx}")

            st.markdown("<br/>", unsafe_allow_html=True)

    # Section 4: Display Saved Bookmarks Basket at the bottom if any
    if st.session_state["saved_bookmarks"]:
        st.markdown("---")
        with st.expander(f"⭐ Saved Research Collection ({len(st.session_state['saved_bookmarks'])} items)", expanded=False):
            for s_id, s_rec in st.session_state["saved_bookmarks"].items():
                st.markdown(f"- **{s_rec['title']}** ({s_rec['year']} | `{s_rec['accession_number']}`) — *{s_rec['institution']}*")
