"""
Digital Heritage Archive - AI Research Assistant View
Source-grounded RAG inquiry engine grounded strictly in primary archival documents and OCR transcripts.
Guarantees anti-hallucination, strict citations, and displays all supporting archival sources below every answer.
"""

import streamlit as st
from PIL import Image
from pathlib import Path
import textwrap
from core.rag_engine import GroundedResearchAssistant
from core.tts_engine import TTSEngine
from core.translator import HeritageTranslator
from config import SUPPORTED_LANGUAGES


def render_ai_assistant():
    header_html = textwrap.dedent("""
    <div style="text-align: center; margin-bottom: 22px;">
        <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">AI RESEARCH ASSISTANT</h1>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
            Source-Grounded Archival Intelligence &bull; FAISS Semantic Retrieval &bull; OCR Grounding &bull; Anti-Hallucination Guard
        </p>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # Workflow Diagram Visualizer
    with st.expander("🔍 System Architecture: Source-Grounded RAG Pipeline Workflow", expanded=False):
        st.markdown(
            """
            ```mermaid
            graph LR
                Q[User Question] --> E[Query Embedding 384-dim]
                E --> F[FAISS Vector Index]
                F --> R[Retrieve Relevant Records]
                R --> C[Build OCR Context & Grounding Check]
                C --> A[Generate Source-Grounded Answer]
                A --> S[Display Supporting Sources]
            ```
            """,
            unsafe_allow_html=True,
        )

    assistant = GroundedResearchAssistant()

    # Preset Sample Inquiries for Research
    st.markdown("##### 💡 Preset Archival Inquiries (Click to Test):")
    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    preset_query = None

    with pcol1:
        if st.button("📜 Ashoka: Religious Harmony", use_container_width=True):
            preset_query = "What principles of religious harmony and speech restraint were decreed by Emperor Ashoka?"
    with pcol2:
        if st.button("👑 Akbar: Sulh-i-Kul & Land", use_container_width=True):
            preset_query = "What did Emperor Akbar decree regarding universal peace (Sulh-i-Kul) and temple land endowments?"
    with pcol3:
        if st.button("🏛️ Chola: Agrarian Charters", use_container_width=True):
            preset_query = "How did the Chola dynasty structure village boundary demarcations and temple land grants?"
    with pcol4:
        if st.button("🚫 Test Non-Existent Subject", use_container_width=True, help="Tests the anti-hallucination guard"):
            preset_query = "What records exist regarding supersonic stealth aircraft in the medieval Vijayanagara empire?"

    # User Query Input
    query_text = preset_query if preset_query else ""
    user_query = st.text_input(
        "Enter your historical research question:",
        value=query_text,
        placeholder="e.g. 'What were the tax exemptions specified in the copper plate charter?', 'How did Ashoka describe inter-religious restraint?'",
        key="ai_research_query_input",
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_query = st.button("🔬 Ask AI Assistant", type="primary", use_container_width=True)

    # Execute Grounded RAG Workflow
    if run_query or preset_query:
        if not user_query.strip():
            st.warning("Please enter a research question.")
            return

        with st.spinner("Embedding query with 384-dim vector, querying FAISS index, and verifying primary OCR sources..."):
            result = assistant.answer_query(user_query)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Check if Sufficient Supporting Context Was Found
        if not result["has_sufficient_context"]:
            st.markdown(
                f"""
                <div class="heritage-card" style="border-left: 5px solid #ef4444; background: rgba(30, 15, 15, 0.85);">
                    <div style="display:flex; align-items:center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.5rem;">🛡️</span>
                        <h3 style="margin: 0; color: #f87171; font-family: 'Inter', sans-serif; font-size: 1.15rem;">
                            Anti-Hallucination Guard Triggered
                        </h3>
                    </div>
                    <p style="font-size: 1.1rem; color: #fecaca; font-weight: 600; margin: 0;">
                        "{result['answer']}"
                    </p>
                    <p style="color: #94a3b8; font-size: 0.88rem; margin: 8px 0 0 0;">
                        The AI Research Assistant is strictly source-grounded and will not fabricate or extrapolate facts when supporting primary archival evidence is missing from the database.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # Render Grounded Answer
        st.markdown("### 🏛️ Source-Grounded Historical Analysis")
        st.markdown(
            f"""
            <div class="heritage-card" style="border-left: 5px solid #fbbf24; padding: 22px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; flex-wrap: wrap;">
                    <span class="heritage-badge badge-emerald">
                        ✅ Verified Grounded Synthesis
                    </span>
                    <span class="heritage-badge badge-sapphire">
                        📚 {result['sources_count']} Supporting Primary Sources
                    </span>
                </div>
                <div style="color: #f8fafc; font-size: 1rem; line-height: 1.7;">
                    {result['answer']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Action Toolbar for Answer: Listen, Translate, Copy
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            if st.button("🔊 Read Answer Aloud (TTS Narration)", key="tts_rag_btn", use_container_width=True):
                tts = TTSEngine()
                with st.spinner("Synthesizing answer speech..."):
                    tts_res = tts.generate_audio(result["answer"][:600], rate=140, voice_gender="female")
                    if tts_res.get("success") and tts_res.get("audio_path"):
                        st.audio(tts_res["audio_path"])
                        st.success("Narration audio generated successfully!")
                    else:
                        st.error(f"TTS Note: {tts_res.get('error')}")

        with act_col2:
            with st.expander("🌐 Translate Historical Synthesis", expanded=False):
                t_lang = st.selectbox(
                    "Select Translation Language:",
                    options=list(SUPPORTED_LANGUAGES.keys()),
                    format_func=lambda x: SUPPORTED_LANGUAGES[x],
                    index=1,
                    key="rag_trans_lang_sel",
                )
                if st.button("Translate Answer", key="rag_trans_btn", use_container_width=True):
                    with st.spinner(f"Translating into {SUPPORTED_LANGUAGES[t_lang]}..."):
                        t_res = HeritageTranslator.translate_text(result["answer"], target_lang=t_lang)
                        if t_res.get("success"):
                            st.markdown(
                                f"""
                                <div style="background: rgba(15, 23, 42, 0.9); padding: 12px; border-radius: 6px; border: 1px solid #fbbf24;">
                                    <strong style="color: #fbbf24;">Translation ({SUPPORTED_LANGUAGES[t_lang]}):</strong><br/>
                                    <p style="color: #f1f5f9; font-size: 0.95rem; margin-top: 6px; white-space: pre-wrap;">{t_res['translated_text']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        st.markdown("---")

        # =====================================================================
        # DISPLAY SUPPORTING SOURCE RECORDS BELOW EVERY ANSWER (Mandatory)
        # =====================================================================
        st.markdown(f"### 📚 Supporting Primary Source Records ({len(result['supporting_sources'])})")
        st.caption("Every fact generated above is grounded in the following verified archival documents cataloged in the repository:")

        for src in result["supporting_sources"]:
            s_idx = src["source_index"]
            s_id = src["record_id"]
            title = src["title"]
            creator = src["creator"]
            year = src["year"]
            doc_type = src["document_type"]
            language = src["language"]
            institution = src["institution"]
            accession = src["accession_number"]
            rights = src["rights"]
            rel_pct = src["relevance_percentage"]
            excerpt = src["excerpt"]
            raw_path = src.get("saved_file_path")
            proc_path = src.get("processed_file_path")

            with st.container():
                source_card_html = textwrap.dedent(f"""
                <div class="heritage-card" style="margin-bottom: 14px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap: wrap;">
                        <h4 style="margin: 0; color: #fbbf24; font-size: 1.15rem;">
                            [Source {s_idx}]: {title}
                        </h4>
                        <span class="heritage-badge badge-emerald">
                            ⚡ {rel_pct:.1f}% Relevance
                        </span>
                    </div>
                    <div style="margin: 8px 0;">
                        <span class="heritage-badge">👤 Creator: <strong>{creator}</strong></span>
                        <span class="heritage-badge">📅 Year: <strong>{year}</strong></span>
                        <span class="heritage-badge">📜 Type: <strong>{doc_type}</strong></span>
                        <span class="heritage-badge">🌐 Language: <strong>{language}</strong></span>
                        <span class="heritage-badge">🏛️ Institution: <strong>{institution}</strong></span>
                        <span class="heritage-badge">🆔 Accession: <code>{accession}</code></span>
                        <span class="heritage-badge">🛡️ Rights: <strong>{rights}</strong></span>
                    </div>
                    <div style="background: rgba(11, 17, 32, 0.85); padding: 12px 14px; border-left: 3px solid #10b981; border-radius: 4px; margin-top: 8px;">
                        <strong style="color: #6ee7b7; font-size: 0.85rem; text-transform: uppercase;">📑 Grounded OCR Transcript Excerpt:</strong><br/>
                        <p style="color: #f1f5f9; font-style: italic; font-size: 0.92rem; margin: 4px 0 0 0; line-height: 1.5;">
                            "{excerpt}"
                        </p>
                    </div>
                </div>
                """)
                st.markdown(source_card_html, unsafe_allow_html=True)

                # Action button to inspect source in Digital Document Viewer
                src_col1, src_col2 = st.columns([1, 4])
                with src_col1:
                    if st.button(f"🔍 Inspect [Source {s_idx}] in Document Viewer", key=f"rag_view_src_{s_id}_{s_idx}", use_container_width=True):
                        st.session_state["selected_doc_id"] = s_id
                        st.session_state["nav_target"] = "Document Viewer"
                        st.session_state["_sidebar_nav_radio_widget"] = "Document Viewer"
                        st.session_state["current_page"] = "Document Viewer"
                        st.rerun()

                st.markdown("<br/>", unsafe_allow_html=True)
