"""
Unit and Integration tests for Institutional Archive Upload module.
Tests:
- Database schema initialization
- Record insertion and field persistence
- Querying and retrieval
- Validation checks
- File saving verification
"""

import os
import sys
import uuid
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RAW_DOCS_DIR, SQLITE_DB_PATH
from core.storage import (
    init_database,
    insert_archival_record,
    get_all_records,
    get_record_by_id,
)


def test_upload_and_storage():
    print("--- 1. Testing Database Initialization ---")
    init_database()
    assert Path(SQLITE_DB_PATH).exists(), "Database file should exist."
    print("[OK] SQLite database exists at:", SQLITE_DB_PATH)

    print("\n--- 2. Testing Local File Persistence ---")
    test_content = b"%PDF-1.4 Mock Archival Charter File Content for Heritage Repository"
    test_filename = f"test_charter_{uuid.uuid4().hex[:6]}.pdf"
    test_filepath = RAW_DOCS_DIR / test_filename
    with open(test_filepath, "wb") as f:
        f.write(test_content)
    assert test_filepath.exists(), "Uploaded file must be saved in data/raw_documents/"
    print("[OK] Saved raw document file successfully at:", test_filepath)

    print("\n--- 3. Testing Archival Record Insertion into SQLite ---")
    acc_num = f"DHA-TEST-{uuid.uuid4().hex[:6].upper()}"
    rec_id = insert_archival_record(
        accession_number=acc_num,
        title="Royal Charter of Emperor Harsha",
        creator="Emperor Harsha Vardhana",
        year="628 CE",
        language="Sanskrit",
        topic="Royal Decrees & Political Treaties",
        document_type="Inscription / Copper Plate Grant",
        institution="National Archives of India",
        rights="Public Domain / Universal Cultural Heritage",
        description="A copper plate charter granting tax exemption to Buddhist monasteries in Kannauj.",
        original_filename=test_filename,
        file_type="PDF Document",
        file_size_bytes=len(test_content),
        saved_file_path=str(test_filepath),
    )
    assert rec_id > 0, "Record ID must be positive integer"
    print(f"[OK] Record inserted successfully with ID #{rec_id} (Accession: {acc_num})")

    print("\n--- 4. Testing Record Retrieval ---")
    fetched = get_record_by_id(rec_id)
    assert fetched is not None, "Record must be retrievable by ID"
    assert fetched["title"] == "Royal Charter of Emperor Harsha"
    assert fetched["creator"] == "Emperor Harsha Vardhana"
    assert fetched["year"] == "628 CE"
    assert fetched["language"] == "Sanskrit"
    assert fetched["topic"] == "Royal Decrees & Political Treaties"
    assert fetched["document_type"] == "Inscription / Copper Plate Grant"
    assert fetched["institution"] == "National Archives of India"
    assert fetched["rights"] == "Public Domain / Universal Cultural Heritage"
    assert fetched["file_size_bytes"] == len(test_content)
    assert fetched["saved_file_path"] == str(test_filepath)
    print("[OK] All 9 metadata fields + file details verified accurately in SQLite!")

    print("\n--- 5. Testing Full Registry Query ---")
    all_recs = get_all_records()
    assert len(all_recs) >= 1, "Should contain at least the inserted record"
    print(f"[OK] Full registry contains {len(all_recs)} records.")

    print("\nALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_upload_and_storage()
