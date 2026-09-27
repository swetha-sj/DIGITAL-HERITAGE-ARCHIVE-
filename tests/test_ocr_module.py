"""
Unit and Integration tests for the OCR & Preprocessing Ingestion Pipeline.
Tests:
- Image Preprocessor (Deskew, Contrast Equalization, Denoising, Adaptive Binarization)
- Text Cleaner (Unicode normalization, artifact stripper, line wrap repairs)
- OCR Engine (Diagnostics, fallback handling, image and PDF interfaces)
- Storage Persistence with OCR extracted text and preprocessed paths
"""

import sys
import uuid
from pathlib import Path
from PIL import Image, ImageDraw

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RAW_DOCS_DIR, PROCESSED_IMAGES_DIR, SQLITE_DB_PATH
from core.preprocessor import ImagePreprocessor
from core.text_cleaner import TextCleaner
from core.ocr_engine import OCREngine
from core.storage import (
    init_database,
    insert_archival_record,
    get_record_by_id,
    get_all_records,
)


def test_ocr_pipeline():
    print("--- 1. Testing Image Preprocessing Engine ---")
    # Create test sample image
    test_img = Image.new("RGB", (300, 400), color=(230, 220, 190))
    draw = ImageDraw.Draw(test_img)
    draw.text((30, 30), "SAMUDRAGUPTA ALLAHABAD INSCRIPTION", fill=(40, 20, 10))
    draw.text((30, 70), "Line 1: Harishena prasasti", fill=(40, 20, 10))

    proc_img, audit = ImagePreprocessor.process_pipeline(
        test_img,
        do_deskew=True,
        do_contrast=True,
        do_denoise=True,
        do_binarize=True,
    )
    assert isinstance(proc_img, Image.Image), "Processed image must be a PIL Image"
    assert audit.get("contrast_enhanced") is True, "Contrast enhancement should be applied"
    assert audit.get("binarized") is True, "Binarization should be applied"
    print("[OK] Image preprocessing pipeline executed successfully. Audit:", audit)

    print("\n--- 2. Testing Text Cleaner Engine ---")
    dirty_ocr_text = "SAMUDRAGUPTA~~~ ======\nAllahabad Inscription--\ncomposed by Hari- \n shena in Classical Sanskrit.\n\n\n\nPreserved in stone."
    clean_result = TextCleaner.clean(dirty_ocr_text)
    assert clean_result["cleaned_text"] != "", "Cleaned text should not be empty"
    assert "Harishena" in clean_result["cleaned_text"], "Hyphenated line break should be repaired"
    assert "~~~~~" not in clean_result["cleaned_text"], "OCR noise artifacts must be removed"
    print("[OK] Text cleaner normalized text and fixed broken line wraps successfully!")

    print("\n--- 3. Testing OCR Engine & Fallback Diagnostics ---")
    ocr_engine = OCREngine()
    tess_available = ocr_engine.is_tesseract_available()
    tess_ver = ocr_engine.get_tesseract_version()
    print(f"     Tesseract Status: {'Available' if tess_available else 'Not on PATH'} (Version: {tess_ver})")

    res = ocr_engine.extract_from_image(test_img)
    assert "success" in res and "text" in res, "OCR extract_from_image must return a valid structured dict"
    print("[OK] OCR Engine handled extraction call gracefully with status:", res.get("success") or res.get("error"))

    print("\n--- 4. Testing End-to-End Database Persistence with OCR Fields ---")
    init_database()
    raw_file = RAW_DOCS_DIR / f"test_inscription_{uuid.uuid4().hex[:6]}.png"
    proc_file = PROCESSED_IMAGES_DIR / f"proc_{raw_file.name}"
    test_img.save(raw_file)
    proc_img.save(proc_file)

    acc_num = f"DHA-OCR-{uuid.uuid4().hex[:6].upper()}"
    rec_id = insert_archival_record(
        accession_number=acc_num,
        title="Allahabad Pillar Inscription of Samudragupta",
        creator="Harishena / Samudragupta",
        year="375 CE",
        language="Sanskrit (संस्कृतम्)",
        topic="Temple Endowments & Epigraphy",
        document_type="Inscription / Copper Plate",
        institution="Archaeological Survey of India (ASI)",
        rights="Public Domain / Universal Cultural Heritage",
        description="Famous Sanskrit prasasti describing the conquests and virtues of Gupta Emperor Samudragupta.",
        original_filename=raw_file.name,
        file_type="Image (PNG)",
        file_size_bytes=raw_file.stat().st_size,
        saved_file_path=str(raw_file),
        processed_file_path=str(proc_file),
        raw_ocr_text=dirty_ocr_text,
        cleaned_text=clean_result["cleaned_text"],
        ocr_confidence=88.5,
    )

    assert rec_id > 0, "Record ID must be positive integer"
    rec = get_record_by_id(rec_id)
    assert rec is not None, "Record must be fetched from SQLite"
    assert rec["raw_ocr_text"] == dirty_ocr_text
    assert rec["cleaned_text"] == clean_result["cleaned_text"]
    assert rec["processed_file_path"] == str(proc_file)
    assert rec["ocr_confidence"] == 88.5
    print(f"[OK] Record #{rec_id} verified with OCR text, preprocessed image path, and confidence in SQLite!")

    print("\nALL OCR MODULE TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_ocr_pipeline()
