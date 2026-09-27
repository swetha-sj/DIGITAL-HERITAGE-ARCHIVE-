"""
Digital Heritage Archive - Ingestion Pipeline View
Handles document upload, computer vision preprocessing, OCR extraction,
text cleaning, and Dublin Core metadata cataloging.
"""

import streamlit as st
from PIL import Image
import uuid
from pathlib import Path
from config import RAW_DOCS_DIR, PROCESSED_IMAGES_DIR, ARCHIVAL_ERAS, ARCHIVAL_CATEGORIES, PRESERVATION_CONDITIONS
from core.preprocessor import ImagePreprocessor
from core.ocr_engine import OCREngine
from core.text_cleaner import TextCleaner
from core.storage import insert_document, insert_metadata
from core.search_engine import HybridSearchEngine


def render_ingestion_pipeline():
    st.markdown("## 📥 Document Ingestion & Processing Pipeline")
    st.markdown(
        "Upload physical manuscript scans, historical charters, or PDFs to restore, OCR, and catalog them into the archive."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 1. Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a manuscript image or scanned document",
            type=["png", "jpg", "jpeg", "tiff", "bmp", "pdf"],
            help="Supported formats: PNG, JPG, TIFF, BMP, PDF",
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            file_ext = Path(file_name).suffix.lower()

            st.success(f"Uploaded: `{file_name}` ({len(file_bytes) / 1024:.1f} KB)")

            # Check if PDF or Image
            if file_ext == ".pdf":
                st.info("PDF document detected. PyMuPDF will be used for extraction.")
                # Save raw PDF
                raw_path = RAW_DOCS_DIR / f"{uuid.uuid4().hex[:8]}_{file_name}"
                with open(raw_path, "wb") as f:
                    f.write(file_bytes)
                st.session_state["ingest_raw_path"] = str(raw_path)
                st.session_state["ingest_file_type"] = "PDF Document"
                st.session_state["ingest_original_name"] = file_name
            else:
                img = Image.open(uploaded_file)
                st.image(img, caption="Original Document Upload", use_container_width=True)

                raw_path = RAW_DOCS_DIR / f"{uuid.uuid4().hex[:8]}_{file_name}"
                img.save(raw_path)
                st.session_state["ingest_raw_path"] = str(raw_path)
                st.session_state["ingest_file_type"] = "Image Scan"
                st.session_state["ingest_original_name"] = file_name
                st.session_state["ingest_pil_img"] = img

    with col2:
        st.markdown("### 2. Image Preprocessing")
        if "ingest_pil_img" in st.session_state:
            st.caption("Apply computer vision filters to optimize aged parchment for OCR.")

            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                do_deskew = st.checkbox("Auto-Deskew (Rotate to 0°)", value=True)
                do_contrast = st.checkbox("CLAHE Contrast Enhancement", value=True)
            with col_opt2:
                do_denoise = st.checkbox("Noise Reduction Filter", value=True)
                do_binarize = st.checkbox("Adaptive Gaussian Binarization", value=False)

            if st.button("✨ Apply Enhancement Filters", use_container_width=True):
                with st.spinner("Processing computer vision algorithms..."):
                    processed_cv, audit = ImagePreprocessor.process_pipeline(
                        st.session_state["ingest_pil_img"],
                        do_deskew=do_deskew,
                        do_contrast=do_contrast,
                        do_denoise=do_denoise,
                        do_binarize=do_binarize,
                    )
                    processed_pil = ImagePreprocessor.convert_to_pil(processed_cv)
                    proc_path = PROCESSED_IMAGES_DIR / f"proc_{Path(st.session_state['ingest_raw_path']).name}"
                    processed_pil.save(proc_path)
                    st.session_state["ingest_processed_path"] = str(proc_path)
                    st.session_state["ingest_processed_pil"] = processed_pil
                    st.session_state["ingest_audit"] = audit

            if "ingest_processed_pil" in st.session_state:
                st.image(
                    st.session_state["ingest_processed_pil"],
                    caption=f"Enhanced Output (Deskew: {st.session_state.get('ingest_audit', {}).get('deskew_angle', 0)}°)",
                    use_container_width=True,
                )
        else:
            st.info("Upload a document on the left to activate computer vision filters.")

    st.markdown("---")

    # OCR and Text Cleaning Section
    st.markdown("### 3. OCR & Text Cleaning")
    ocr_col1, ocr_col2 = st.columns([1, 1])

    with ocr_col1:
        st.markdown("**OCR Transcript Extraction**")
        ocr_lang = st.selectbox("OCR Language Engine", ["eng (English)", "hin (Hindi)", "san (Sanskrit)", "tam (Tamil)"])
        lang_code = ocr_lang.split()[0]

        if st.button("🔍 Run OCR Extraction", use_container_width=True):
            ocr_engine = OCREngine()
            with st.spinner("Running optical character recognition..."):
                if st.session_state.get("ingest_file_type") == "PDF Document":
                    res = ocr_engine.extract_from_pdf(st.session_state["ingest_raw_path"], lang=lang_code)
                elif "ingest_processed_pil" in st.session_state:
                    res = ocr_engine.extract_from_image(st.session_state["ingest_processed_pil"], lang=lang_code)
                elif "ingest_pil_img" in st.session_state:
                    res = ocr_engine.extract_from_image(st.session_state["ingest_pil_img"], lang=lang_code)
                else:
                    res = {"success": False, "error": "Please upload a document first.", "text": ""}

                if res.get("success"):
                    st.session_state["raw_ocr_text"] = res["text"]
                    st.success(f"OCR Complete! Confidence: {res.get('confidence', 'N/A')}%")
                else:
                    st.warning(f"OCR Status: {res.get('error', 'Execution completed with fallback text.')}")
                    if not res.get("text"):
                        st.session_state["raw_ocr_text"] = ""

        raw_text = st.text_area(
            "Raw OCR Text Output",
            value=st.session_state.get("raw_ocr_text", ""),
            height=200,
        )

    with ocr_col2:
        st.markdown("**Text Cleaning & Standardization**")
        if st.button("🧹 Clean & Normalize Text", use_container_width=True):
            clean_res = TextCleaner.clean(raw_text)
            st.session_state["cleaned_text"] = clean_res["cleaned_text"]
            st.info(f"Cleaned! Reduction: {clean_res['reduction_percentage']}% scanning noise removed.")

        cleaned_text = st.text_area(
            "Final Cleaned Archival Transcript",
            value=st.session_state.get("cleaned_text", raw_text),
            height=200,
        )

    st.markdown("---")

    # Metadata Entry & Cataloging
    st.markdown("### 4. Dublin Core Metadata Entry & Storage")
    with st.form("metadata_entry_form"):
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            title = st.text_input("Document Title *", placeholder="e.g. Royal Inscription of Rajaraja Chola")
            era = st.selectbox("Historical Era *", ARCHIVAL_ERAS)
            dynasty = st.text_input("Dynasty / Historical Period", placeholder="e.g. Chola Dynasty")
        with mcol2:
            category = st.selectbox("Archival Category *", ARCHIVAL_CATEGORIES)
            approx_year = st.text_input("Approximate Date / Year", placeholder="e.g. 1010 CE or 3rd Century BCE")
            region = st.text_input("Origin Region / Location", placeholder="e.g. Thanjavur, Tamil Nadu")
        with mcol3:
            condition = st.selectbox("Preservation Condition *", PRESERVATION_CONDITIONS)
            author = st.text_input("Author / Scribe / Creator", placeholder="e.g. Scribe Madhavan")
            tags = st.text_input("Search Tags (Comma separated)", placeholder="e.g. Copper Plate, Land Grant, Temple")

        submitted = st.form_submit_button("💾 Save & Index Document to Archive", use_container_width=True)
        if submitted:
            if not title:
                st.error("Document Title is required.")
            else:
                doc_uid = f"DOC-{uuid.uuid4().hex[:6].upper()}"
                raw_p = st.session_state.get("ingest_raw_path", "data/sample_data/sample.png")
                proc_p = st.session_state.get("ingest_processed_path", raw_p)
                f_type = st.session_state.get("ingest_file_type", "Image Scan")
                f_name = st.session_state.get("ingest_original_name", "document.png")

                # Insert into SQLite
                doc_id = insert_document(
                    doc_uid=doc_uid,
                    title=title,
                    original_filename=f_name,
                    file_type=f_type,
                    raw_file_path=raw_p,
                    processed_file_path=proc_p,
                    extracted_text=raw_text,
                    cleaned_text=cleaned_text,
                )

                insert_metadata(
                    doc_id=doc_id,
                    era=era,
                    category=category,
                    accession_number=f"DHA-{uuid.uuid4().hex[:6].upper()}",
                    preservation_condition=condition,
                    dynasty_period=dynasty,
                    approx_year=approx_year,
                    origin_region=region,
                    author_creator=author,
                    tags=tags,
                )

                # Update FAISS Index
                try:
                    search_engine = HybridSearchEngine()
                    search_engine.reindex_all_documents()
                except Exception:
                    pass

                st.success(f"🎉 Successfully cataloged document #{doc_id} into the Digital Heritage Archive & Vector Store!")
