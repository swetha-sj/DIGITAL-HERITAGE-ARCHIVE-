"""
Digital Heritage Archive - Digital Document Viewer
Interactive high-resolution manuscript & artifact inspector with side-by-side OCR transcript,
AI-generated summary, voice synthesis (TTS), live multilingual translation, and source preservation.
"""

import streamlit as st
from PIL import Image
from pathlib import Path
import json
import textwrap
from core.storage import get_all_records, get_record_by_id, get_multimedia_for_record
from core.tts_engine import TTSEngine, get_web_speech_html, render_interactive_audio_player
from core.translator import HeritageTranslator, ALL_LANGUAGES, DEMO_LANGUAGES
from core.ai_summarizer import ArchivalSummarizer
from config import SUPPORTED_LANGUAGES


def render_document_viewer(default_record_id: int = None):
    """Renders the Digital Document Viewer interface for inspecting archival sources."""
    
    header_html = textwrap.dedent("""
    <div style="text-align: center; margin-bottom: 22px;">
        <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">DIGITAL DOCUMENT VIEWER</h1>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
            High-Resolution Archival Inspection &bull; OCR Transcription &bull; AI Historical Summary &bull; Multilingual Translation &bull; Voice Synthesis
        </p>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    records = get_all_records(limit=200)
    if not records:
        st.warning("No archival records found in the database. Please ingest documents in the **Admin** panel.")
        return

    # Check session state for document selection from Search or other views
    selected_doc_id = default_record_id or st.session_state.get("selected_doc_id")

    # Document Selection Bar
    doc_map = {f"#{r['id']} — {r['title']} ({r.get('year', 'Historical')}) [{r.get('document_type', 'Record')}]": r['id'] for r in records}
    doc_labels = list(doc_map.keys())

    # Find default index
    default_idx = 0
    if selected_doc_id:
        for idx, lbl in enumerate(doc_labels):
            if doc_map[lbl] == selected_doc_id:
                default_idx = idx
                break

    sel_col1, sel_col2 = st.columns([3, 1])
    with sel_col1:
        chosen_label = st.selectbox(
            "Select Archival Record to Inspect:",
            options=doc_labels,
            index=default_idx,
        )
    with sel_col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Archive View", use_container_width=True):
            st.rerun()

    active_id = doc_map.get(chosen_label, doc_map[doc_labels[0]])
    st.session_state["selected_doc_id"] = active_id
    rec = get_record_by_id(active_id)

    if not rec:
        st.error(f"Could not load record #{active_id}.")
        return

    # Generate AI structured summary
    ai_summary = ArchivalSummarizer.generate_structured_summary(rec)

    # Initialize Saved Bookmarks in session state if not present
    if "saved_bookmarks" not in st.session_state:
        st.session_state["saved_bookmarks"] = {}

    is_saved = active_id in st.session_state["saved_bookmarks"]

    # =========================================================================
    # 1. TOP METADATA BANNER (Items 2, 3, 4, 5, 6, 7, 8)
    # =========================================================================
    banner_html = textwrap.dedent(f"""
    <div class="doc-viewer-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
            <div>
                <span class="heritage-badge badge-sapphire" style="font-size: 0.85rem;">
                    🆔 Accession No: <strong>{rec.get('accession_number', 'DHA-001')}</strong>
                </span>
                <span class="heritage-badge badge-emerald" style="font-size: 0.85rem;">
                    ✨ OCR Confidence: <strong>{rec.get('ocr_confidence', 95.0):.1f}%</strong>
                </span>
                <h2 style="margin: 8px 0 4px 0; color: #fbbf24; font-size: 1.8rem; font-family: 'Cinzel', serif;">
                    {rec['title']}
                </h2>
            </div>
        </div>
        
        <div class="meta-grid">
            <div class="meta-item">
                <div class="meta-label">👤 Creator / Authority</div>
                <div class="meta-value">{rec.get('creator', 'Historical Scribes')}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">📅 Year / Period</div>
                <div class="meta-value">{rec.get('year', 'Ancient Era')}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">📜 Document Type</div>
                <div class="meta-value">{rec.get('document_type', 'Manuscript')}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">🌐 Language / Script</div>
                <div class="meta-value">{rec.get('language', 'Classical Sanskrit')}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">🏛️ Holding Institution</div>
                <div class="meta-value">{rec.get('institution', 'National Archives of India')}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">🛡️ Rights & Source Info</div>
                <div class="meta-value">{rec.get('rights', 'Public Domain / CC0 Open Access')}</div>
            </div>
        </div>
    </div>
    """)
    st.markdown(banner_html, unsafe_allow_html=True)

    # =========================================================================
    # 2. MAIN DUAL-PANE WORKSPACE: Left = Original Scan, Right = OCR & AI Summary
    # =========================================================================
    col_left, col_right = st.columns([1, 1], gap="large")

    # -------------------------------------------------------------------------
    # LEFT PANE: Original Document / Image (Item 1)
    # -------------------------------------------------------------------------
    with col_left:
        st.markdown("### 🖼️ Original Archival Document / Scan")
        
        raw_path = rec.get("saved_file_path")
        proc_path = rec.get("processed_file_path")
        
        # Scan Type Selector (Enhanced Preprocessed vs Raw Archival Original)
        has_processed = proc_path and Path(proc_path).exists()
        has_raw = raw_path and Path(raw_path).exists()

        scan_view_mode = "Enhanced Scan"
        if has_processed and has_raw:
            scan_view_mode = st.radio(
                "Scan Display Mode:",
                ["Enhanced Scan (Preprocessed)", "Original Raw Scan"],
                horizontal=True,
                key=f"scan_mode_{active_id}",
            )

        img_displayed = False
        target_img_path = proc_path if (scan_view_mode.startswith("Enhanced") and has_processed) else raw_path

        if target_img_path and Path(target_img_path).exists():
            if str(target_img_path).lower().endswith(".pdf"):
                st.info(f"📄 **PDF Document Cataloged**: `{rec.get('original_filename')}`")
                st.markdown(f"**Stored Path:** `{target_img_path}`")
                img_displayed = True
            else:
                try:
                    img = Image.open(target_img_path)
                    st.image(
                        img,
                        caption=f"Archival Source: {rec['title']} ({img.width}x{img.height} px)",
                        use_container_width=True,
                    )
                    img_displayed = True
                except Exception as e:
                    st.warning(f"Could not open image file: {e}")

        if not img_displayed:
            st.info(f"Visual asset file: `{rec.get('original_filename')}` (stored at `{raw_path}`)")

        # Image & Storage Technical Metadata Details
        with st.expander("📦 Archival Storage & Repository Technical Data", expanded=False):
            st.markdown(
                f"""
                - **Original Filename:** `{rec.get('original_filename')}`
                - **File Format:** `{rec.get('file_type')}`
                - **File Size:** `{rec.get('file_size_bytes', 0)/1024:.2f} KB`
                - **Primary Storage Path:** `{rec.get('saved_file_path')}`
                - **Processed Enhanced Path:** `{rec.get('processed_file_path') or 'N/A'}`
                - **Catalog Creation Date:** `{rec.get('created_at', 'Recently Ingested')}`
                """
            )
            if raw_path and Path(raw_path).exists():
                try:
                    f_bytes = Path(raw_path).read_bytes()
                    st.download_button(
                        label=f"📥 Download Original Document File ({rec.get('original_filename')})",
                        data=f_bytes,
                        file_name=rec.get("original_filename", "archival_source.png"),
                        mime="application/pdf" if str(raw_path).lower().endswith(".pdf") else "image/png",
                        key=f"dl_left_{active_id}",
                        use_container_width=True,
                    )
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # RIGHT PANE: Extracted OCR Text (Item 9) & AI-Generated Summary (Item 10)
    # -------------------------------------------------------------------------
    with col_right:
        # Item 10: AI-Generated Historical Summary
        st.markdown("### 📑 AI-Generated Historical Summary")
        summary_box_html = textwrap.dedent(f"""
        <div class="ai-summary-box">
            <div style="color: #fbbf24; font-weight: 700; font-size: 1.05rem; margin-bottom: 6px;">
                🏛️ Historical & Diplomatic Context
            </div>
            <p style="color: #f1f5f9; font-size: 0.96rem; margin: 0 0 10px 0; line-height: 1.6;">
                {ai_summary['executive_summary']}
            </p>
            <div style="margin-top: 8px; font-size: 0.88rem; color: #cbd5e1;">
                <strong style="color: #fbbf24;">🏷️ Thematic Focus:</strong> {ai_summary['thematic_focus']}<br/>
                <strong style="color: #fbbf24;">🔍 Key Entities:</strong> {', '.join(ai_summary['entities'])}<br/>
                <strong style="color: #fbbf24;">⏱️ Reading Time:</strong> ~{ai_summary['reading_time_minutes']} min ({ai_summary['word_count']} words)
            </div>
        </div>
        """)
        st.markdown(summary_box_html, unsafe_allow_html=True)

        # Item 9: Extracted OCR Text
        st.markdown("### 📝 Extracted OCR Text (Verified Transcript)")
        
        transcript = rec.get("cleaned_text") or rec.get("raw_ocr_text") or rec.get("description") or "No transcript text available."
        
        # Word count and metrics
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.caption(f"📊 {len(transcript.split())} Words &bull; {len(transcript)} Characters &bull; {rec.get('language')} Script")
        with t_col2:
            st.caption(f"🛡️ OCR Confidence: **{rec.get('ocr_confidence', 95.0):.1f}%**")

        st.text_area(
            "Archival Transcript Content:",
            value=transcript,
            height=230,
            disabled=True,
            key=f"viewer_transcript_area_{active_id}",
        )

    st.markdown("---")

    # =========================================================================
    # 3. INTERACTIVE ACTIONS BAR (Items 11, 12, 13)
    # =========================================================================
    st.markdown("### ⚡ Interactive Archival Tools")

    tab_listen, tab_translate, tab_media, tab_save = st.tabs([
        "🔊 Listen (Audio Narration)",
        "🌐 Translate (Multilingual)",
        "🎬 Connected Multimedia (Audio/Video)",
        "💾 Save Source & Export",
    ])

    # -------------------------------------------------------------------------
    # ITEM 11: Listen Button (Text-to-Speech)
    # -------------------------------------------------------------------------
    with tab_listen:
        st.markdown("#### 🎙️ Synthesize Archival Voice Narration")
        st.markdown("Listen to the transcribed historical text read aloud with offline speech synthesis.")
        
        lcol1, lcol2, lcol3 = st.columns([2, 1, 1])
        with lcol1:
            speech_rate = st.slider("Playback Rate (Words Per Minute):", 100, 200, 140, 10, key=f"tts_rate_{active_id}")
        with lcol2:
            voice_gender = st.selectbox("Voice Gender:", ["Female", "Male"], key=f"tts_gender_{active_id}")
        with lcol3:
            st.write("")
            st.write("")
            listen_btn = st.button("🔊 Synthesize & Listen", type="primary", use_container_width=True, key=f"listen_btn_{active_id}")

        # Detect language
        doc_lang = rec.get("language", "English").lower()
        lang_tag = "en"
        if "hindi" in doc_lang or "sanskrit" in doc_lang:
            lang_tag = "hi"
        elif "kannada" in doc_lang:
            lang_tag = "kn"
        elif "tamil" in doc_lang:
            lang_tag = "ta"
        elif "telugu" in doc_lang:
            lang_tag = "te"

        tts_text = transcript if len(transcript.strip()) > 10 else rec.get("title", "")
        st.markdown("<br/>", unsafe_allow_html=True)
        render_interactive_audio_player(
            text=tts_text[:600],
            lang_code=lang_tag,
            key_prefix=f"doc_listen_{active_id}",
        )

    # -------------------------------------------------------------------------
    # ITEM 12: Translate Button (Multilingual Translation - English, Hindi, Kannada, Tamil)
    # -------------------------------------------------------------------------
    with tab_translate:
        st.markdown("#### 🌐 Multilingual Access (Demonstration Languages)")
        st.markdown("Translate archival records between **English**, **हिन्दी (Hindi)**, **ಕನ್ನಡ (Kannada)**, and **தமிழ் (Tamil)**.")

        tcol1, tcol2 = st.columns([2, 1])
        with tcol1:
            target_lang_code = st.radio(
                "Select Target Demonstration Language:",
                options=["hi", "kn", "ta", "en"],
                format_func=lambda code: {"en": "English", "hi": "हिन्दी (Hindi)", "kn": "ಕನ್ನಡ (Kannada)", "ta": "தமிழ் (Tamil)"}[code],
                horizontal=True,
                index=0,
                key=f"trans_target_{active_id}",
            )
        with tcol2:
            st.write("")
            translate_btn = st.button("🌐 Translate Text", type="primary", use_container_width=True, key=f"trans_btn_{active_id}")

        if translate_btn or transcript:
            with st.spinner("Executing translation pipeline..."):
                trans_res = HeritageTranslator.translate_text(transcript, target_lang=target_lang_code)

            target_lang_title = {"en": "English", "hi": "हिन्दी (Hindi)", "kn": "ಕನ್ನಡ (Kannada)", "ta": "தமிழ் (Tamil)"}.get(target_lang_code, target_lang_code)

            # Workflow: Original Text -> Translation -> Translated Text (Displayed Together Side-by-Side)
            st.markdown(f"##### 📜 Dual-Pane Display: Original & Translated Text ({target_lang_title})")
            
            dcol_orig, dcol_trans = st.columns(2, gap="medium")
            with dcol_orig:
                orig_box_html = textwrap.dedent(f"""
                <div style="background: rgba(15, 23, 42, 0.9); padding: 14px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.4); border-top: 3px solid #3b82f6;">
                    <div style="color: #93c5fd; font-weight: 700; margin-bottom: 6px; font-size: 0.95rem;">
                        📜 Original Text ({rec.get('language', 'Original Script')})
                    </div>
                    <p style="color: #e2e8f0; font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; line-height: 1.6; white-space: pre-wrap; margin: 0; max-height: 260px; overflow-y: auto;">
{transcript}
                    </p>
                </div>
                """)
                st.markdown(orig_box_html, unsafe_allow_html=True)

            with dcol_trans:
                if trans_res.get("success"):
                    trans_box_html = textwrap.dedent(f"""
                    <div style="background: rgba(15, 23, 42, 0.9); padding: 14px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.4); border-top: 3px solid #10b981;">
                        <div style="color: #6ee7b7; font-weight: 700; margin-bottom: 6px; font-size: 0.95rem;">
                            🌐 Translated Text ({target_lang_title})
                        </div>
                        <p style="color: #f8fafc; font-size: 0.94rem; line-height: 1.7; white-space: pre-wrap; margin: 0; max-height: 260px; overflow-y: auto;">
{trans_res['translated_text']}
                        </p>
                    </div>
                    """)
                    st.markdown(trans_box_html, unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 10px;'><strong>🔊 Translated Speech Narration:</strong></div>", unsafe_allow_html=True)
                    render_interactive_audio_player(
                        text=trans_res["translated_text"][:500],
                        lang_code=target_lang_code,
                        key_prefix=f"doc_trans_{active_id}_{target_lang_code}",
                    )
                else:
                    st.error(f"Translation Note: {trans_res.get('error', 'Translation failed.')}")

    # -------------------------------------------------------------------------
    # TAB 3: Connected Multimedia (Audio / Video / Scans)
    # -------------------------------------------------------------------------
    with tab_media:
        st.markdown(f"#### 🎬 Multimedia Assets Connected to Record #{active_id}")
        st.markdown(f"Historical audio recordings, video reels, and architectural scans linked to **{rec.get('title')}**.")

        linked_media = get_multimedia_for_record(active_id)
        if not linked_media:
            st.info(f"No multimedia items currently linked to record #{active_id}. You can upload and connect audio, video, or image artifacts in the **Audio-Visual** archive tab.")
        else:
            st.markdown(f"##### 📚 Found {len(linked_media)} Connected Media Items:")
            for m_idx, item in enumerate(linked_media, start=1):
                m_type = item.get("media_type", "image").lower()
                m_title = item.get("title", "Archival Media")
                m_desc = item.get("description") or item.get("transcript") or ""
                m_creator = item.get("creator") or item.get("speaker_narrator") or "Archivist"
                m_year = item.get("year") or item.get("recorded_date") or ""
                m_path = item.get("file_path", "")
                m_dur = item.get("duration_seconds", 0.0)

                m_acc = item.get("accession_number") or f"AV-{item.get('id', '0')}"
                m_inst = item.get("institution", "National Archives")

                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.85); padding: 14px; border-radius: 6px; border-left: 4px solid #f59e0b; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <strong style="color: #fbbf24; font-size: 1.05rem;">
                                    #{m_idx}. [{m_type.upper()}] {m_title}
                                </strong>
                                <span class="heritage-badge badge-amber">{m_acc}</span>
                            </div>
                            <div style="color: #94a3b8; font-size: 0.84rem; margin: 4px 0 8px 0;">
                                👤 <strong>Creator/Speaker:</strong> {m_creator} | 📅 <strong>Year:</strong> {m_year} | 🏛️ <strong>Institution:</strong> {m_inst}
                            </div>
                            <p style="color: #e2e8f0; font-size: 0.9rem; margin: 0 0 8px 0;">
                                {m_desc}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if m_type == "audio" and m_path and Path(m_path).exists():
                        st.audio(m_path)
                    elif m_type == "video" and m_path and Path(m_path).exists():
                        st.video(m_path)
                    elif m_type == "image" and m_path and Path(m_path).exists():
                        try:
                            img = Image.open(m_path)
                            st.image(img, use_container_width=True, caption=m_title)
                        except Exception:
                            st.info(f"Image: {Path(m_path).name}")

                    if item.get("transcript"):
                        with st.expander(f"📝 View Transcript for '{m_title}'", expanded=False):
                            st.write(item.get("transcript"))

                    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # ITEM 13: Save Source Button & Research Collection Management
    # -------------------------------------------------------------------------
    with tab_save:
        st.markdown("#### 💾 Save Archival Source to Research Collection")
        
        save_btn_col1, save_btn_col2 = st.columns([1, 2])
        with save_btn_col1:
            if not is_saved:
                if st.button("⭐ Save Source to Research Basket", type="primary", use_container_width=True, key=f"save_src_btn_{active_id}"):
                    st.session_state["saved_bookmarks"][active_id] = rec
                    st.success(f"Saved '{rec['title']}' to your research collection!")
                    st.rerun()
            else:
                if st.button("❌ Remove Source from Saved", use_container_width=True, key=f"unsave_src_btn_{active_id}"):
                    st.session_state["saved_bookmarks"].pop(active_id, None)
                    st.info("Removed source from saved collection.")
                    st.rerun()

        with save_btn_col2:
            # Export Full Metadata as JSON
            meta_export = {
                "accession_number": rec.get("accession_number"),
                "title": rec.get("title"),
                "creator": rec.get("creator"),
                "year": rec.get("year"),
                "language": rec.get("language"),
                "topic": rec.get("topic"),
                "document_type": rec.get("document_type"),
                "institution": rec.get("institution"),
                "rights": rec.get("rights"),
                "description": rec.get("description"),
                "ai_summary": ai_summary.get("executive_summary"),
                "transcript": transcript,
                "ocr_confidence": rec.get("ocr_confidence"),
                "export_timestamp": "2026-09-27T19:15:00Z",
            }
            json_str = json.dumps(meta_export, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Export Source Record (JSON Metadata)",
                data=json_str,
                file_name=f"{rec.get('accession_number', 'record')}_metadata.json",
                mime="application/json",
                key=f"dl_json_{active_id}",
                use_container_width=True,
            )

        # Standard Citation Box
        st.markdown("##### 📖 Archival Academic Citations")
        citation_apa = f"{rec.get('creator', 'Author')} ({rec.get('year', 'n.d.')}). {rec.get('title')}. [{rec.get('document_type')}]. {rec.get('institution')}. Accession: {rec.get('accession_number')}."
        citation_chicago = f"{rec.get('creator', 'Author')}. \"{rec.get('title')}.\" {rec.get('document_type')}, {rec.get('year')}. Holding: {rec.get('institution')}, {rec.get('accession_number')}."
        
        cite_html = textwrap.dedent(f"""
        <div class="citation-box">
            <strong style="color: #fbbf24;">APA Citation:</strong><br/>
            <code>{citation_apa}</code><br/><br/>
            <strong style="color: #fbbf24;">Chicago Citation:</strong><br/>
            <code>{citation_chicago}</code>
        </div>
        """)
        st.markdown(cite_html, unsafe_allow_html=True)
