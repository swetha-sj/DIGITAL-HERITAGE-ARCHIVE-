"""
Digital Heritage Archive - AI Research Hub & RAG Assistant
Provides conversational RAG inquiry grounded strictly in archival records
with verified citations and multi-language translation.
"""

import streamlit as st
from core.rag_engine import RAGResearchEngine
from core.translator import HeritageTranslator
from config import SUPPORTED_LANGUAGES


def render_ai_research_hub():
    st.markdown("## 🤖 AI Heritage Research Assistant (RAG)")
    st.markdown(
        "Ask complex historical and comparative questions. The assistant retrieves primary sources from the archive "
        "and synthesizes answers with strict citation grounding."
    )

    rag = RAGResearchEngine()

    # Preset Sample Inquiries for rapid demo
    st.markdown("**Sample Research Inquiries:**")
    pcol1, pcol2, pcol3 = st.columns(3)
    preset_query = None
    with pcol1:
        if st.button("📜 Ashoka's Edicts on Religious Harmony", use_container_width=True):
            preset_query = "What were Emperor Ashoka's core principles on religious tolerance and speech restraint?"
    with pcol2:
        if st.button("👑 Akbar's Sulh-i-Kul & Land Grants", use_container_width=True):
            preset_query = "What did Emperor Akbar decree regarding universal peace and temple land endowments?"
    with pcol3:
        if st.button("🏛️ Chola Temple Administration Grants", use_container_width=True):
            preset_query = "How did Rajaraja Chola structure temple endowments and administrative oversight?"

    query_val = preset_query if preset_query else ""

    user_query = st.text_input(
        "Enter your historical research question:",
        value=query_val,
        placeholder="e.g. Compare the religious tolerance policies of the Mauryan and Mughal empires...",
    )

    if st.button("🔬 Analyze & Synthesize Findings", use_container_width=True) or preset_query:
        if not user_query.strip():
            st.warning("Please enter a research question.")
            return

        with st.spinner("Retrieving archival manuscripts and synthesizing grounded response..."):
            response = rag.answer_query(user_query)

        st.markdown("### 🏛️ Archival Synthesis & Findings")
        st.markdown(
            f"""
            <div class="heritage-card">
                {response['answer']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Citations Section
        st.markdown(f"### 📚 Verified Source References ({response['sources_count']})")
        if response.get("citations"):
            for cit in response["citations"]:
                st.markdown(
                    f"""
                    <div class="citation-box">
                        <strong>[Source {cit['source_id']}]: {cit['title']}</strong><br/>
                        <small>🏛️ <strong>Era:</strong> {cit['era']} | 🏷️ <strong>Category:</strong> {cit['category']} | 🆔 <strong>Accession:</strong> <code>{cit['accession_number']}</code></small><br/>
                        <p style="margin-top: 6px; font-style: italic; color: #cbd5e1;">"{cit['snippet']}"</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No specific archival documents were cited.")

        # Multi-language translation of the synthesized answer
        st.markdown("---")
        st.markdown("#### 🌐 Translate Research Findings")
        tcol1, tcol2 = st.columns([3, 1])
        with tcol1:
            trans_lang = st.selectbox(
                "Translate synthesis into:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: SUPPORTED_LANGUAGES[x],
                index=1,
            )
        with tcol2:
            st.write("")
            st.write("")
            if st.button("Translate Synthesis", use_container_width=True):
                with st.spinner("Translating findings..."):
                    tres = HeritageTranslator.translate_text(response["answer"], target_lang=trans_lang)
                    if tres["success"]:
                        st.markdown(
                            f"""
                            <div class="heritage-card">
                                <strong>Translated Findings ({SUPPORTED_LANGUAGES[trans_lang]}):</strong><br/>
                                {tres['translated_text']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"Translation Error: {tres.get('error')}")
