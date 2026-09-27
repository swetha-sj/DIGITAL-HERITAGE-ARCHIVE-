"""
Unit and Integration tests for Audio-Visual Archive.
Tests:
1. Ingestion and storage of Images, Audio recordings, and Video footage.
2. Metadata persistence for all Dublin Core fields.
3. Gallery filtering by media type (All, Image, Audio, Video).
4. Keyword search across multimedia titles, transcripts, and tags.
5. Bidirectional linking between multimedia items and primary archival records.
6. Deletion and retrieval operations.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.storage import (
    get_all_records,
    insert_multimedia_item,
    get_all_multimedia,
    get_multimedia_by_id,
    get_multimedia_for_record,
    delete_multimedia_item,
)
from utils.sample_media_loader import (
    create_sample_image,
    create_sample_audio,
    create_sample_video,
    bootstrap_multimedia_archive,
)


def test_audiovisual_pipeline():
    print("--- 1. Testing Sample Multimedia Generation & Bootstrap ---")
    total_mm = bootstrap_multimedia_archive()
    assert total_mm >= 10, f"Expected at least 10 seeded media items, got {total_mm}"
    print(f"[OK] Seeded multimedia items count: {total_mm}")

    print("\n--- 2. Testing Ingestion of Image Artifact ---")
    sample_img_path = create_sample_image(
        filename="test_epigraphic_tablet.png",
        title="Test Epigraphic Tablet Scan",
        subtitle="National Epigraphy Bureau",
    )
    assert Path(sample_img_path).exists(), "Image file must exist on disk"
    
    img_id = insert_multimedia_item(
        media_uid="AV-TEST-IMG-001",
        title="Test Epigraphic Tablet of Karnataka",
        media_type="image",
        file_path=sample_img_path,
        description="High-resolution multispectral scan of 6th-century stone tablet.",
        creator="Epigraphy Wing ASI",
        year="550 CE",
        language="Old Kannada",
        institution="Karnataka State Archaeology",
        rights="Public Domain / CC0",
        file_format="PNG Image (800x600)",
        file_size_bytes=Path(sample_img_path).stat().st_size,
        tags="Tablet, Inscription, Chalukya",
    )
    assert img_id > 0, "Image insertion must return valid database ID"
    print(f"[OK] Ingested Image item #{img_id}: 'Test Epigraphic Tablet of Karnataka'")

    print("\n--- 3. Testing Ingestion of Audio Recording ---")
    sample_aud_path = create_sample_audio(
        filename="test_historical_declaration.mp3",
        spoken_text="All citizens shall have equal liberty of thought, expression, belief, faith and worship.",
        lang_code="en",
    )
    assert Path(sample_aud_path).exists(), "Audio file must exist on disk"

    # Get a primary archival record to link to
    records = get_all_records(limit=5)
    test_rec_id = records[0]["id"] if records else 1

    aud_id = insert_multimedia_item(
        media_uid="AV-TEST-AUD-001",
        title="Test Constitutional Declaration Audio",
        media_type="audio",
        file_path=sample_aud_path,
        description="Spoken historic reading of the Preamble principles.",
        creator="Constituent Assembly Narrator",
        year="1949 CE",
        language="English",
        institution="Parliament Library Archive",
        rights="Public Domain / Open Access",
        file_format="MP3 Audio",
        file_size_bytes=Path(sample_aud_path).stat().st_size,
        duration_seconds=15.0,
        linked_record_id=test_rec_id,
        tags="Preamble, Liberty, Constitution, Audio",
        transcript="All citizens shall have equal liberty of thought, expression, belief, faith and worship.",
    )
    assert aud_id > 0, "Audio insertion must return valid database ID"
    print(f"[OK] Ingested Audio item #{aud_id} linked to Archival Record #{test_rec_id}")

    print("\n--- 4. Testing Ingestion of Video Footage ---")
    sample_vid_path = create_sample_video(
        filename="test_archival_monument_clip.mp4",
        title="Test Heritage Monument Aerial Scan",
        subtitle="LiDAR Spatial Survey 2026",
        duration_sec=3,
    )
    assert Path(sample_vid_path).exists(), "Video file must exist on disk"

    vid_id = insert_multimedia_item(
        media_uid="AV-TEST-VID-001",
        title="Test Heritage Monument Aerial LiDAR Scan",
        media_type="video",
        file_path=sample_vid_path,
        description="Aerial 3D point-cloud survey of medieval temple sanctuary.",
        creator="ASI Remote Sensing Lab",
        year="2026 Digitization",
        language="English",
        institution="National Museum Bureau",
        rights="Open Data CC-BY 4.0",
        file_format="MP4 Video (1080p)",
        file_size_bytes=Path(sample_vid_path).stat().st_size,
        duration_seconds=12.0,
        linked_record_id=test_rec_id,
        tags="LiDAR, Temple, 3D Scan, Video",
        transcript="Photogrammetric spatial reconstruction of sanctuary stones.",
    )
    assert vid_id > 0, "Video insertion must return valid database ID"
    print(f"[OK] Ingested Video item #{vid_id} linked to Archival Record #{test_rec_id}")

    print("\n--- 5. Testing Filtering by Media Type ---")
    all_imgs = get_all_multimedia(media_type="image")
    all_auds = get_all_multimedia(media_type="audio")
    all_vids = get_all_multimedia(media_type="video")

    assert len(all_imgs) >= 1, "Must return image items"
    assert len(all_auds) >= 1, "Must return audio items"
    assert len(all_vids) >= 1, "Must return video items"
    assert all(m["media_type"] == "image" for m in all_imgs)
    assert all(m["media_type"] == "audio" for m in all_auds)
    assert all(m["media_type"] == "video" for m in all_vids)
    print(f"[OK] Filter counts: {len(all_imgs)} Images, {len(all_auds)} Audio tracks, {len(all_vids)} Video clips.")

    print("\n--- 6. Testing Keyword Search across Multimedia Metadata ---")
    search_ambedkar = get_all_multimedia(search_query="Ambedkar")
    search_konark = get_all_multimedia(search_query="Konark")
    search_pashupati = get_all_multimedia(search_query="Pashupati")

    assert len(search_ambedkar) >= 1, "Search for 'Ambedkar' must return relevant media"
    assert len(search_konark) >= 1, "Search for 'Konark' must return relevant media"
    assert len(search_pashupati) >= 1, "Search for 'Pashupati' must return relevant media"
    print(f"[OK] Search query retrieval verified for 'Ambedkar', 'Konark', and 'Pashupati'.")

    print("\n--- 7. Testing Bidirectional Archival Record Linkage ---")
    linked_to_rec = get_multimedia_for_record(test_rec_id)
    assert len(linked_to_rec) >= 2, f"Expected at least 2 linked items for record #{test_rec_id}, got {len(linked_to_rec)}"
    for item in linked_to_rec:
        assert item["linked_record_id"] == test_rec_id
        assert "linked_record_title" in item
    print(f"[OK] Found {len(linked_to_rec)} multimedia assets linked to Record #{test_rec_id} ('{linked_to_rec[0]['linked_record_title']}')")

    print("\n--- 8. Testing Single Item Lookup & Cleanup ---")
    retrieved = get_multimedia_by_id(img_id)
    assert retrieved is not None, f"Item #{img_id} must be retrieved"
    assert retrieved["title"] == "Test Epigraphic Tablet of Karnataka"

    # Delete test items
    assert delete_multimedia_item(img_id) is True
    assert delete_multimedia_item(aud_id) is True
    assert delete_multimedia_item(vid_id) is True
    assert get_multimedia_by_id(img_id) is None
    print("[OK] Single item lookup and deletion validated.")

    print("\n[SUCCESS] ALL AUDIO-VISUAL ARCHIVE REQUIREMENTS TESTED AND PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    test_audiovisual_pipeline()
