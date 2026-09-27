"""
Digital Heritage Archive - Audio-Visual & Multimedia Heritage Archive
Interactive gallery and ingestion platform for preserving Historical Images, Audio Recordings,
and Video Footage with Dublin Core metadata and deep connections to Archival Records.

Display capabilities:
- For Audio: Interactive audio player with waveform & transcript
- For Video: High-definition video player with motion controls & documentary summary
- For Images: High-resolution image preview with metadata & download
- Connected Archival Records: Bidirectional linkage to primary cataloged documents
"""

import streamlit as st
from PIL import Image
from pathlib import Path
import uuid
import textwrap
import os

from config import (
    MULTIMEDIA_DIR,
    MULTIMEDIA_IMAGES_DIR,
    MULTIMEDIA_AUDIO_DIR,
    MULTIMEDIA_VIDEO_DIR,
    ARCHIVAL_ERAS,
)
from core.storage import (
    get_all_multimedia,
    get_multimedia_by_id,
    insert_multimedia_item,
    get_all_records,
    get_record_by_id,
    delete_multimedia_item,
)
from utils.sample_media_loader import bootstrap_multimedia_archive


def render_audiovisual():
    # Page Header
    header_html = textwrap.dedent("""
    <div style="text-align: center; margin-bottom: 22px;">
        <h1 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; letter-spacing: 0.08em;">
            🎙️ AUDIO-VISUAL HERITAGE ARCHIVE
        </h1>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-top: 5px;">
            Intangible Heritage &bull; Oral Testimonies &bull; Historical Footage &bull; High-Resolution Artifact Gallery
        </p>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # 1. Ensure sample data is initialized
    all_media = get_all_multimedia(limit=300)
    if not all_media:
        bootstrap_multimedia_archive()
        all_media = get_all_multimedia(limit=300)

    # Calculate Counts
    total_count = len(all_media)
    img_count = sum(1 for m in all_media if m.get("media_type") == "image")
    aud_count = sum(1 for m in all_media if m.get("media_type") == "audio")
    vid_count = sum(1 for m in all_media if m.get("media_type") == "video")
    linked_count = sum(1 for m in all_media if m.get("linked_record_id") is not None)

    # Top Metrics Banner
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Media Items", total_count)
    with m2:
        st.metric("🖼️ Images & Scans", img_count)
    with m3:
        st.metric("🎙️ Audio Recordings", aud_count)
    with m4:
        st.metric("🎬 Video Footage", vid_count)
    with m5:
        st.metric("🔗 Linked to Documents", linked_count)

    st.markdown("---")

    # Main Tabs: Gallery & Ingestion Studio
    tab_gallery, tab_upload = st.tabs([
        "🏛️ Audio-Visual Archive Gallery",
        "📤 Archivist Ingestion Studio (Upload Media)",
    ])

    # =========================================================================
    # TAB 1: MULTIMEDIA ARCHIVE GALLERY
    # =========================================================================
    with tab_gallery:
        # Category Filter Pills
        st.markdown("##### 🔍 Filter Archive by Media Type:")
        
        if "av_media_filter" not in st.session_state:
            st.session_state["av_media_filter"] = "All"

        filter_cols = st.columns(5)
        categories = [
            ("All Media", "All", total_count),
            ("🖼️ Images", "image", img_count),
            ("🎙️ Audio", "audio", aud_count),
            ("🎬 Video", "video", vid_count),
            ("🔗 Linked Only", "linked", linked_count),
        ]

        active_filter = st.session_state["av_media_filter"]

        for idx, (label, val, count) in enumerate(categories):
            with filter_cols[idx]:
                is_active = (active_filter == val)
                btn_type = "primary" if is_active else "secondary"
                if st.button(f"{label} ({count})", key=f"av_flt_{val}", type=btn_type, use_container_width=True):
                    st.session_state["av_media_filter"] = val
                    st.rerun()

        selected_media_type = st.session_state["av_media_filter"]

        # Search and Sort Bar
        scol1, scol2 = st.columns([3, 1])
        with scol1:
            search_query = st.text_input(
                "🔍 Search Audio-Visual Archive:",
                placeholder="e.g. 'Ambedkar', 'Nehru', 'Konark', 'Vedic', 'Nalanda', 'Tryst with Destiny'...",
                key="av_search_box",
            )
        with scol2:
            sort_order = st.selectbox(
                "Sort Gallery:",
                ["Newest First", "Oldest First", "Title (A-Z)"],
                key="av_sort_box",
            )

        # Retrieve filtered items
        if selected_media_type == "linked":
            items = [m for m in get_all_multimedia(search_query=search_query) if m.get("linked_record_id") is not None]
        else:
            items = get_all_multimedia(
                media_type=None if selected_media_type == "All" else selected_media_type,
                search_query=search_query,
            )

        if sort_order == "Oldest First":
            items = list(reversed(items))
        elif sort_order == "Title (A-Z)":
            items = sorted(items, key=lambda x: x.get("title", "").lower())

        st.markdown("<br/>", unsafe_allow_html=True)

        if not items:
            st.warning(f"No multimedia items found matching filter '{selected_media_type}' and query '{search_query}'.")
        else:
            st.markdown(f"### 📚 Displaying {len(items)} Archival Media Items")
            
            # Display items in rich cards
            for idx, item in enumerate(items, start=1):
                m_id = item["id"]
                m_uid = item.get("media_uid", f"AV-{m_id}")
                m_type = item.get("media_type", "image").lower()
                m_title = item.get("title", "Untitled Archival Media")
                m_desc = item.get("description") or item.get("transcript") or "Archival multimedia asset."
                m_creator = item.get("creator") or item.get("speaker_narrator") or "Archival Contributor"
                m_year = item.get("year") or item.get("recorded_date") or "Historical Era"
                m_lang = item.get("language", "English")
                m_inst = item.get("institution", "National Archives of India")
                m_rights = item.get("rights", "Public Domain / CC0 Open Access")
                m_path = item.get("file_path", "")
                m_format = item.get("file_format") or Path(m_path).suffix.upper()
                m_dur = item.get("duration_seconds", 0.0)
                m_size = item.get("file_size_bytes", 0)
                m_tags = item.get("tags") or item.get("era_topic") or ""
                m_transcript = item.get("transcript", "")
                linked_rec_id = item.get("linked_record_id")
                linked_title = item.get("linked_record_title")
                linked_year = item.get("linked_record_year")

                # Type styling tokens
                type_badges = {
                    "image": ("🖼️ IMAGE ARTIFACT", "#3b82f6", "badge-sapphire"),
                    "audio": ("🎙️ AUDIO RECORDING", "#10b981", "badge-emerald"),
                    "video": ("🎬 VIDEO FOOTAGE", "#f59e0b", "badge-amber"),
                }
                type_label, type_color, type_badge_cls = type_badges.get(m_type, ("📁 MEDIA", "#fbbf24", "badge-amber"))

                with st.container():
                    # Card Header HTML
                    card_html = textwrap.dedent(f"""
                    <div style="background: rgba(15, 23, 42, 0.9); border-radius: 8px; border: 1px solid rgba(251, 191, 36, 0.25); border-left: 5px solid {type_color}; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="background: {type_color}22; color: {type_color}; border: 1px solid {type_color}; font-size: 0.85rem; font-weight: 700; padding: 3px 12px; border-radius: 12px;">
                                    {type_label}
                                </span>
                                <span style="background: rgba(251, 191, 36, 0.12); color: #fbbf24; border: 1px solid #fbbf24; font-size: 0.85rem; font-weight: 600; padding: 3px 10px; border-radius: 6px;">
                                    📅 {m_year}
                                </span>
                            </div>
                            <span style="color: #94a3b8; font-size: 0.82rem; font-family: monospace;">
                                Accession: {m_uid}
                            </span>
                        </div>
                        <h3 style="color: #fbbf24; margin: 0 0 8px 0; font-family: 'Cinzel', serif; font-size: 1.3rem;">
                            #{idx}. {m_title}
                        </h3>
                        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin: 0 0 10px 0;">
                            {m_desc}
                        </p>
                        <div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 0.84rem; color: #94a3b8; margin-bottom: 6px;">
                            <span>👤 <strong>Creator/Narrator:</strong> {m_creator}</span>
                            <span>🌐 <strong>Language:</strong> {m_lang}</span>
                            <span>📄 <strong>Format:</strong> {m_format}</span>
                            <span>🏛️ <strong>Holding:</strong> {m_inst}</span>
                        </div>
                    </div>
                    """)
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Dynamic Media Player & Preview Section
                    pcol_left, pcol_right = st.columns([1.3, 1], gap="medium")

                    # Left Column: Dedicated Player per media type
                    with pcol_left:
                        st.markdown("##### 🎛️ Interactive Playback & Preview:")
                        
                        if m_type == "audio":
                            # Audio Player
                            if m_path and Path(m_path).exists():
                                st.audio(m_path)
                            else:
                                st.info("🎙️ Spoken audio track cataloged.")
                            
                            if m_dur > 0:
                                st.caption(f"⏱️ **Duration:** ~{m_dur:.1f}s | 🎧 **Bitrate:** 128 kbps | 🔊 **Type:** Master Archival Recording")

                        elif m_type == "video":
                            # Video Player
                            if m_path and Path(m_path).exists():
                                st.video(m_path)
                            else:
                                st.info("🎬 Motion picture footage cataloged.")

                            if m_dur > 0:
                                st.caption(f"⏱️ **Duration:** ~{m_dur:.1f}s | 📺 **Format:** {m_format} | 🎥 **Aspect:** 16:9 Standard")

                        elif m_type == "image":
                            # Image Preview
                            if m_path and Path(m_path).exists():
                                try:
                                    img_obj = Image.open(m_path)
                                    st.image(img_obj, use_container_width=True, caption=f"{m_title} ({img_obj.width}x{img_obj.height} px)")
                                except Exception:
                                    st.info(f"🖼️ Image File: `{Path(m_path).name}`")
                            else:
                                st.info(f"🖼️ Primary Visual Artifact: `{Path(m_path).name if m_path else 'Image'}`")

                    # Right Column: Connected Archival Record & Metadata
                    with pcol_right:
                        # Connected Archival Record
                        st.markdown("##### 🔗 Connected Archival Record:")
                        if linked_rec_id:
                            st.markdown(
                                f"""
                                <div style="background: rgba(10, 15, 26, 0.95); padding: 12px 14px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.4); border-left: 4px solid #10b981; margin-bottom: 10px;">
                                    <span style="color: #6ee7b7; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">
                                        ✅ Linked Primary Document:
                                    </span>
                                    <div style="color: #fbbf24; font-weight: 600; font-size: 0.95rem; margin-top: 2px;">
                                        #{linked_rec_id}. {linked_title or 'Archival Record'}
                                    </div>
                                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
                                        Year: {linked_year or 'Historical'} &bull; Creator: {item.get('linked_record_creator', 'Archival')}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                f"📜 Open Linked Document #{linked_rec_id} in Document Viewer",
                                key=f"av_open_doc_{m_id}_{idx}",
                                type="primary",
                                use_container_width=True,
                            ):
                                st.session_state["selected_doc_id"] = linked_rec_id
                                st.session_state["current_page"] = "Document Viewer"
                                st.rerun()
                        else:
                            st.info("ℹ️ Standalone multimedia asset (No primary document linked).")

                        # Transcript / Oral Testimony Expander
                        if m_transcript:
                            with st.expander("📝 Spoken Transcript / Oral Testimony", expanded=(m_type == "audio")):
                                st.text_area(
                                    "Verified Audio/Video Transcript:",
                                    value=m_transcript,
                                    height=110,
                                    disabled=True,
                                    key=f"av_trans_view_{m_id}_{idx}",
                                )

                        # Dublin Core Source Details & Download
                        with st.expander("🏛️ Dublin Core Source & Preservation Info", expanded=False):
                            meta_info_html = textwrap.dedent(f"""
                            <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.6;">
                                <strong style="color: #fbbf24;">🆔 Dublin Core UID:</strong> <code>{m_uid}</code><br/>
                                <strong style="color: #fbbf24;">🛡️ Rights & License:</strong> {m_rights}<br/>
                                <strong style="color: #fbbf24;">🏷️ Subject Tags:</strong> {m_tags or 'Heritage'}<br/>
                                <strong style="color: #fbbf24;">📁 Physical Path:</strong> <code>{m_path}</code><br/>
                                <strong style="color: #fbbf24;">📦 File Size:</strong> {m_size/1024:.1f} KB
                            </div>
                            """)
                            st.markdown(meta_info_html, unsafe_allow_html=True)
                            
                            if m_path and Path(m_path).exists():
                                f_bytes = Path(m_path).read_bytes()
                                st.download_button(
                                    label=f"📥 Download {m_format} File ({Path(m_path).name})",
                                    data=f_bytes,
                                    file_name=Path(m_path).name,
                                    mime="image/png" if m_type == "image" else ("video/mp4" if m_type == "video" else "audio/mp3"),
                                    key=f"av_dl_{m_id}_{idx}",
                                    use_container_width=True,
                                )

                    st.markdown("<br/>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: ARCHIVIST INGESTION STUDIO (UPLOAD MEDIA)
    # =========================================================================
    with tab_upload:
        st.markdown("### 📤 Institutional Archivist Ingestion Studio")
        st.markdown("Preserve oral history recordings, archival motion reels, and high-resolution artifact scans into the national repository.")

        # Get existing archival records for linkage dropdown
        records = get_all_records(limit=200)
        rec_options = ["None (Standalone Multimedia Item)"] + [
            f"#{r['id']} — {r['title']} ({r.get('year', 'Historical')})" for r in records
        ]
        rec_map = {f"#{r['id']} — {r['title']} ({r.get('year', 'Historical')})": r['id'] for r in records}

        with st.form("archivist_multimedia_ingest_form"):
            st.markdown("#### 1. Select Media Type & Upload File:")
            fcol1, fcol2 = st.columns([1, 2])
            
            with fcol1:
                ingest_media_type = st.selectbox(
                    "Media Category *",
                    ["Audio Recording (MP3, WAV, OGG, M4A)", "Video Footage (MP4, WEBM, MOV)", "Image Artifact (PNG, JPG, TIFF, WEBP)"],
                    key="ingest_media_type_select",
                )
            
            with fcol2:
                # File types per category
                allowed_types = ["mp3", "wav", "m4a", "ogg", "flac"]
                if "Video" in ingest_media_type:
                    allowed_types = ["mp4", "webm", "mov", "mkv", "avi"]
                elif "Image" in ingest_media_type:
                    allowed_types = ["png", "jpg", "jpeg", "webp", "tiff", "bmp"]

                uploaded_file = st.file_uploader(
                    f"Choose {ingest_media_type} File to Ingest *",
                    type=allowed_types,
                    key="av_file_uploader",
                )

            st.markdown("#### 2. Dublin Core Metadata Details:")
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                media_title = st.text_input(
                    "Media Title *",
                    placeholder="e.g. 'Constituent Assembly Closing Speech' or 'Sun Temple Drone Scan'",
                    key="av_title_input",
                )
                media_creator = st.text_input(
                    "Creator / Speaker / Photographer / Director *",
                    placeholder="e.g. 'Dr. B. R. Ambedkar', 'ASI Epigraphy Wing', 'Films Division'",
                    key="av_creator_input",
                )
                media_year = st.text_input(
                    "Year / Recording Date *",
                    placeholder="e.g. '1949 CE', '1500 BCE', 'August 1947'",
                    key="av_year_input",
                )
                media_lang = st.selectbox(
                    "Spoken Language / Script:",
                    ["English", "Hindi (हिन्दी)", "Kannada (ಕನ್ನಡ)", "Tamil (தமிழ்)", "Telugu (తెలుగు)", "Sanskrit (संस्कृतम्)", "Persian", "Prakrit / Brahmi", "Other Historical Script"],
                    key="av_lang_input",
                )

            with mcol2:
                media_inst = st.text_input(
                    "Holding Institution / Archive *",
                    value="National Archives of India (NAI)",
                    key="av_inst_input",
                )
                media_rights = st.selectbox(
                    "Rights & Preservation Terms:",
                    [
                        "Public Domain / CC0 Open Access",
                        "National Archival Heritage / Public Educational Access",
                        "UNESCO World Heritage Cultural License",
                        "Creative Commons Attribution (CC-BY 4.0)",
                        "Restricted Research Access / Institutional Archival Copy",
                    ],
                    key="av_rights_input",
                )
                media_tags = st.text_input(
                    "Thematic Tags & Keywords (comma-separated):",
                    placeholder="e.g. Constitution, Speech, Parliament, Democracy, Law",
                    key="av_tags_input",
                )
                linked_rec_choice = st.selectbox(
                    "Connect to Cataloged Archival Record (Optional):",
                    options=rec_options,
                    key="av_linked_record_select",
                    help="Associates this multimedia asset directly with an existing cataloged manuscript or document in the archive.",
                )

            media_desc = st.text_area(
                "Historical Description & Context Summary *",
                placeholder="Provide diplomatic context, historical provenance, recording conditions, or artifact description...",
                key="av_desc_input",
            )

            media_transcript = st.text_area(
                "Spoken Transcript / Oral History Testimony / Translation Excerpt:",
                placeholder="Enter verbatim speech transcript or lyric transliteration...",
                key="av_trans_input",
            )

            submit_ingest = st.form_submit_button(
                "💾 Ingest & Catalog into Audio-Visual Archive",
                type="primary",
                use_container_width=True,
            )

            if submit_ingest:
                if not media_title or not media_creator or not media_year or not media_desc:
                    st.error("Please fill in all required fields (Title, Creator, Year, and Description).")
                elif not uploaded_file:
                    st.error("Please upload a media file (Image, Audio, or Video).")
                else:
                    # Determine normalized media type
                    n_type = "audio"
                    target_dir = MULTIMEDIA_AUDIO_DIR
                    if "Video" in ingest_media_type:
                        n_type = "video"
                        target_dir = MULTIMEDIA_VIDEO_DIR
                    elif "Image" in ingest_media_type:
                        n_type = "image"
                        target_dir = MULTIMEDIA_IMAGES_DIR

                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save uploaded file
                    safe_uid = uuid.uuid4().hex[:8].upper()
                    dest_filename = f"{safe_uid}_{uploaded_file.name}"
                    save_path = target_dir / dest_filename
                    save_path.write_bytes(uploaded_file.read())
                    
                    f_size = os.path.getsize(save_path)
                    f_format = Path(uploaded_file.name).suffix.upper().replace(".", "")

                    # Linked Record ID
                    linked_id = None
                    if linked_rec_choice and linked_rec_choice != "None (Standalone Multimedia Item)":
                        linked_id = rec_map.get(linked_rec_choice)

                    accession_no = f"DHA-AV-{safe_uid}"

                    new_id = insert_multimedia_item(
                        media_uid=accession_no,
                        title=media_title,
                        media_type=n_type,
                        file_path=str(save_path),
                        description=media_desc,
                        creator=media_creator,
                        year=media_year,
                        language=media_lang.split()[0],
                        institution=media_inst,
                        accession_number=accession_no,
                        rights=media_rights,
                        file_format=f"{f_format} {n_type.capitalize()}",
                        file_size_bytes=f_size,
                        duration_seconds=30.0 if n_type in ["audio", "video"] else 0.0,
                        linked_record_id=linked_id,
                        tags=media_tags,
                        transcript=media_transcript or media_desc,
                        recorded_date=media_year,
                        speaker_narrator=media_creator,
                        era_topic=media_tags,
                    )

                    st.success(f"🎉 Successfully ingested '{media_title}' as **{accession_no}** (ID #{new_id})!")
                    st.info(f"Media saved to `{save_path}`. It is now cataloged and available in the Audio-Visual Gallery.")
                    st.rerun()
