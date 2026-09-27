"""
Digital Heritage Archive - Text Cleaning Engine
Standardizes OCR transcripts, strips digitization noise, repairs broken lines,
and performs Unicode normalization for Indic, Persian, Arabic, and Latin historical texts.
"""

import unicodedata
import re
from typing import Dict, Any


class TextCleaner:
    """Provides rule-based and linguistic sanitization for historical OCR transcripts."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Applies NFKC Unicode normalization for standardized glyph representations."""
        if not text:
            return ""
        return unicodedata.normalize("NFKC", text)

    @staticmethod
    def remove_ocr_artifacts(text: str) -> str:
        """
        Removes typical OCR scanning artifacts such as stray punctuation patterns,
        repeated non-alphanumeric noise, and broken formatting characters.
        """
        if not text:
            return ""

        # Remove long sequences of symbols (e.g. ~~~~, =====, _______)
        cleaned = re.sub(r"[\~\|\_\^\*\#\=\+\-\<\>]{3,}", " ", text)

        # Fix hyphenated line breaks (e.g. "archaeo- \n logy" -> "archaeology")
        cleaned = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", cleaned)

        # Replace excessive multiple line breaks with double newlines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # Normalize multiple spaces into single spaces
        cleaned = re.sub(r"[ \t]+", " ", cleaned)

        # Strip unprintable control characters except newline & tab
        cleaned = "".join(ch for ch in cleaned if ch == "\n" or ch == "\t" or unicodedata.category(ch)[0] != "C")

        return cleaned.strip()

    @classmethod
    def clean(cls, raw_text: str) -> Dict[str, Any]:
        """
        Runs the full text cleaning pipeline.
        Returns cleaned text along with cleaning metrics.
        """
        if not raw_text:
            return {
                "cleaned_text": "",
                "original_char_count": 0,
                "cleaned_char_count": 0,
                "reduction_percentage": 0.0,
            }

        normalized = cls.normalize_unicode(raw_text)
        cleaned = cls.remove_ocr_artifacts(normalized)

        orig_len = len(raw_text)
        clean_len = len(cleaned)
        diff_ratio = round(((orig_len - clean_len) / orig_len) * 100, 2) if orig_len > 0 else 0.0

        return {
            "cleaned_text": cleaned,
            "original_char_count": orig_len,
            "cleaned_char_count": clean_len,
            "reduction_percentage": diff_ratio,
        }

    @classmethod
    def clean_ocr_text(cls, raw_text: str) -> str:
        """Cleans raw OCR text and directly returns the normalized string."""
        res = cls.clean(raw_text)
        return res.get("cleaned_text", "")

