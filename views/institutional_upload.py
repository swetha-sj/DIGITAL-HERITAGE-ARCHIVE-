"""
Digital Heritage Archive - Admin Page: Upload & OCR Ingestion Pipeline
Implements the end-to-end Archival Workflow:
Upload ➔ Preprocess ➔ Tesseract OCR ➔ Text Clean ➔ Archivist Edit ➔ Metadata ➔ SQLite Storage
"""

import streamlit as st
import uuid
import textwrap
from pathlib import Path
from PIL import Image
from config import RAW_DOCS_DIR, PROCESSED_IMAGES_DIR, SAMPLE_DATA_DIR
from core.storage import insert_archival_record, get_all_records, get_record_by_id
from core.preprocessor import ImagePreprocessor
from core.ocr_engine import OCREngine
from core.text_cleaner import TextCleaner
from core.search_engine import SmartSearchEngine

DOCUMENT_TYPES = [
    "Writing",
    "Manuscript",
    "Royal Decree / Farman",
    "Inscription / Copper Plate",
    "Historical Newspaper",
    "Historical Map",
    "Legal Charter",
    "Photograph / Visual Record",
    "Other",
]

LANGUAGES = [
    "English",
    "Hindi (हिन्दी)",
    "Sanskrit (संस्कृतम्)",
    "Tamil (தமிழ்)",
    "Bengali (বাংলা)",
    "Urdu (اردو)",
    "Persian (فارسی)",
    "Marathi (मराठी)",
    "Telugu (తెలుగు)",
    "Gujarati (ગુજરાતી)",
    "Kannada (ಕನ್ನಡ)",
    "Malayalam (മലയാളം)",
    "Arabic (العربية)",
    "Other",
]

OCR_LANG_MAP = {
    "English": "eng",
    "Hindi (हिन्दी)": "hin",
    "Sanskrit (संस्कृतम्)": "san",
    "Tamil (தமிழ்)": "tam",
    "Bengali (বাংলা)": "ben",
    "Urdu (اردو)": "urd",
    "Persian (فارسی)": "fas",
    "Marathi (मराठी)": "mar",
    "Telugu (తెలుగు)": "tel",
    "Gujarati (ગુજરાતી)": "guj",
    "Kannada (ಕನ್ನಡ)": "kan",
    "Malayalam (മലയാളം)": "mal",
    "Arabic (العربية)": "ara",
    "Other": "eng",
}


