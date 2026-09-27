"""
Digital Heritage Archive - Dublin Core & Archival Metadata Schema
Defines data models and schema validation adhering to international cultural heritage standards.
"""

from typing import Optional, Dict, Any, List
import uuid


class DublinCoreMetadata:
    """
    Data model based on Dublin Core Metadata Element Set (ISO 15836)
    enhanced with specific cultural heritage archival fields.
    """

    def __init__(
        self,
        title: str,
        era: str,
        category: str,
        accession_number: Optional[str] = None,
        preservation_condition: str = "Pristine / Well Preserved",
        dynasty_period: Optional[str] = None,
        approx_year: Optional[str] = None,
        origin_region: Optional[str] = None,
        author_creator: Optional[str] = None,
        donor_source: Optional[str] = None,
        rights_status: str = "Public Domain / Cultural Heritage",
        language: str = "en",
        tags: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.title = title.strip()
        self.era = era
        self.category = category
        self.accession_number = accession_number or f"DHA-{uuid.uuid4().hex[:8].upper()}"
        self.preservation_condition = preservation_condition
        self.dynasty_period = dynasty_period or "Unspecified"
        self.approx_year = approx_year or "Circa Unknown"
        self.origin_region = origin_region or "India"
        self.author_creator = author_creator or "Unknown Scribe / Artisan"
        self.donor_source = donor_source or "National Heritage Trust"
        self.rights_status = rights_status
        self.language = language
        self.tags = tags or ""
        self.custom_metadata = custom_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Converts metadata to dictionary representation."""
        return {
            "title": self.title,
            "era": self.era,
            "category": self.category,
            "accession_number": self.accession_number,
            "preservation_condition": self.preservation_condition,
            "dynasty_period": self.dynasty_period,
            "approx_year": self.approx_year,
            "origin_region": self.origin_region,
            "author_creator": self.author_creator,
            "donor_source": self.donor_source,
            "rights_status": self.rights_status,
            "language": self.language,
            "tags": self.tags,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> List[str]:
        """Validates that mandatory Dublin Core fields are provided."""
        errors = []
        if not data.get("title"):
            errors.append("Document Title is mandatory.")
        if not data.get("era"):
            errors.append("Historical Era is mandatory.")
        if not data.get("category"):
            errors.append("Archival Category is mandatory.")
        return errors
