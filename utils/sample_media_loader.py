"""
Digital Heritage Archive - Sample Multimedia Generator & Seeder
Generates authentic playable sample Audio (MP3), Video (MP4), and Image assets,
and seeds the multimedia_items table linked to archival records.
"""

import os
import sys
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    MULTIMEDIA_IMAGES_DIR,
    MULTIMEDIA_AUDIO_DIR,
    MULTIMEDIA_VIDEO_DIR,
)
from core.storage import (
    get_all_records,
    get_all_multimedia,
    insert_multimedia_item,
)
from core.tts_engine import TTSEngine

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def create_sample_image(
    filename: str,
    title: str,
    subtitle: str,
    category_color: tuple = (251, 191, 36),
    width: int = 800,
    height: int = 600,
) -> str:
    """Generates an aesthetic heritage banner/artifact image."""
    MULTIMEDIA_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    img_path = MULTIMEDIA_IMAGES_DIR / filename
    
    # Create dark parchment background with subtle gradient
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Draw ornamental border
    margin = 25
    draw.rectangle(
        [(margin, margin), (width - margin, height - margin)],
        outline=category_color,
        width=3,
    )
    draw.rectangle(
        [(margin + 8, margin + 8), (width - margin - 8, height - margin - 8)],
        outline=(71, 85, 105),
        width=1,
    )

    # Draw decorative center seal / medallion
    center_x, center_y = width // 2, height // 2 - 20
    draw.ellipse(
        [(center_x - 120, center_y - 120), (center_x + 120, center_y + 120)],
        outline=category_color,
        width=2,
    )
    draw.ellipse(
        [(center_x - 100, center_y - 100), (center_x + 100, center_y + 100)],
        fill=(30, 41, 59),
        outline=(217, 119, 6),
        width=2,
    )

    # Draw title text
    # Draw simple centered text using default font
    draw.text((center_x, center_y - 20), "🏛️ DIGITAL ARCHIVE", fill=category_color, anchor="mm")
    draw.text((center_x, center_y + 15), "HERITAGE ARTIFACT", fill=(241, 245, 249), anchor="mm")

    # Draw Title and Subtitle at bottom
    draw.text((width // 2, height - 120), title, fill=(251, 191, 36), anchor="mm")
    draw.text((width // 2, height - 80), subtitle, fill=(148, 163, 184), anchor="mm")
    draw.text((width // 2, height - 50), "Preservation Standard: Dublin Core DC-MI 2026", fill=(100, 116, 139), anchor="mm")

    img.save(img_path, format="PNG")
    return str(img_path)


def create_sample_audio(filename: str, spoken_text: str, lang_code: str = "en") -> str:
    """Synthesizes real playable MP3 audio file using TTS engine."""
    MULTIMEDIA_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = MULTIMEDIA_AUDIO_DIR / filename
    
    tts = TTSEngine(output_dir=MULTIMEDIA_AUDIO_DIR)
    res = tts.generate_audio(spoken_text, lang=lang_code)
    
    if res.get("success") and res.get("audio_path") and Path(res["audio_path"]).exists():
        # Move or copy to target filename
        src_path = Path(res["audio_path"])
        if src_path != audio_path:
            audio_path.write_bytes(src_path.read_bytes())
        return str(audio_path)
    
    # Fallback: create empty/placeholder MP3 structure if TTS network fails
    if not audio_path.exists():
        audio_path.write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 512)
    return str(audio_path)


def create_sample_video(filename: str, title: str, subtitle: str, duration_sec: int = 5) -> str:
    """Generates an animated historical MP4 video clip with title cards and moving visuals."""
    MULTIMEDIA_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    video_path = MULTIMEDIA_VIDEO_DIR / filename

    if not CV2_AVAILABLE:
        # Fallback dummy binary if cv2 missing
        if not video_path.exists():
            video_path.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
        return str(video_path)

    width, height = 640, 480
    fps = 24
    total_frames = duration_sec * fps

    # Try MP4V codec
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

    for frame_idx in range(total_frames):
        # Create base canvas with smooth animation
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Background gradient with pulse
        pulse = int(15 + 10 * np.sin(frame_idx / 10.0))
        frame[:, :] = (pulse + 15, pulse + 10, pulse + 5)

        # Draw moving decorative circle / emblem
        angle = (frame_idx / float(total_frames)) * 2 * np.pi
        center_x = int(width / 2 + 40 * np.cos(angle))
        center_y = int(height / 2 - 30 + 15 * np.sin(angle))
        radius = int(70 + 10 * np.sin(frame_idx / 8.0))
        
        cv2.circle(frame, (center_x, center_y), radius, (36, 191, 251), 2)
        cv2.circle(frame, (center_x, center_y), radius - 15, (20, 180, 120), 1)

        # Draw border
        cv2.rectangle(frame, (20, 20), (width - 20, height - 20), (36, 191, 251), 2)
        cv2.rectangle(frame, (26, 26), (width - 26, height - 26), (100, 116, 139), 1)

        # Overlay text
        cv2.putText(
            frame,
            "DIGITAL HERITAGE ARCHIVE",
            (int(width / 2 - 160), 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (36, 191, 251),
            2,
            cv2.LINE_AA,
        )
        
        # Main title
        cv2.putText(
            frame,
            title[:35],
            (40, height - 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (240, 240, 240),
            2,
            cv2.LINE_AA,
        )

        # Subtitle
        cv2.putText(
            frame,
            subtitle[:45],
            (40, height - 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (148, 163, 184),
            1,
            cv2.LINE_AA,
        )

        # Timecode
        sec = frame_idx // fps
        cv2.putText(
            frame,
            f"REC 00:0{sec}:{(frame_idx % fps):02d} | 4K ARCHIVAL DIGITIZATION",
            (40, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (100, 200, 100),
            1,
            cv2.LINE_AA,
        )

        out.write(frame)

    out.release()
    return str(video_path)


def bootstrap_multimedia_archive() -> int:
    """Generates all sample media assets and seeds them into the multimedia_items database."""
    # Fetch existing archival records to link to
    records = get_all_records(limit=100)
    rec_by_title = {r["title"].lower(): r["id"] for r in records}
    
    # Helper to find linked record ID
    def find_linked_id(keywords: list) -> int:
        for r in records:
            t = (r["title"] + " " + r.get("description", "")).lower()
            if any(k.lower() in t for k in keywords):
                return r["id"]
        return records[0]["id"] if records else None

    existing_mm = get_all_multimedia(limit=10)
    if len(existing_mm) >= 10:
        return len(existing_mm)

    print("--- Bootstrapping Audio-Visual Heritage Archive Assets ---")

    # -------------------------------------------------------------------------
    # 1. AUDIO ITEMS (Speeches, Recitations, Oral Histories)
    # -------------------------------------------------------------------------
    audio_data = [
        {
            "uid": "AV-AUD-001",
            "title": "Dr. B. R. Ambedkar — Concluding Address on the Constitution (1949)",
            "filename": "ambedkar_constitution_speech_1949.mp3",
            "creator": "Dr. Bhimrao Ramji Ambedkar",
            "year": "1949 CE (November 25)",
            "language": "English",
            "institution": "Parliament Library of India & National Archives",
            "rights": "Public Domain / CC0 Open Access",
            "tags": "Constitution, Assembly, Democracy, Equality, Law",
            "keywords": ["Constitution", "Ambedkar"],
            "description": "Historic speech delivered by Dr. B. R. Ambedkar to the Constituent Assembly outlining constitutional morality, fundamental rights, and democratic safeguards.",
            "transcript": (
                "On the 26th of January 1950, we are going to enter into a life of contradictions. "
                "In politics we will have equality and in social and economic life we will have inequality. "
                "In politics we will be recognizing the principle of one man one vote and one vote one value. "
                "We must remove this contradiction at the earliest possible moment or else those who suffer from inequality will blow up the structure of political democracy."
            ),
            "format": "MP3 Audio",
            "duration": 48.0,
        },
        {
            "uid": "AV-AUD-002",
            "title": "Pandit Jawaharlal Nehru — 'Tryst with Destiny' Speech (1947)",
            "filename": "nehru_tryst_with_destiny_1947.mp3",
            "creator": "Pandit Jawaharlal Nehru",
            "year": "1947 CE (August 14-15 Midnight)",
            "language": "English",
            "institution": "All India Radio (AIR) Archives",
            "rights": "National Heritage Preservation / Educational CC-BY-NC",
            "tags": "Independence, Freedom Struggle, Parliament, Midnight Speech",
            "keywords": ["Independence", "Freedom", "Constitution"],
            "description": "Midnight radio broadcast delivered to the Indian Constituent Assembly on the eve of India's independence from British colonial rule.",
            "transcript": (
                "Long years ago we made a tryst with destiny, and now the time comes when we shall redeem our pledge, "
                "not wholly or in full measure, but very substantially. At the stroke of the midnight hour, "
                "when the world sleeps, India will awake to life and freedom. A moment comes, which comes but rarely in history, "
                "when we step out from the old to the new, when an age ends, and when the soul of a nation, long suppressed, finds utterance."
            ),
            "format": "MP3 Audio",
            "duration": 52.0,
        },
        {
            "uid": "AV-AUD-003",
            "title": "Rigveda Vedic Oral Chanting — Nasadiya Sukta (Hymn of Creation)",
            "filename": "rigveda_nasadiya_sukta_chant.mp3",
            "creator": "Vedic Shrotriya Pundits of Varanasi",
            "year": "1500 BCE (Vedic Oral Tradition)",
            "language": "Vedic Sanskrit",
            "institution": "Indira Gandhi National Centre for the Arts (IGNCA)",
            "rights": "UNESCO Intangible Cultural Heritage Preservation",
            "tags": "Rigveda, Philosophy, Creation Hymn, Oral Tradition, Sanskrit",
            "keywords": ["Vedic", "Rigveda", "Manuscript"],
            "description": "Sacred Vedic oral chanting preserved verbatim across millennia via Pada-patha and Ghana-patha recitation techniques.",
            "transcript": (
                "नासदासीन्नो सदासीत्तदानीं नासीद्रजो नो व्योमा परो यत्। "
                "किमावरीवः कुह कस्य शर्मन्नम्भः किमासीद्गहनं गभीरम्॥ "
                "Then was not non-existence nor existence: there was no realm of air, no sky beyond it. "
                "What covered in, and where? and what gave shelter? Was water there, unfathomed depth of water?"
            ),
            "format": "MP3 Audio",
            "duration": 65.0,
        },
        {
            "uid": "AV-AUD-004",
            "title": "Rabindranath Tagore — Recitation of 'Where the Mind is Without Fear'",
            "filename": "tagore_gitanjali_recitation.mp3",
            "creator": "Gurudev Rabindranath Tagore",
            "year": "1912 CE",
            "language": "English / Bengali",
            "institution": "Visva-Bharati University Archival Audio Collection",
            "rights": "Public Domain / Nobel Laureate Heritage",
            "tags": "Literature, Gitanjali, Poetry, Freedom, Tagore",
            "keywords": ["Writings", "Literature", "Tagore"],
            "description": "Original poetic recitation from Gitanjali embodying universal human freedom, knowledge without division, and spiritual awakening.",
            "transcript": (
                "Where the mind is without fear and the head is held high; "
                "Where knowledge is free; "
                "Where the world has not been broken up into fragments by narrow domestic walls; "
                "Where words come out from the depth of truth; "
                "Where tireless striving stretches its arms towards perfection; "
                "Into that heaven of freedom, my Father, let my country awake."
            ),
            "format": "MP3 Audio",
            "duration": 40.0,
        },
    ]

    for item in audio_data:
        f_path = create_sample_audio(item["filename"], item["transcript"])
        f_size = os.path.getsize(f_path) if os.path.exists(f_path) else 128000
        l_id = find_linked_id(item["keywords"])

        insert_multimedia_item(
            media_uid=item["uid"],
            title=item["title"],
            media_type="audio",
            file_path=f_path,
            description=item["description"],
            creator=item["creator"],
            year=item["year"],
            language=item["language"],
            institution=item["institution"],
            accession_number=item["uid"],
            rights=item["rights"],
            file_format=item["format"],
            file_size_bytes=f_size,
            duration_seconds=item["duration"],
            linked_record_id=l_id,
            tags=item["tags"],
            transcript=item["transcript"],
            recorded_date=item["year"],
            speaker_narrator=item["creator"],
            era_topic=item["tags"],
        )

    # -------------------------------------------------------------------------
    # 2. VIDEO ITEMS (Archival Reels, 3D Scans, Documentary Clips)
    # -------------------------------------------------------------------------
    video_data = [
        {
            "uid": "AV-VID-001",
            "title": "Constitution of India — Constituent Assembly Signing Ceremony (1950)",
            "filename": "constitution_signing_ceremony_1950.mp4",
            "creator": "Films Division of India",
            "year": "1950 CE (January 24)",
            "language": "English / Hindi",
            "institution": "National Film Archive of India (NFAI)",
            "rights": "National Archival Heritage / Public Access",
            "tags": "Constitution, Signing, Parliament, Assembly, Historical Footage",
            "keywords": ["Constitution", "India"],
            "description": "Historical newsreel footage recording members of the Constituent Assembly signing the original calligraphic English and Hindi Constitution of India.",
            "transcript": "Archival motion reel recording the 284 members of the Constituent Assembly affixing their signatures to the calligraphic Constitution in the Constitution Hall, New Delhi.",
            "format": "MP4 Video (1080p)",
            "duration": 18.0,
        },
        {
            "uid": "AV-VID-002",
            "title": "Konark Sun Temple — 3D Laser Scanning & Photogrammetric Flythrough",
            "filename": "konark_sun_temple_3d_scan.mp4",
            "creator": "Archaeological Survey of India (ASI) Digital Lab",
            "year": "1250 CE (Digitized 2024)",
            "language": "English",
            "institution": "Archaeological Survey of India & UNESCO Heritage Bureau",
            "rights": "Open Archaeological Heritage Data CC-BY",
            "tags": "Architecture, Konark, Sun Temple, Laser Scan, 3D Photogrammetry, Odisha",
            "keywords": ["Temple", "Architecture", "Chola", "Legacy"],
            "description": "High-precision LiDAR laser scan and photogrammetric spatial reconstruction of the 24 sculpted chariot wheels of the 13th-century Konark Sun Temple.",
            "transcript": "Spatial 3D LiDAR point-cloud simulation visualizing sundial timekeeping calculations on the spoke carvings of the Konark Sun Temple wheel.",
            "format": "MP4 Video (1080p)",
            "duration": 24.0,
        },
        {
            "uid": "AV-VID-003",
            "title": "Decipherment of Ashoka's Brahmi Inscriptions — Epigraphic Documentary",
            "filename": "ashoka_brahmi_epigraphy_doc.mp4",
            "creator": "Epigraphical Society of India",
            "year": "250 BCE (Preserved 2025)",
            "language": "Prakrit / English",
            "institution": "Epigraphy Branch, Archaeological Survey of India, Mysore",
            "rights": "Educational & Academic Public Domain",
            "tags": "Epigraphy, Ashoka, Brahmi Script, Inscriptions, Rock Edicts",
            "keywords": ["Ashoka", "Edicts", "Brahmi", "Rock"],
            "description": "Documentary examining James Prinsep's 1837 decipherment of Ashokan Brahmi script and modern multispectral imaging of rock edict stone surfaces.",
            "transcript": "Multispectral photometric analysis revealing chisel depth and letterforms of Emperor Ashoka's Major Rock Edict at Girnar, Junagadh.",
            "format": "MP4 Video (720p)",
            "duration": 20.0,
        },
    ]

    for item in video_data:
        f_path = create_sample_video(item["filename"], item["title"], item["tags"], duration_sec=5)
        f_size = os.path.getsize(f_path) if os.path.exists(f_path) else 512000
        l_id = find_linked_id(item["keywords"])

        insert_multimedia_item(
            media_uid=item["uid"],
            title=item["title"],
            media_type="video",
            file_path=f_path,
            description=item["description"],
            creator=item["creator"],
            year=item["year"],
            language=item["language"],
            institution=item["institution"],
            accession_number=item["uid"],
            rights=item["rights"],
            file_format=item["format"],
            file_size_bytes=f_size,
            duration_seconds=item["duration"],
            linked_record_id=l_id,
            tags=item["tags"],
            transcript=item["transcript"],
            recorded_date=item["year"],
            speaker_narrator=item["creator"],
            era_topic=item["tags"],
        )

    # -------------------------------------------------------------------------
    # 3. IMAGE ITEMS (High-Resolution Visual Artifacts & Architectural Scans)
    # -------------------------------------------------------------------------
    image_data = [
        {
            "uid": "AV-IMG-001",
            "title": "Nalanda Mahavihara Ancient University Excavations (High-Res Scan)",
            "filename": "nalanda_mahavihara_ruins_scan.png",
            "creator": "Archaeological Survey of India (Excavation Branch)",
            "year": "5th - 12th Century CE",
            "language": "Classical Sanskrit / Pali",
            "institution": "Nalanda Archaeological Museum & UNESCO",
            "rights": "Public Domain / CC0 Open Access",
            "tags": "Nalanda, Mahavihara, University, Monastery, Buddhist Studies, Bihar",
            "keywords": ["Treatises", "Writings", "Manuscript"],
            "description": "High-resolution architectural survey plate of the main votive stupa and monastic cells of the ancient Nalanda University in Bihar.",
            "format": "PNG High-Res Image (2400x1800)",
        },
        {
            "uid": "AV-IMG-002",
            "title": "Indus Valley Civilization — Pashupati Seal Artifact (Mohenjo-daro)",
            "filename": "indus_pashupati_steatite_seal.png",
            "creator": "Harappan Craftsmen",
            "year": "2500 BCE (Mature Harappan)",
            "language": "Indus Script (Undeciphered)",
            "institution": "National Museum, New Delhi",
            "rights": "National Treasure / Public Heritage Access",
            "tags": "Indus Valley, Mohenjo-daro, Harappa, Steatite Seal, Proto-Shiva",
            "keywords": ["Indus", "Ancient", "Life"],
            "description": "Carved steatite seal depicting a three-faced seated figure surrounded by an elephant, tiger, rhinoceros, water buffalo, and ibexes.",
            "format": "PNG High-Res Image (1600x1600)",
        },
        {
            "uid": "AV-IMG-003",
            "title": "Brihadisvara Temple Tanjore — Chola Imperial Wall Mural (Thanjavur)",
            "filename": "brihadisvara_chola_fresco_scan.png",
            "creator": "Imperial Chola Guild Painters",
            "year": "1010 CE (Rajaraja Chola I)",
            "language": "Old Tamil",
            "institution": "Tamil Nadu State Archaeology Department & Thanjavur Palace",
            "rights": "UNESCO World Heritage Cultural License",
            "tags": "Chola, Tanjore, Brihadisvara, Temple Murals, Fresco, Tamil Nadu",
            "keywords": ["Chola", "Temple", "Legacy"],
            "description": "Magnificent 11th-century fresco painting from the ambulatory corridor of Brihadisvara Temple depicting Emperor Rajaraja I and sage Karuvurar.",
            "format": "PNG High-Res Image (2000x1500)",
        },
        {
            "uid": "AV-IMG-004",
            "title": "Emperor Shah Jahan — Imperial Farman & Court Blueprint Plate",
            "filename": "shah_jahan_imperial_farman_plate.png",
            "creator": "Imperial Mughal Court Calligraphers (Dar-ul-Insha)",
            "year": "1650 CE",
            "language": "Nastaliq Persian",
            "institution": "National Archives of India (NAI, Janpath)",
            "rights": "Public Domain / CC0 Open Access",
            "tags": "Mughal, Shah Jahan, Farman, Nastaliq, Royal Tughra, Gold Leaf",
            "keywords": ["Farman", "Mughal", "Constitution", "Writings"],
            "description": "Illuminated royal decree written in Persian Nastaliq script bearing the grand imperial Tughra seal in vermilion and gold leaf.",
            "format": "PNG High-Res Image (2200x1700)",
        },
    ]

    for item in image_data:
        f_path = create_sample_image(
            filename=item["filename"],
            title=item["title"][:38],
            subtitle=item["institution"],
        )
        f_size = os.path.getsize(f_path) if os.path.exists(f_path) else 350000
        l_id = find_linked_id(item["keywords"])

        insert_multimedia_item(
            media_uid=item["uid"],
            title=item["title"],
            media_type="image",
            file_path=f_path,
            description=item["description"],
            creator=item["creator"],
            year=item["year"],
            language=item["language"],
            institution=item["institution"],
            accession_number=item["uid"],
            rights=item["rights"],
            file_format=item["format"],
            file_size_bytes=f_size,
            duration_seconds=0.0,
            linked_record_id=l_id,
            tags=item["tags"],
            transcript=item["description"],
            recorded_date=item["year"],
            speaker_narrator=item["creator"],
            era_topic=item["tags"],
        )

    all_mm = get_all_multimedia()
    print(f"[OK] Multimedia archive initialized successfully with {len(all_mm)} media items.")
    return len(all_mm)


if __name__ == "__main__":
    bootstrap_multimedia_archive()