def render_admin_upload():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.1em;">ADMIN</h1>
            <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 5px;">Upload Archival Material & OCR Pipeline</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_workflow, tab_records = st.tabs(["⚡ Ingestion & OCR Workflow", "📋 View Cataloged Records"])

    with tab_workflow:
        # Step 1: Upload
        st.markdown("### 1. Upload / Scan Historical Document")
        
        col_up1, col_up2 = st.columns([3, 1])
        with col_up1:
            uploaded_file = st.file_uploader(
                "Select Archival Document File (PDF or Image format):",
                type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
                help="Select an archival manuscript scan, charter, royal decree, or PDF",
                key="archivist_file_input",
            )
        with col_up2:
            st.write("")
            st.write("")
            if st.button("🖼️ Load Demo Scan", help="Loads a sample historical manuscript scan for instant testing", use_container_width=True):
                sample_img_path = SAMPLE_DATA_DIR / "ashoka_major_rock_edict_xii.png"
                if not sample_img_path.exists():
                    sample_img_path = SAMPLE_DATA_DIR / "ashoka_edict_test.png"
                if sample_img_path.exists():
                    pil_sample = Image.open(sample_img_path)
                    st.session_state["current_pil_img"] = pil_sample
                    st.session_state["active_file_name"] = sample_img_path.name
                    st.session_state["active_file_type"] = "Image (PNG)"
                    st.session_state["active_file_bytes"] = sample_img_path.read_bytes()
                    st.success("Loaded demo manuscript scan!")

        # Handle user upload
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name
            file_ext = Path(file_name).suffix.lower()
            file_type = "PDF Document" if file_ext == ".pdf" else f"Image ({file_ext.replace('.', '').upper()})"

            st.session_state["active_file_name"] = file_name
            st.session_state["active_file_type"] = file_type
            st.session_state["active_file_bytes"] = file_bytes
            st.session_state["active_file_ext"] = file_ext

            if file_ext != ".pdf":
                try:
                    pil_img = Image.open(uploaded_file)
                    st.session_state["current_pil_img"] = pil_img
                except Exception:
                    st.session_state.pop("current_pil_img", None)
            else:
                st.session_state.pop("current_pil_img", None)
                temp_pdf_path = RAW_DOCS_DIR / f"temp_{file_name}"
                with open(temp_pdf_path, "wb") as f:
                    f.write(file_bytes)
                st.session_state["temp_pdf_path"] = str(temp_pdf_path)

        # File Status Display
        active_name = st.session_state.get("active_file_name")
        if active_name:
            st.info(f"📁 **Active Document:** `{active_name}` ({st.session_state.get('active_file_type', 'File')})")

        st.markdown("---")

        # Step 2: Image Preprocessing Section (ALWAYS VISIBLE)
        st.markdown("### 2. Image Preprocessing (Filter Controls & Side-by-Side Comparison)")
        st.caption("Apply computer vision enhancement algorithms to optimize aged, stained, or tilted historical documents.")

        # Filter Controls Panel
        st.markdown(
            """
            <div style="background: rgba(18, 26, 43, 0.85); padding: 14px 20px; border-radius: 10px; border: 1px solid rgba(212, 175, 55, 0.4); margin-bottom: 15px;">
                <h4 style="color: #fbbf24; margin: 0 0 10px 0;">⚙️ Computer Vision Enhancement Controls</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            chk_deskew = st.checkbox("Auto-Deskew (Straighten 0°)", value=True, help="Detects text angle and rotates back to 0°")
        with fcol2:
            chk_contrast = st.checkbox("CLAHE Contrast Equalization", value=True, help="Restores faded ancient ink and evens exposure")
        with fcol3:
            chk_denoise = st.checkbox("Non-local Means Denoise", value=True, help="Removes paper grain & speckles")
        with fcol4:
            chk_binarize = st.checkbox("Adaptive Gaussian Binarize", value=False, help="Segments dark ink from yellow parchment")

        # Big Preprocessing Action Button
        apply_filter_btn = st.button("✨ Apply Preprocessing Filters", type="primary", use_container_width=True)

        if apply_filter_btn:
            if "current_pil_img" not in st.session_state:
                st.warning("⚠️ Please upload an image file in Step 1 (or click 'Load Demo Scan') before applying filters.")
            else:
                with st.spinner("Executing OpenCV image enhancement pipeline..."):
                    cv_proc, audit = ImagePreprocessor.process_pipeline(
                        st.session_state["current_pil_img"],
                        do_deskew=chk_deskew,
                        do_contrast=chk_contrast,
                        do_denoise=chk_denoise,
                        do_binarize=chk_binarize,
                    )
                    proc_pil = ImagePreprocessor.convert_to_pil(cv_proc)
                    st.session_state["processed_pil_img"] = proc_pil
                    st.session_state["proc_audit"] = audit
                    st.success("✅ Filters applied successfully! Inspect the side-by-side comparison below.")

        # Side-by-Side Visual Comparison
        st.markdown("#### 🔍 Side-by-Side Visual Comparison: Original Scan vs. Enhanced Output")
        comp_col1, comp_col2 = st.columns(2)

        with comp_col1:
            st.markdown(
                """
                <div style="text-align: center; background: rgba(15, 23, 42, 0.9); padding: 8px; border-radius: 6px; border: 1px solid rgba(148, 163, 184, 0.3); margin-bottom: 8px;">
                    <strong style="color: #cbd5e1;">🖼️ Original Uploaded Scan</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if "current_pil_img" in st.session_state:
                st.image(
                    st.session_state["current_pil_img"],
                    caption=f"Original: {st.session_state.get('active_file_name', 'Manuscript Scan')}",
                    use_container_width=True,
                )
            else:
                st.info("No image loaded yet. Upload an image above or click **'Load Demo Scan'** to view original.")

        with comp_col2:
            if "processed_pil_img" in st.session_state:
                audit_info = st.session_state.get("proc_audit", {})
                deskew_val = audit_info.get("deskew_angle", 0.0)
                engine_name = audit_info.get("engine", "OpenCV")
                st.markdown(
                    f"""
                    <div style="text-align: center; background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #6ee7b7;">✨ Enhanced Output (Engine: {engine_name} | Deskew: {deskew_val}°)</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.image(
                    st.session_state["processed_pil_img"],
                    caption="Preprocessed Image (Enhanced for OCR)",
                    use_container_width=True,
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; background: rgba(15, 23, 42, 0.9); padding: 8px; border-radius: 6px; border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 8px;">
                        <strong style="color: #fbbf24;">✨ Enhanced Output (Preview)</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.info("👈 Click the **'✨ Apply Preprocessing Filters'** button above to generate and render the enhanced output side-by-side here.")

        st.markdown("---")

        # Step 3 & 4: Tesseract OCR & Text Cleaning
        st.markdown("### 3. Tesseract OCR & Text Cleaning")

        # Tesseract Status & Path Config Expander
        with st.expander("⚙️ Tesseract Engine Settings & Installation Guide", expanded=False):
            tess_detected = OCREngine.is_tesseract_available()
            st.markdown(f"**Tesseract Binary Status:** {'🟢 Detected on System' if tess_detected else '🟡 Not on PATH (Smart Fallback Active)'}")
            
            custom_tess_input = st.text_input(
                "Specify Custom Tesseract Executable Path (if installed elsewhere):",
                value=st.session_state.get("custom_tess_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
                help="Enter path to tesseract.exe on your Windows system",
            )
            if st.button("Set Custom Path"):
                st.session_state["custom_tess_path"] = custom_tess_input
                st.success(f"Configured Tesseract path: {custom_tess_input}")

            st.markdown(
                """
                **How to install Tesseract on Windows (Optional for live custom scan OCR):**
                1. Download installer from: [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
                2. Or run in PowerShell: `winget install UB-Mannheim.TesseractOCR`
                """
            )
        
        ocr_col1, ocr_col2 = st.columns([1, 1])
        with ocr_col1:
            selected_lang_label = st.selectbox("Select OCR Language:", LANGUAGES, index=0, key="ocr_lang_selector")
            ocr_lang_code = OCR_LANG_MAP.get(selected_lang_label, "eng")

            ocr_btn = st.button("🔍 Extract Text via OCR", use_container_width=True)
            if ocr_btn:
                if "active_file_name" not in st.session_state and "current_pil_img" not in st.session_state:
                    st.warning("Please upload a file or click 'Load Demo Scan' first.")
                else:
                    custom_p = st.session_state.get("custom_tess_path")
                    ocr_engine = OCREngine(custom_tesseract_path=custom_p)
                    
                    with st.spinner("Extracting text and running optical character recognition..."):
                        active_fname = st.session_state.get("active_file_name", "document.png")
                        
                        if st.session_state.get("active_file_ext") == ".pdf":
                            res = ocr_engine.extract_from_pdf(st.session_state["temp_pdf_path"], lang=ocr_lang_code)
                        else:
                            target_img = st.session_state.get("processed_pil_img") or st.session_state.get("current_pil_img")
                            res = ocr_engine.extract_from_image(target_img, lang=ocr_lang_code, filename=active_fname)

                        if res.get("success"):
                            st.session_state["raw_ocr_extracted"] = res.get("text", "")
                            st.session_state["ocr_confidence_val"] = res.get("confidence", 0.0)
                            
                            if res.get("is_fallback"):
                                st.info(f"ℹ️ {res.get('error')}")
                            else:
                                st.success(f"✅ Text Extracted! ({res.get('word_count', len(res.get('text', '').split()))} words | Confidence: {res.get('confidence', 0)}%)")
                        else:
                            st.warning(f"ℹ️ {res.get('error', 'Extraction completed.')}")
                            if not st.session_state.get("raw_ocr_extracted"):
                                st.session_state["raw_ocr_extracted"] = res.get("text", "")
                            st.session_state["ocr_confidence_val"] = 0.0

            raw_text_display = st.text_area(
                "Raw OCR Extracted Text:",
                value=st.session_state.get("raw_ocr_extracted", ""),
                height=180,
                placeholder="Optical character recognition or text stream output will appear here...",
                key="raw_ocr_area",
            )

        with ocr_col2:
            st.markdown("**Automated Text Cleaning:**")
            st.caption("Standardizes Unicode, strips scanning artifacts, and repairs broken hyphenated line breaks.")

            if st.button("🧹 Clean & Standardize OCR Text", use_container_width=True):
                if raw_text_display.strip():
                    clean_res = TextCleaner.clean(raw_text_display)
                    st.session_state["edited_cleaned_text"] = clean_res["cleaned_text"]
                    st.info(f"Cleaned! Removed {clean_res['reduction_percentage']}% scanning noise & broken artifacts.")
                else:
                    st.warning("No text to clean.")

            # Step 5 & 6: Archivist Interactive Transcript Editor
            current_clean_val = st.session_state.get("edited_cleaned_text", raw_text_display)
            edited_transcript = st.text_area(
                "Verified Transcript (Archivist Editor):",
                value=current_clean_val,
                height=180,
                placeholder="Archivist can inspect, correct, and edit the final transcript here before publishing...",
                key="archivist_transcript_editor",
                help="You can freely edit or correct the transcript text here.",
            )

        st.markdown("---")

        # Step 7: Archival Metadata Entry
        st.markdown("### 4. Archival Metadata & Publishing")
        st.caption("Enter metadata to catalog the document along with the verified transcript into SQLite.")

        with st.form("admin_archival_upload_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Title:", placeholder="e.g. Royal Decree of Emperor Akbar on Sulh-i-Kul")
                creator = st.text_input("Creator:", placeholder="e.g. Jalal-ud-din Muhammad Akbar")
                year = st.text_input("Year:", placeholder="e.g. 1582 CE or 1857")
                language = st.selectbox("Language:", LANGUAGES, index=0)

            with col_b:
                topic = st.text_input("Topic:", placeholder="e.g. Universal Peace & Religious Endowments")
                document_type = st.selectbox("Document Type:", DOCUMENT_TYPES, index=0)
                institution = st.text_input("Institution:", placeholder="e.g. National Archives of India")
                rights = st.text_input("Rights:", placeholder="e.g. Public Domain / Cultural Heritage")

            description = st.text_area(
                "Description:",
                placeholder="Detailed historical context, provenance, physical condition notes, and description...",
                height=100,
            )

            st.markdown("<br/>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Process & Save", use_container_width=True)

        if submit_btn:
            # Form Validation
            errors = []
            if "active_file_name" not in st.session_state and "current_pil_img" not in st.session_state:
                errors.append("Please upload or load an archival file before saving.")
            if not title.strip():
                errors.append("Title is required.")
            if not creator.strip():
                errors.append("Creator is required.")
            if not year.strip():
                errors.append("Year is required.")
            if not topic.strip():
                errors.append("Topic is required.")
            if not institution.strip():
                errors.append("Institution is required.")
            if not rights.strip():
                errors.append("Rights statement is required.")

            if errors:
                st.error("⚠️ Please resolve the following required fields:")
                for err in errors:
                    st.markdown(f"- {err}")
            else:
                # 1. Save original raw file in data/raw_documents/
                f_name = st.session_state.get("active_file_name", "manuscript_scan.png")
                safe_name = f"{uuid.uuid4().hex[:8]}_{f_name}"
                saved_raw_path = RAW_DOCS_DIR / safe_name
                
                if "active_file_bytes" in st.session_state:
                    with open(saved_raw_path, "wb") as f:
                        f.write(st.session_state["active_file_bytes"])
                elif "current_pil_img" in st.session_state:
                    st.session_state["current_pil_img"].save(saved_raw_path)

                # 2. Save preprocessed image if available
                saved_proc_path = None
                if "processed_pil_img" in st.session_state:
                    proc_filename = f"proc_{safe_name}.png"
                    saved_proc_path = PROCESSED_IMAGES_DIR / proc_filename
                    st.session_state["processed_pil_img"].save(saved_proc_path)

                # 3. Generate Accession ID
                year_tag = "".join(filter(str.isalnum, year))[:6].upper() or "DOC"
                accession_num = f"DHA-{year_tag}-{uuid.uuid4().hex[:6].upper()}"

                # 4. Store in SQLite
                try:
                    final_cleaned = edited_transcript.strip()
                    raw_extracted = st.session_state.get("raw_ocr_extracted", "").strip()
                    conf = st.session_state.get("ocr_confidence_val", 0.0)

                    record_id = insert_archival_record(
                        accession_number=accession_num,
                        title=title.strip(),
                        creator=creator.strip(),
                        year=year.strip(),
                        language=language.strip(),
                        topic=topic.strip(),
                        document_type=document_type.strip(),
                        institution=institution.strip(),
                        rights=rights.strip(),
                        description=description.strip(),
                        original_filename=f_name,
                        file_type=st.session_state.get("active_file_type", "Image (PNG)"),
                        file_size_bytes=saved_raw_path.stat().st_size if saved_raw_path.exists() else 1024,
                        saved_file_path=str(saved_raw_path),
                        processed_file_path=str(saved_proc_path) if saved_proc_path else None,
                        raw_ocr_text=raw_extracted,
                        cleaned_text=final_cleaned,
                        ocr_confidence=conf,
                    )

                    st.session_state["recent_saved_id"] = record_id
                    
                    # Synchronize into FAISS vector search index
                    try:
                        search_eng = SmartSearchEngine()
                        indexed_count = search_eng.reindex_all_documents()
                        faiss_synced = True
                    except Exception:
                        faiss_synced = False

                    st.success(f"🎉 **Record Published & Cataloged!** Accession: `{accession_num}` (ID: #{record_id})")
                    if faiss_synced:
                        st.info("⚡ **Search Index Synchronized:** Vector embeddings generated and indexed in FAISS 384-dim semantic space.")

                except Exception as ex:
                    st.error(f"❌ Failed to store in SQLite: {str(ex)}")

        # Display latest saved record with transcript & file paths
        if "recent_saved_id" in st.session_state:
            rec = get_record_by_id(st.session_state["recent_saved_id"])
            if rec:
                st.markdown("---")
                st.markdown("### 📄 Published Archival Record & Verified Transcript")
                
                # Render visual card
                saved_card_html = textwrap.dedent(f"""
                <div class="heritage-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 8px;">
                        <h3 style="margin:0; color:#fbbf24;">#{rec['id']}. {rec['title']}</h3>
                        <span class="heritage-badge" style="background: rgba(16, 185, 129, 0.2); border-color: #10b981; color: #6ee7b7;">
                            ✨ Published & Indexed
                        </span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span class="heritage-badge">🆔 Accession: <code>{rec['accession_number']}</code></span>
                        <span class="heritage-badge">👤 Creator: {rec['creator']}</span>
                        <span class="heritage-badge">📅 Year: {rec['year']}</span>
                        <span class="heritage-badge">🌐 Language: {rec['language']}</span>
                        <span class="heritage-badge">🏷️ Topic: {rec['topic']}</span>
                        <span class="heritage-badge">📜 Type: {rec['document_type']}</span>
                        <span class="heritage-badge">🏛️ Institution: {rec['institution']}</span>
                        <span class="heritage-badge">⚡ OCR Conf: {rec['ocr_confidence']}%</span>
                    </div>
                    <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 6px;">
                        <strong>Description:</strong> {rec['description'] or 'No description provided.'}
                    </p>
                </div>
                """)
                st.markdown(saved_card_html, unsafe_allow_html=True)

                # Action Launchers
                act_col1, act_col2, act_col3 = st.columns(3)
                with act_col1:
                    if st.button(f"📜 Inspect in Document Viewer (#{rec['id']})", type="primary", use_container_width=True, key=f"admin_view_btn_{rec['id']}"):
                        st.session_state["selected_doc_id"] = rec["id"]
                        st.session_state["current_page"] = "Document Viewer"
                        st.rerun()
                with act_col2:
                    if st.button("🔍 Find in Smart Search", use_container_width=True, key=f"admin_search_btn_{rec['id']}"):
                        st.session_state["current_page"] = "Search"
                        st.rerun()
                with act_col3:
                    if st.button("⏳ View on Timeline", use_container_width=True, key=f"admin_timeline_btn_{rec['id']}"):
                        st.session_state["current_page"] = "Timeline"
                        st.rerun()

                st.markdown("<br/>", unsafe_allow_html=True)

                # Saved Document Visual Preview & Download
                scol1, scol2 = st.columns([1, 1])
                with scol1:
                    p_path = rec.get("processed_file_path") or rec.get("saved_file_path")
                    if p_path and Path(p_path).exists() and not str(p_path).lower().endswith(".pdf"):
                        try:
                            s_img = Image.open(p_path)
                            st.image(s_img, caption="Archival Scan Preview", use_container_width=True)
                        except Exception:
                            pass
                    
                    # 1-Click Download Button
                    raw_p = rec.get("saved_file_path")
                    if raw_p and Path(raw_p).exists():
                        try:
                            f_bytes = Path(raw_p).read_bytes()
                            st.download_button(
                                label=f"📥 Download Original File ({rec['original_filename']})",
                                data=f_bytes,
                                file_name=rec['original_filename'],
                                mime="application/pdf" if str(raw_p).lower().endswith(".pdf") else "image/png",
                                key=f"dl_saved_btn_{rec['id']}",
                                use_container_width=True,
                            )
                        except Exception:
                            pass

                with scol2:
                    transcript_box_html = textwrap.dedent(f"""
                    <div style="background: rgba(15, 23, 42, 0.9); padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                        <strong style="color:#fbbf24;">📝 Verified Archival Transcript:</strong><br/>
                        <p style="color: #f1f5f9; font-family: monospace; font-size: 0.88rem; margin-top: 5px; white-space: pre-wrap;">{rec['cleaned_text'] or rec['raw_ocr_text'] or 'No transcript attached.'}</p>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 10px 14px; border-radius: 6px; font-size: 0.85rem; color: #94a3b8;">
                        <strong>📁 Original File:</strong> {rec['original_filename']} ({rec['file_type']} | {rec['file_size_bytes'] / 1024:.2f} KB)<br/>
                        <strong>📍 Storage Path:</strong> <code>{rec['saved_file_path']}</code><br/>
                        <strong>🕒 Cataloged:</strong> {rec['created_at']}
                    </div>
                    """)
                    st.markdown(transcript_box_html, unsafe_allow_html=True)

    with tab_records:
        st.markdown("### 📋 Archival Records & Verified Transcripts in SQLite")
        all_records = get_all_records()
        if not all_records:
            st.info("No records in the database yet.")
        else:
            st.caption(f"Total stored records: {len(all_records)}")
            for r in all_records:
                with st.expander(f"#{r['id']} - {r['title']} ({r['year']}) | {r['accession_number']}"):
                    rcol1, rcol2 = st.columns([1, 1])
                    with rcol1:
                        st.markdown(f"**Title:** {r['title']}")
                        st.markdown(f"**Creator:** {r['creator']} | **Year:** {r['year']} | **Language:** {r['language']}")
                        st.markdown(f"**Topic:** {r['topic']} | **Type:** {r['document_type']} | **Institution:** {r['institution']}")
                        st.markdown(f"**Rights:** {r['rights']}")
                        st.markdown(f"**Description:** {r['description'] or 'N/A'}")
                        
                        raw_f = r.get("saved_file_path")
                        if raw_f and Path(raw_f).exists():
                            try:
                                b_data = Path(raw_f).read_bytes()
                                st.download_button(
                                    label=f"📥 Download ({r['original_filename']})",
                                    data=b_data,
                                    file_name=r['original_filename'],
                                    mime="application/pdf" if str(raw_f).lower().endswith(".pdf") else "image/png",
                                    key=f"tab_dl_{r['id']}",
                                    use_container_width=True,
                                )
                            except Exception:
                                pass

                    with rcol2:
                        img_to_show = r.get("processed_file_path") or r.get("saved_file_path")
                        if img_to_show and Path(img_to_show).exists() and not str(img_to_show).lower().endswith(".pdf"):
                            try:
                                exp_img = Image.open(img_to_show)
                                st.image(exp_img, caption=r['title'], use_container_width=True)
                            except Exception:
                                pass

                        if r.get("cleaned_text") or r.get("raw_ocr_text"):
                            st.markdown("**Archival Transcript:**")
                            st.text_area("Transcript", value=r.get("cleaned_text") or r.get("raw_ocr_text"), height=120, disabled=True, key=f"rec_text_{r['id']}")
