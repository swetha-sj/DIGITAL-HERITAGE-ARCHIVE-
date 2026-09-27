"""
Digital Heritage Archive - Institutional Archive Management View
Curator analytics, preservation condition monitoring, and catalog export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from core.storage import get_stats, get_all_documents
from utils.sample_loader import bootstrap_sample_data
from core.search_engine import HybridSearchEngine


def render_institutional_admin():
    st.markdown("## 🏛️ Institutional Archive Management & Curator Hub")
    st.markdown("Monitor archival preservation metrics, collection statistics, and collection integrity.")

    stats = get_stats()

    # Top Metric Cards
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Total Documents", stats["total_documents"])
    with mcol2:
        st.metric("Oral Audio/Video Items", stats["total_multimedia"])
    with mcol3:
        st.metric("Cataloged Eras", len(stats["era_distribution"]))
    with mcol4:
        st.metric("Archival Standards", "Dublin Core (ISO 15836)")

    st.markdown("---")

    # Analytics Charts
    ccol1, ccol2 = st.columns(2)

    with ccol1:
        st.markdown("### 📊 Distribution Across Historical Eras")
        if stats["era_distribution"]:
            era_df = pd.DataFrame(
                list(stats["era_distribution"].items()), columns=["Era", "Document Count"]
            )
            fig_era = px.bar(
                era_df,
                x="Era",
                y="Document Count",
                color="Era",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Antique,
            )
            fig_era.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig_era, use_container_width=True)
        else:
            st.info("No era data yet.")

    with ccol2:
        st.markdown("### 🛡️ Preservation Condition Status")
        if stats["condition_distribution"]:
            cond_df = pd.DataFrame(
                list(stats["condition_distribution"].items()),
                columns=["Condition", "Count"],
            )
            fig_cond = px.pie(
                cond_df,
                names="Condition",
                values="Count",
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Gold,
            )
            fig_cond.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_cond, use_container_width=True)
        else:
            st.info("No condition data yet.")

    st.markdown("---")

    # Archival Administration Actions
    st.markdown("### ⚙️ Curator Maintenance & Controls")
    act_col1, act_col2 = st.columns(2)

    with act_col1:
        st.markdown("#### 🔄 Sample Archive Bootstrapper")
        st.caption("Re-seed or ensure built-in historical demo documents are populated in SQLite and FAISS.")
        if st.button("🚀 Load / Reset Heritage Demo Data", use_container_width=True):
            with st.spinner("Bootstrapping sample records..."):
                count = bootstrap_sample_data()
                st.success(f"Archival records synchronized! Total documents: {count}")
                st.rerun()

    with act_col2:
        st.markdown("#### ⚡ Re-build FAISS Vector Index")
        st.caption("Regenerate Sentence Transformers embeddings for all cataloged records.")
        if st.button("⚡ Rebuild Vector Embeddings", use_container_width=True):
            with st.spinner("Reindexing FAISS embeddings..."):
                engine = HybridSearchEngine()
                indexed_count = engine.reindex_all_documents()
                st.success(f"Reindexed {indexed_count} documents in FAISS vector store!")

    st.markdown("---")

    # Export Collection
    st.markdown("### 📥 Export Archival Catalog")
    docs = get_all_documents()
    if docs:
        df_docs = pd.DataFrame(docs)
        csv_data = df_docs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download Archival Catalog (CSV)",
            data=csv_data,
            file_name="digital_heritage_archive_catalog.csv",
            mime="text/csv",
            use_container_width=True,
        )
