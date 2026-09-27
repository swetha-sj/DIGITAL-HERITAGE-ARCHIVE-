"""
Digital Heritage Archive - Sample Data Bootstrapper
Populates realistic historical records, royal decrees, manuscripts, and epigraphs across Indian history into SQLite.
"""

from pathlib import Path
from PIL import Image, ImageDraw
from config import RAW_DOCS_DIR, SAMPLE_DATA_DIR
from core.storage import get_all_records, insert_archival_record
from core.search_engine import SmartSearchEngine
import uuid


def create_parchment_sample_image(filename: str, title_text: str, body_text: str) -> str:
    """Creates a sample parchment-styled archival image for demo testing."""
    target_path = SAMPLE_DATA_DIR / filename
    if target_path.exists():
        return str(target_path)

    # 800 x 1000 canvas with antique parchment background color
    img = Image.new("RGB", (800, 1000), color=(244, 233, 206))
    draw = ImageDraw.Draw(img)

    # Add a decorative archival border
    draw.rectangle([(20, 20), (780, 980)], outline=(120, 80, 40), width=3)
    draw.rectangle([(25, 25), (775, 975)], outline=(180, 140, 90), width=1)

    # Write heading
    draw.text((40, 50), title_text.upper()[:45], fill=(60, 30, 10))
    draw.line([(40, 80), (760, 80)], fill=(120, 80, 40), width=2)

    # Write body lines
    y = 110
    lines = body_text.split("\n")
    for line in lines[:24]:
        draw.text((40, y), line[:65], fill=(40, 20, 10))
        y += 28

    img.save(target_path)
    return str(target_path)


