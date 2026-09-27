"""
Digital Heritage Archive - Digital Document Viewer
High-resolution side-by-side manuscript viewer with metadata breakdown,
instant Text-to-Speech narration, and live translation.
"""

import streamlit as st
from PIL import Image
from pathlib import Path
from core.storage import get_all_documents, get_document_by_id
from core.tts_engine import TTSEngine
from core.translator import HeritageTranslator
from config import SUPPORTED_LANGUAGES


def render_document_viewer():
    st.markdown("## 📜 Digital Manuscript & Document Viewer")
    st.markdown("Inspect high-resolution archival scans alongside verified transcripts, metadata, and voice narration.")

    docs = get_all_documents()
    if not docs:
        st.warning("No archival records found. Please ingest documents in the Ingestion Pipeline or load sample data.")
        return

    # Document Selection
    doc_options = {f"#{d['id']} - {d['title']} ({d.get('approx_year', 'Historical')})": d['id'] for d in docs}
    selected_label = st.selectbox("Select Archival Record to Inspect:", list(doc_options.keys()))
    selected_id = doc_options[selected_label]

    doc = get_document_by_id(selected_id)
    if not doc:
        st.error("Failed to load document.")
        return

    # Metadata Badges Bar
    st.markdown(
        f"""
        <div class="heritage-card">
            <span class="heritage-badge">🏛️ {doc.get('era', 'Era')}</span>
            <span class="heritage-badge">🔖 {doc.get('category', 'Category')}</span>
            <span class="heritage-badge">📍 {doc.get('origin_region', 'India')}</span>
            <span class="heritage-badge">📅 {doc.get('approx_year', 'N/A')}</span>
            <span class="heritage-badge">🛡️ {doc.get('preservation_condition', 'Preserved')}</span>
            <span class="heritage-badge">🆔 Accession: {doc.get('accession_number', 'DHA-001')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🖼️ Original Archival Scan")
        img_path = doc.get("processed_file_path") or doc.get("raw_file_path")
        if img_path and Path(img_path).exists():
            try:
                img = Image.open(img_path)
                st.image(img, caption=f"Archival Record: {doc['title']}", use_container_width=True)
            except Exception:
                st.info(f"File stored at: `{img_path}`")
        else:
            st.info("Visual scan not available or path moved.")

    with col2:
        st.markdown("### 📝 Verified Transcript & Audio")
        transcript = doc.get("cleaned_text") or doc.get("extracted_text") or "No transcript available."
        st.text_area("Archival Text", value=transcript, height=260, disabled=True)

        # Audio Narration Section (TTS)
        st.markdown("#### 🎙️ Voice Narration (Text-to-Speech)")
        tcol1, tcol2 = st.columns([2, 1])
        with tcol1:
            speech_rate = st.slider("Playback Speed", min_value=100, max_value=200, value=140, step=10)
        with tcol2:
            voice_choice = st.selectbox("Voice", ["Female", "Male"])

        if st.button("🔊 Generate Audio Narration", use_container_width=True):
            tts = TTSEngine()
            with st.spinner("Synthesizing historical reading..."):
                res = tts.generate_audio(transcript, rate=speech_rate, voice_gender=voice_choice.lower())
                if res["success"] and res["audio_path"]:
                    st.audio(res["audio_path"])
                    st.success("Audio narration generated successfully!")
                else:
                    st.error(f"TTS Error: {res.get('error')}")

        st.markdown("---")

        # Multilingual Translation Section
        st.markdown("#### 🌐 Instant Translation")
        trans_col1, trans_col2 = st.columns([2, 1])
        with trans_col1:
            target_lang = st.selectbox(
                "Translate Transcript into:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: SUPPORTED_LANGUAGES[x],
                index=1,  # Default Hindi
            )
        with trans_col2:
            st.write("")
            st.write("")
            translate_btn = st.button("Translate", use_container_width=True)

        if translate_btn:
            with st.spinner(f"Translating into {SUPPORTED_LANGUAGES[target_lang]}..."):
                trans_res = HeritageTranslator.translate_text(transcript, target_lang=target_lang)
                if trans_res["success"]:
                    st.markdown(f"**Translated ({SUPPORTED_LANGUAGES[target_lang]}):**")
                    st.text_area("Translation", value=trans_res["translated_text"], height=160)
                else:
                    st.error(f"Translation Error: {trans_res.get('error')}")
