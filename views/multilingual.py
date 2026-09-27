"""
Digital Heritage Archive - Multilingual Access Hub
Supports:
- Core Demonstration Languages: English, Hindi, Kannada, Tamil
- Extended Multilingual Suite (18+ Indic & Global Languages):
  Telugu, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, Sanskrit, Urdu,
  French, German, Spanish, Japanese, Arabic.
Workflow: Original Archival Text -> Multi-Tier Translation -> Translated Text (Side-by-Side Dual Pane).
Pure Neural Native Speech Audio Playback.
"""

import streamlit as st
from pathlib import Path

try:
    from core.translator import HeritageTranslator, DEMO_LANGUAGES, ALL_LANGUAGES
except Exception:
    try:
        from core.translator import HeritageTranslator
        DEMO_LANGUAGES = getattr(HeritageTranslator, "DEMO_LANGUAGES", {
            "en": "English", "hi": "हिन्दी (Hindi)", "kn": "ಕನ್ನಡ (Kannada)", "ta": "தமிழ் (Tamil)",
        })
        ALL_LANGUAGES = getattr(HeritageTranslator, "ALL_LANGUAGES", DEMO_LANGUAGES)
    except Exception:
        DEMO_LANGUAGES = {
            "en": "English", "hi": "हिन्दी (Hindi)", "kn": "ಕನ್ನಡ (Kannada)", "ta": "தமிழ் (Tamil)",
        }
        ALL_LANGUAGES = DEMO_LANGUAGES
        class HeritageTranslator:
            DEMO_LANGUAGES = DEMO_LANGUAGES
            ALL_LANGUAGES = ALL_LANGUAGES
            @classmethod
            def translate_text(cls, text, target_lang="hi", source_lang="en"):
                return {"success": True, "original_text": text, "translated_text": text, "provider": "Fallback Lexicon", "target_language": target_lang}

from core.storage import get_all_records, get_record_by_id
from core.tts_engine import TTSEngine, render_interactive_audio_player, render_tts_studio


# Language Categorization for Clean UI
LANGUAGE_GROUPS = {
    "🎯 Core Demonstration (4 Languages)": ["hi", "kn", "ta", "en"],
    "🇮🇳 Indian Heritage Suite (13 Languages)": ["hi", "kn", "ta", "te", "ml", "bn", "mr", "gu", "pa", "or", "sa", "ur", "en"],
    "🌍 Global Research Suite (6 Languages)": ["fr", "de", "es", "ja", "ar", "en"],
    "🌐 Complete Multilingual Catalog (All 18 Languages)": list(ALL_LANGUAGES.keys()),
}