def bootstrap_sample_data() -> int:
    """
    Populates curated historical documents spanning all 5 timeline categories:
    Life, Writings, Speeches, Constitution, Legacy across Indian Eras.
    """
    samples = [
        # --- 1. SPEECHES ---
        {
            "title": "Major Rock Edict XII of Ashoka on Religious Harmony & Speech Restraint",
            "filename": "ashoka_major_rock_edict_xii.png",
            "creator": "Emperor Ashoka Maurya (Piyadasi)",
            "year": "257 BCE",
            "language": "Sanskrit (संस्कृतम्)",
            "topic": "Speeches & Royal Proclamations",
            "document_type": "Rock Edict / Public Speech Inscription",
            "institution": "Archaeological Survey of India (ASI)",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Historic speech and rock edict of Emperor Ashoka advocating universal religious tolerance, moral restraint in speech, and mutual respect among faiths.",
            "transcript": (
                "Beloved-of-the-Gods, King Piyadasi, speaks thus to all assembly:\n"
                "He honors the householders and ascetics of all creeds with gifts and reverence.\n"
                "The essential root of Dhamma is restraint in speech: not praising one's own faith\n"
                "or condemning another without weighty reason. Concord alone is meritorious,\n"
                "whereby all may listen to and respect one another's tenets."
            ),
        },
        {
            "title": "Quit India Movement Secret Directive & Proclamation",
            "filename": "quit_india_secret_bulletin_1942.png",
            "creator": "Congress Underground Directorate",
            "year": "1942 CE",
            "language": "English",
            "topic": "Speeches & Freedom Proclamations",
            "document_type": "Historical Proclamation / Speech Bulletin",
            "institution": "National Archives of India",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Historical proclamation and rallying address issued during the August 1942 Quit India Movement proclaiming total civil disobedience.",
            "transcript": (
                "DO OR DIE! Following the historic Gowalia Tank address, let every Indian consider\n"
                "himself a free citizen. The final struggle for India's liberation has commenced.\n"
                "Keep the flame of non-violent resistance burning in every village and town.\n"
                "Inquilab Zindabad! Karenge Ya Marenge!"
            ),
        },

        # --- 2. CONSTITUTION ---
        {
            "title": "Imperial Farman of Emperor Akbar on Sulh-i-Kul & Land Grants",
            "filename": "akbar_farman_sulh_i_kul.png",
            "creator": "Jalal-ud-din Muhammad Akbar",
            "year": "1582 CE",
            "language": "Persian (فارسی)",
            "topic": "Royal Decrees & Constitutional Treaties",
            "document_type": "Royal Decree / Farman",
            "institution": "National Archives of India",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Imperial Farman constitutional decree establishing universal peace (Sulh-i-Kul) and granting tax-free perpetual land endowments for public welfare.",
            "transcript": (
                "By the Order of the Sovereign, Jalal-ud-din Muhammad Akbar Badshah Ghazi.\n"
                "Under the constitutional principle of Universal Peace (Sulh-i-Kul), all subjects\n"
                "are guaranteed freedom of worship without imperial hindrance.\n"
                "Five hundred bighas of cultivable land are hereby endowed in perpetuity\n"
                "free from all cesses and sovereign levies."
            ),
        },
        {
            "title": "Constitution of India - Preamble & Fundamental Rights Draft",
            "filename": "constitution_india_preamble_draft_1949.png",
            "creator": "Dr. B.R. Ambedkar / Drafting Committee",
            "year": "1949 CE",
            "language": "English",
            "topic": "Constitutional Law & Sovereign Charters",
            "document_type": "Constitutional Charter / Sovereign Draft",
            "institution": "Parliament House Library / National Archives",
            "rights": "National Archival Heritage of India",
            "description": "Foundational sovereign document establishing the Republic of India, securing Justice, Liberty, Equality, and Fraternity for all citizens.",
            "transcript": (
                "WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a\n"
                "SOVEREIGN DEMOCRATIC REPUBLIC and to secure to all its citizens:\n"
                "JUSTICE, social, economic and political; LIBERTY of thought, expression, belief, faith and worship;\n"
                "EQUALITY of status and of opportunity; and to promote among them all\n"
                "FRATERNITY assuring the dignity of the individual and the unity of the Nation."
            ),
        },

        # --- 3. WRITINGS ---
        {
            "title": "Kautilya's Arthashastra on Statecraft & Treasury Administration",
            "filename": "kautilya_arthashastra_manuscript.png",
            "creator": "Acharya Chanakya (Kautilya)",
            "year": "300 BCE",
            "language": "Sanskrit (संस्कृतम्)",
            "topic": "Scholarly Treatises & Political Philosophy",
            "document_type": "Palm-Leaf Manuscript Treatise",
            "institution": "Oriental Research Institute, Mysore",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Ancient Sanskrit treatise on statecraft, economic policy, military strategy, civic administration, and royal duties (Rajadharma).",
            "transcript": (
                "In the happiness of his subjects lies the king's happiness; in their welfare his welfare.\n"
                "Whatever pleases himself the king shall not consider as good, but whatever pleases\n"
                "his subjects he shall consider as good. The root of wealth is the state treasury,\n"
                "and righteousness is the foundation of all sovereign power."
            ),
        },
        {
            "title": "Baburnama - Illustrated Royal Memoirs of Emperor Babur",
            "filename": "baburnama_illustrated_manuscript_1526.png",
            "creator": "Zahir-ud-din Muhammad Babur",
            "year": "1526 CE",
            "language": "Chagatai Turkic / Persian",
            "topic": "Historical Memoirs & Literary Chronicles",
            "document_type": "Illuminated Manuscript",
            "institution": "National Museum, New Delhi",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Personal memoirs and geographic observations of Babur describing the flora, fauna, architecture, and governance of 16th-century Hindustan.",
            "transcript": (
                "Hindustan is a country of few charms. Its people have no good looks; of social intercourse,\n"
                "there is none; of genius and capacity, there is none; in handicrafts and work there is no form or symmetry.\n"
                "Yet it is a wonderful country: it has vast amounts of gold and silver; its craftsmen in every trade are boundless."
            ),
        },

        # --- 4. LIFE ---
        {
            "title": "Samudragupta Allahabad Pillar Inscription on Imperial Accession",
            "filename": "samudragupta_allahabad_pillar.png",
            "creator": "Court Poet Harishena",
            "year": "375 CE",
            "language": "Sanskrit (संस्कृतम्)",
            "topic": "Biographical Chronicles & Imperial Dynasties",
            "document_type": "Stone Inscription / Prasasti",
            "institution": "Archaeological Survey of India (ASI)",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Celebrated Sanskrit eulogy composed by Harishena recounting the life, musical talents, poetic virtues, and military campaigns of Samudragupta.",
            "transcript": (
                "Whose mind was proficient in establishing the order of the scriptures, who was the builder\n"
                "of the pale of religion, whose radiant fame moved over the three worlds.\n"
                "He who surpassed Brihaspati in sharp intellect, and Tumburu and Narada in musical skill,\n"
                "the noble King of Kings, Samudragupta, beloved of his father Chandragupta."
            ),
        },
        {
            "title": "Coronation Charter & Life Chronicle of Emperor Harsha",
            "filename": "harsha_vardhana_coronation_charter_628.png",
            "creator": "Emperor Harsha Vardhana",
            "year": "628 CE",
            "language": "Sanskrit (संस्कृतम्)",
            "topic": "Royal Chronicles & Dynastic Milestones",
            "document_type": "Copper Plate Charter",
            "institution": "National Archives of India",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Royal copper plate recording the life and benevolent governance of King Harsha following his coronation at Kannauj.",
            "transcript": (
                "Sri Harsha Deva, worshipper of Maheshvara and Sun, following the assembly of Kannauj:\n"
                "By this royal copper charter, all tax revenues from the village of Somakunda\n"
                "are dedicated to the maintenance of travelers, scholars, and medical dispensaries in perpetuity."
            ),
        },

        # --- 5. LEGACY ---
        {
            "title": "Thanjavur Brihadisvara Temple Chola Copper Plate Grant",
            "filename": "rajaraja_chola_copper_grant.png",
            "creator": "Rajaraja Chola I",
            "year": "1010 CE",
            "language": "Tamil (தமிழ்)",
            "topic": "Temple Endowments & Epigraphy",
            "document_type": "Inscription / Copper Plate",
            "institution": "Saraswathi Mahal Library, Thanjavur",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Chola royal inscription recording the legacy endowment of villages, gold, and bronze deities to the Peruvudaiyar Temple.",
            "transcript": (
                "Hail Prosperity! In the 25th year of the reign of King Rajakesarivarman, alias Sri Rajaraja Deva.\n"
                "The Great King endowed villages, gold ornaments studded with rubies, and bronze deities to the\n"
                "Peruvudaiyar Temple of Thanjavur. The administration shall be supervised by the assembly of the Sabha."
            ),
        },
        {
            "title": "Sanchi Stupa Archaeological Heritage & Conservation Charter",
            "filename": "sanchi_stupa_conservation_charter_1919.png",
            "creator": "Sir John Marshall / ASI",
            "year": "1919 CE",
            "language": "English",
            "topic": "Heritage Conservation & Preservation Legacy",
            "document_type": "Archival Conservation Charter",
            "institution": "Archaeological Survey of India (ASI)",
            "rights": "Public Domain / Universal Cultural Heritage",
            "description": "Historic conservation charter detailing the monumental preservation and scientific restoration of the Great Stupa at Sanchi.",
            "transcript": (
                "Scientific restoration report on the Great Stupa at Sanchi, Bhopal State.\n"
                "The four carved Torana gateways, having suffered weathering across two millennia,\n"
                "are reinforced with structural grout and protective drainage to ensure eternal preservation\n"
                "for future generations of world cultural heritage."
            ),
        },
    ]

    existing = get_all_records(limit=200)
    existing_titles = {r["title"] for r in existing}

    added = 0
    for item in samples:
        if item["title"] in existing_titles:
            continue

        img_path = create_parchment_sample_image(
            filename=item["filename"],
            title_text=item["title"],
            body_text=item["transcript"],
        )

        acc_num = f"DHA-{item['year'].replace(' ', '-').upper()}-{uuid.uuid4().hex[:4].upper()}"
        file_size = Path(img_path).stat().st_size if Path(img_path).exists() else 2048

        insert_archival_record(
            accession_number=acc_num,
            title=item["title"],
            creator=item["creator"],
            year=item["year"],
            language=item["language"],
            topic=item["topic"],
            document_type=item["document_type"],
            institution=item["institution"],
            rights=item["rights"],
            description=item["description"],
            original_filename=item["filename"],
            file_type="Image (PNG)",
            file_size_bytes=file_size,
            saved_file_path=img_path,
            processed_file_path=img_path,
            raw_ocr_text=item["transcript"],
            cleaned_text=item["transcript"],
            ocr_confidence=95.0,
        )
        added += 1

    # Reindex FAISS vector index if new records added
    if added > 0:
        try:
            engine = SmartSearchEngine()
            engine.reindex_all_documents()
        except Exception:
            pass

    return len(get_all_records(limit=200))
