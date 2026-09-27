"""
Digital Heritage Archive - Global Configuration
Handles filesystem paths, supported languages, database locations, and model defaults.
"""

from pathlib import Path
import os

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_documents"
PROCESSED_IMAGES_DIR = DATA_DIR / "processed_images"
AUDIO_VIDEO_DIR = DATA_DIR / "audio_video"
MULTIMEDIA_DIR = DATA_DIR / "multimedia"
MULTIMEDIA_IMAGES_DIR = MULTIMEDIA_DIR / "images"
MULTIMEDIA_AUDIO_DIR = MULTIMEDIA_DIR / "audio"
MULTIMEDIA_VIDEO_DIR = MULTIMEDIA_DIR / "video"
DB_DIR = DATA_DIR / "db"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
SAMPLE_DATA_DIR = DATA_DIR / "sample_data"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure all directories exist
for directory in [
    DATA_DIR,
    RAW_DOCS_DIR,
    PROCESSED_IMAGES_DIR,
    AUDIO_VIDEO_DIR,
    MULTIMEDIA_DIR,
    MULTIMEDIA_IMAGES_DIR,
    MULTIMEDIA_AUDIO_DIR,
    MULTIMEDIA_VIDEO_DIR,
    DB_DIR,
    VECTOR_STORE_DIR,
    SAMPLE_DATA_DIR,
    ASSETS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
SQLITE_DB_PATH = DB_DIR / "heritage_archive.db"
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = VECTOR_STORE_DIR / "faiss_metadata.json"

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Supported Archival Eras & Categories
ARCHIVAL_ERAS = [
    "Ancient / Vedic Era (Pre-600 BCE)",
    "Mauryan & Post-Mauryan (322 BCE - 320 CE)",
    "Gupta Golden Age (320 CE - 550 CE)",
    "Medieval & Chola / Vijayanagara (600 CE - 1526 CE)",
    "Mughal Era (1526 CE - 1757 CE)",
    "Colonial & Freedom Movement (1757 CE - 1947 CE)",
    "Post-Independence (1947 CE - Present)",
]

ARCHIVAL_CATEGORIES = [
    "Royal Decrees & Farmans",
    "Inscriptions & Copper Plates",
    "Manuscripts & Religious Texts",
    "Historical Maps & Cartography",
    "Legal & Revenue Records",
    "Freedom Struggle Pamphlets & Press",
    "Oral Testimonies & Folk Audio",
    "Archival Footage & Visual Records",
]

PRESERVATION_CONDITIONS = [
    "Pristine / Well Preserved",
    "Minor Degradation / Faded Ink",
    "Brittle / Fragmentary Edges",
    "Severe Water / Insect Damage",
    "Restored / Digitally Enhanced",
]

# Supported Languages for Translation & OCR
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "sa": "Sanskrit (संस्कृतम्)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "ur": "Urdu (اردو)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "fa": "Persian (فارسی)",
    "ar": "Arabic (العربية)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
}

# Tesseract Executable Path (if custom path needed on Windows)
TESSERACT_CMD = os.environ.get(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else "tesseract"
)