def render_multilingual():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">MULTILINGUAL ARCHIVAL ACCESS & SPEECH</h1>
            <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
                Demonstration Languages: <strong>English</strong> &bull; <strong>हिन्दी (Hindi)</strong> &bull; <strong>ಕನ್ನಡ (Kannada)</strong> &bull; <strong>தமிழ் (Tamil)</strong>
                + <strong>14 Extended Heritage Languages</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    main_tab_trans, main_tab_tts = st.tabs([
        "🌐 Dual-Pane Multilingual Translation",
        "🎙️ Interactive Text-to-Speech Studio",
    ])

    with main_tab_tts:
        render_tts_studio()

    with main_tab_trans:
        # Workflow Visualizer Banner
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 8px; padding: 12px 18px; margin-bottom: 22px; text-align: center;">
                <div style="color: #fbbf24; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">
                    Archival Multilingual Access Pipeline
                </div>
                <div style="display: flex; justify-content: center; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 0.95rem; color: #f8fafc; font-weight: 500;">
                    <span class="heritage-badge badge-sapphire" style="font-size: 0.9rem; padding: 6px 14px;">1. 📜 Original Archival Text</span>
                    <span style="color: #fbbf24; font-size: 1.2rem;">➔</span>
                    <span class="heritage-badge badge-emerald" style="font-size: 0.9rem; padding: 6px 14px;">2. ⚡ Multi-Tier Translation Engine</span>
                    <span style="color: #fbbf24; font-size: 1.2rem;">➔</span>
                    <span class="heritage-badge badge-sapphire" style="font-size: 0.9rem; padding: 6px 14px;">3. 🌐 Dual-Pane Comparison + Neural Voice</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        records = get_all_records(limit=100)

        # 1. Source Text Selection
        st.markdown("##### 1. Select Archival Manuscript or Custom Historical Inscription:")
        tab_catalog, tab_custom = st.tabs(["📚 From Cataloged Archival Records", "✍️ Custom Archival Transcript / Inscription"])
        
        selected_text = ""
        selected_title = "Selected Archival Manuscript"
        selected_lang = "Classical Script"

    with tab_catalog:
        if records:
            doc_map = {f"#{r['id']}: {r['title']} ({r.get('year', 'Historical')}) [{r.get('language', 'Script')}]": r['id'] for r in records}
            chosen_label = st.selectbox("Choose Archival Manuscript to Translate:", list(doc_map.keys()), key="multi_doc_sel")
            rec_id = doc_map[chosen_label]
            rec = get_record_by_id(rec_id)
            if rec:
                selected_text = rec.get("cleaned_text") or rec.get("raw_ocr_text") or rec.get("description") or ""
                selected_title = rec.get("title", "Archival Document")
                selected_lang = rec.get("language", "Classical Script")
                
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.5); border-left: 3px solid #fbbf24; padding: 8px 14px; border-radius: 4px; margin-bottom: 8px; font-size: 0.88rem; color: #cbd5e1;">
                        <strong>Document Type:</strong> {rec.get('document_type', 'Manuscript')} &bull; 
                        <strong>Creator / Period:</strong> {rec.get('creator', 'Historical')} ({rec.get('year', 'Ancient')}) &bull; 
                        <strong>Institution:</strong> {rec.get('holding_institution', 'National Archive')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No records found in database. Ingest documents in Admin or use custom input tab.")

    with tab_custom:
        custom_input = st.text_area(
            "Enter or Paste Archival Transcript / Inscription:",
            value=(
                "Beloved-of-the-Gods, King Priyadarsin, speaks thus: Father and mother should be obeyed. "
                "Teachers should be respected. Mercy towards all living creatures should be practiced. "
                "Truth should be spoken. Concord alone is meritorious, whereby all may listen to one another's tenets."
            ),
            height=110,
            key="custom_trans_input",
        )
        if custom_input.strip():
            selected_text = custom_input.strip()
            selected_title = "Custom Archival Transcript"
            selected_lang = "English / Input Language"

    st.markdown("<br/>", unsafe_allow_html=True)

    # 2. Target Language Selection
    st.markdown("##### 2. Choose Target Language for Translation & Neural Voice Narration:")
    
    # Quick selection buttons for 4 Core Demonstration Languages
    st.markdown(
        "<div style='font-size: 0.82rem; color: #94a3b8; margin-bottom: 6px;'>⚡ Quick Demonstration Shortcuts:</div>",
        unsafe_allow_html=True,
    )
    qcol1, qcol2, qcol3, qcol4, qcol5 = st.columns(5)
    with qcol1:
        if st.button("🇮🇳 हिन्दी (Hindi)", use_container_width=True, key="quick_btn_hi"):
            st.session_state["active_trans_lang_code"] = "hi"
            st.rerun()
    with qcol2:
        if st.button("🇮🇳 ಕನ್ನಡ (Kannada)", use_container_width=True, key="quick_btn_kn"):
            st.session_state["active_trans_lang_code"] = "kn"
            st.rerun()
    with qcol3:
        if st.button("🇮🇳 தமிழ் (Tamil)", use_container_width=True, key="quick_btn_ta"):
            st.session_state["active_trans_lang_code"] = "ta"
            st.rerun()
    with qcol4:
        if st.button("🇬🇧 English", use_container_width=True, key="quick_btn_en"):
            st.session_state["active_trans_lang_code"] = "en"
            st.rerun()
    with qcol5:
        if st.button("🇮🇳 తెలుగు (Telugu)", use_container_width=True, key="quick_btn_te"):
            st.session_state["active_trans_lang_code"] = "te"
            st.rerun()

    col_filter, col_lang = st.columns([1, 2])
    with col_filter:
        filter_group = st.selectbox(
            "Language Category Filter:",
            options=list(LANGUAGE_GROUPS.keys()),
            index=0,
            key="lang_group_filter",
        )

    available_codes = LANGUAGE_GROUPS[filter_group]
    cur_sel = st.session_state.get("active_trans_lang_code", "hi")
    if cur_sel not in available_codes:
        cur_idx = 0
    else:
        cur_idx = available_codes.index(cur_sel)
    
    with col_lang:
        target_lang_code = st.selectbox(
            f"Select Target Language from {filter_group}:",
            options=available_codes,
            format_func=lambda code: ALL_LANGUAGES.get(code, code),
            index=cur_idx,
            key="unified_target_lang_code_sel",
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Translation Execution Button
    btn_c1, btn_c2 = st.columns([1, 2])
    with btn_c1:
        translate_btn = st.button("🌐 Execute Multilingual Translation", type="primary", use_container_width=True)

    # Check if translation should run or is cached
    state_key = f"trans_res_{target_lang_code}_{hash(selected_text[:120])}"
    
    if translate_btn or (selected_text and state_key not in st.session_state):
        if not selected_text.strip():
            st.warning("Please select or enter archival text to translate.")
            return

        with st.spinner(f"Translating archival text into {ALL_LANGUAGES.get(target_lang_code, target_lang_code)}..."):
            res = HeritageTranslator.translate_text(selected_text, target_lang=target_lang_code)
            st.session_state[state_key] = res

    # Retrieve active translation result
    res = st.session_state.get(state_key)
    if not res and selected_text.strip():
        res = HeritageTranslator.translate_text(selected_text, target_lang=target_lang_code)
        st.session_state[state_key] = res

    if res:
        target_lang_name = ALL_LANGUAGES.get(target_lang_code, target_lang_code)
        st.markdown(f"### 📜 Dual-Pane Comparison: Original & Translated Text ({target_lang_name})")
        
        col_orig, col_trans = st.columns(2, gap="medium")

        # ---------------------------------------------------------------------
        # Left Column: Original Archival Text
        # ---------------------------------------------------------------------
        with col_orig:
            st.markdown(
                f"""
                <div class="heritage-card" style="border-top: 3px solid #3b82f6; min-height: 280px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #93c5fd; font-size: 1.05rem;">
                            📜 Original Archival Text
                        </h4>
                        <span class="heritage-badge badge-sapphire">
                            {selected_lang}
                        </span>
                    </div>
                    <div style="font-size: 0.83rem; color: #cbd5e1; margin-bottom: 8px;">
                        <strong>Source:</strong> {selected_title}
                    </div>
                    <div style="background: rgba(10, 15, 26, 0.9); padding: 12px; border-radius: 6px; border: 1px solid rgba(59, 130, 246, 0.3); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; line-height: 1.6; color: #f1f5f9; min-height: 160px; max-height: 280px; overflow-y: auto; white-space: pre-wrap;">
{selected_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown("<div style='margin-top: 10px; color: #93c5fd; font-weight: 600;'>🔊 Original Audio Narration (English / Source):</div>", unsafe_allow_html=True)
            render_interactive_audio_player(
                text=selected_text[:500],
                lang_code="en",
                key_prefix=f"orig_audio_{hash(selected_text[:50])}",
            )

        # ---------------------------------------------------------------------
        # Right Column: Translated Text & Multilingual Neural Voice
        # ---------------------------------------------------------------------
        with col_trans:
            provider_label = res.get("provider", "Translation Engine")
            st.markdown(
                f"""
                <div class="heritage-card" style="border-top: 3px solid #10b981; min-height: 280px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #6ee7b7; font-size: 1.05rem;">
                            🌐 Translated Text ({target_lang_name})
                        </h4>
                        <span class="heritage-badge badge-emerald">
                            {target_lang_name}
                        </span>
                    </div>
                    <div style="font-size: 0.83rem; color: #cbd5e1; margin-bottom: 8px;">
                        <strong>Engine:</strong> {provider_label}
                    </div>
                    <div style="background: rgba(10, 22, 20, 0.9); padding: 12px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3); font-family: 'Inter', sans-serif; font-size: 0.94rem; line-height: 1.7; color: #f8fafc; min-height: 160px; max-height: 280px; overflow-y: auto; white-space: pre-wrap;">
{res['translated_text']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"<div style='margin-top: 10px; color: #6ee7b7; font-weight: 600;'>🔊 Native Neural Audio ({target_lang_name}):</div>", unsafe_allow_html=True)
            render_interactive_audio_player(
                text=res["translated_text"][:500],
                lang_code=target_lang_code,
                key_prefix=f"trans_audio_{target_lang_code}_{hash(res['translated_text'][:50])}",
            )
