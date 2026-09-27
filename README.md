# 🏛️ DIGITAL HERITAGE ARCHIVE
### *National Heritage Discovery & Preservation Platform • Ministry of Culture*

An end-to-end intelligent digital preservation and discovery platform designed for ancient manuscripts, historical archives, royal decrees, oral histories, and multimedia cultural artifacts.

---

## 🌟 Key Capabilities & Workflow

```
[ Archival Document / Audio / Video ]
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 1. Ingestion & Preprocessing    │ ➔ Deskew, Contrast Enhancement, Denoising, Binarization
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 2. OCR & Text Cleaning          │ ➔ Tesseract / Multi-engine OCR, Unicode Normalization, Regex Correction
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 3. Dublin Core Metadata Entry   │ ➔ Title, Era/Dynasty, Region, Language, Preservation Condition
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 4. Storage & Hybrid Indexing    │ ➔ SQLite (Relational Catalog) + ChromaDB (Vector Embeddings)
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 5. Discovery & AI Research      │ ➔ Hybrid Search (Keyword + Semantic) & RAG Assistant with Source Citations
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 6. Multimodal Heritage Suite    │ ➔ Multilingual Translation, Text-to-Speech, Oral History AV Archive
 └───────────────┬─────────────────┘
                 │
                 ▼
 ┌─────────────────────────────────┐
 │ 7. Institutional Management     │ ➔ Interactive Era Timeline, Curator Analytics, Preservation Condition Logs
 └─────────────────────────────────┘
```

---

## 📁 Clean Project Architecture

```
Digital_Heritage_Archive/
│
├── app.py                          # Streamlit Main Dashboard & Navigation
├── config.py                       # Configuration (Paths, Languages, Default Settings)
├── requirements.txt                # Python Dependencies
├── README.md                       # Comprehensive Documentation
│
├── core/                           # Modular Processing & AI Engines
│   ├── __init__.py
│   ├── preprocessor.py             # OpenCV image enhancements (deskew, denoise, binarize, contrast)
│   ├── ocr_engine.py               # Robust OCR Engine with multi-language & fallback support
│   ├── text_cleaner.py             # Unicode normalizer, artifact stripper, spell corrector
│   ├── metadata_schema.py          # Dublin Core + Heritage Archival Data Models (Pydantic)
│   ├── storage.py                  # Local File Storage & SQLite Database Management
│   ├── search_engine.py            # Hybrid Search Engine (SQLite FTS / BM25 + ChromaDB Vector DB)
│   ├── rag_engine.py               # RAG Heritage Research Assistant with source verification
│   ├── translator.py               # Multilingual Translator (Indic & Global languages)
│   ├── tts_engine.py               # Text-to-Speech Engine for audio playback
│   └── timeline_builder.py         # Chronological data builder for interactive timelines
│
├── views/                          # Streamlit UI Subsystems & Pages
│   ├── __init__.py
│   ├── 1_Ingestion_Pipeline.py      # Upload ➔ Preprocessing ➔ OCR ➔ Metadata Entry
│   ├── 2_Document_Viewer.py        # High-res Viewer, Side-by-side Inspection, OCR Highlight
│   ├── 3_Smart_Search.py           # Hybrid Keyword + Semantic Search with Faceted Filters
│   ├── 4_AI_Research_Hub.py        # RAG Chatbot, Source Grounding, Multilingual Translation & TTS
│   ├── 5_Heritage_Timeline.py      # Interactive Dynasty/Era Chronological Timeline
│   ├── 6_AV_Oral_History.py        # Audio/Video Archive & Oral Testimonies Player
│   └── 7_Institutional_Admin.py     # Curator Stats, Conservation Logs, Audit Trails & PDF Reports
│
├── data/                           # Local Persistent Archive Storage
│   ├── raw_documents/              # Original uploaded documents & manuscripts
│   ├── processed_images/           # Enhanced & cleaned document images
│   ├── audio_video/                # Multimedia audio/video files
│   ├── db/                         # SQLite Database (`heritage_archive.db`)
│   ├── vector_store/               # ChromaDB Persistent Vector Index
│   └── sample_data/                # Built-in sample archival documents for instant demonstration
│
├── assets/                         # Static Assets & Styling
│   └── style.css                   # Custom Royal Heritage Dark/Gold Glassmorphism Theme
│
└── utils/                          # Utility Helpers
    ├── __init__.py
    ├── logger.py                   # System & Audit Logger
    └── sample_loader.py            # Auto-populates rich demo records on first startup
```

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend / Web UI** | Streamlit, Streamlit Extras, Plotly, Custom Vanilla CSS (Heritage Glassmorphism) |
| **Image Preprocessing** | OpenCV (`cv2`), Pillow (`PIL`), NumPy, SciPy |
| **OCR & Extraction** | PyTesseract (Tesseract OCR), PyPDF2, pdf2image |
| **NLP & Text Cleaning** | Regex, Python `unicodedata`, Deep Translator |
| **Storage & Database** | SQLite (Structured Archival Catalog), Local File Store |
| **Vector Database & Search** | ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **AI & RAG Engine** | LangChain / Google Gemini API / HuggingFace with Citation Grounding |
| **Voice & Speech** | gTTS (Google Text-to-Speech) |
| **Analytics & Timeline** | Plotly Express, Pandas |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ installed
- *(Optional for full OCR)*: Tesseract-OCR binary installed on system (built-in fallback provided if not present)

### 2. Installation
```powershell
# Navigate to project directory
cd c:\Users\User\Desktop\Digital_Heritage_Archive

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Prototype
```powershell
streamlit run app.py
```

---

## 🏛️ Platform Architecture & Engineering Highlights
- **100% Real Working Local Prototype**: Functional SQLite DB, persistent ChromaDB/FAISS vector store, OpenCV filters, real-time OCR, and live RAG citations.
- **Zero-Crash Fallback Architecture**: Built-in sample documents across Indian Eras (Maurya, Gupta, Mughal, Chola, Colonial, Modern) ensure immediate demo-readiness even without internet or hardware accelerators.
- **Standards Compliant**: Implements international **Dublin Core** metadata standards for cultural archives.
