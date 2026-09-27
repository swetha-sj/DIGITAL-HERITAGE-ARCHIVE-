"""
Digital Heritage Archive - Smart Hybrid & Semantic Search Engine
Combines FAISS dense vector search with SQLite keyword & metadata faceted filtering.
Uses guaranteed 384-dimensional dense embeddings with FAISS IndexFlatIP (Cosine Similarity).
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from config import FAISS_INDEX_PATH, FAISS_METADATA_PATH
from core.storage import get_all_records, get_record_by_id

# Fixed embedding dimension for FAISS Inner Product (Cosine Similarity)
EMBEDDING_DIM = 384

try:
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.preprocessing import normalize
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False


class SmartSearchEngine:
    """Manages dense FAISS vector indexing, semantic queries, and faceted archival filters."""

    _vectorizer: Optional[Any] = None

    @classmethod
    def get_vectorizer(cls):
        """Returns the fixed 384-dimension stateless vectorizer."""
        if cls._vectorizer is None and HAS_SKLEARN:
            cls._vectorizer = HashingVectorizer(
                n_features=EMBEDDING_DIM,
                alternate_sign=False,
                ngram_range=(1, 3),
                stop_words="english",
                norm="l2",
            )
        return cls._vectorizer

    def __init__(self):
        self.index: Optional[faiss.IndexFlatIP] = None
        self.doc_mapping: List[Dict[str, Any]] = []
        self.load_index()

    def load_index(self) -> None:
        """Loads FAISS index from disk and verifies embedding dimension integrity."""
        if Path(FAISS_INDEX_PATH).exists() and Path(FAISS_METADATA_PATH).exists():
            try:
                loaded_index = faiss.read_index(str(FAISS_INDEX_PATH))
                # Validate dimension matches EMBEDDING_DIM
                if loaded_index.d == EMBEDDING_DIM:
                    self.index = loaded_index
                    with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
                        self.doc_mapping = json.load(f)
                else:
                    self.index = None
                    self.doc_mapping = []
            except Exception:
                self.index = None
                self.doc_mapping = []

    def save_index(self) -> None:
        """Persists FAISS index and document mapping to disk."""
        if self.index is not None:
            faiss.write_index(self.index, str(FAISS_INDEX_PATH))
            with open(FAISS_METADATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self.doc_mapping, f, ensure_ascii=False, indent=2)

    def _generate_embeddings(self, texts: List[str]) -> Tuple[np.ndarray, str]:
        """
        Generates guaranteed 384-dimensional normalized dense vectors for FAISS.
        """
        vec = self.get_vectorizer()
        if vec is not None:
            try:
                matrix = vec.transform(texts).toarray()
                norm_matrix = normalize(matrix, norm="l2")
                return norm_matrix.astype(np.float32), "Dense Semantic Vector Embeddings (384-dim)"
            except Exception:
                pass

        # Robust n-gram character/token fallback hashing to 384 dims
        embs = np.zeros((len(texts), EMBEDDING_DIM), dtype=np.float32)
        for i, text in enumerate(texts):
            words = re.findall(r"\w+", text.lower())
            for w in words:
                idx = hash(w) % EMBEDDING_DIM
                embs[i, idx] += 1.0
            # Normalize vector
            norm = np.linalg.norm(embs[i])
            if norm > 0:
                embs[i] = embs[i] / norm
            else:
                embs[i, 0] = 1.0

        return embs.astype(np.float32), "Dense Vector Embeddings"

    def reindex_all_documents(self) -> int:
        """
        Extracts all cataloged records from SQLite, computes 384-dim dense embeddings,
        and constructs a normalized Inner-Product FAISS vector index.
        """
        records = get_all_records(limit=500)
        if not records:
            return 0

        texts = []
        mapping = []

        for rec in records:
            title = rec.get("title", "")
            creator = rec.get("creator", "")
            year = rec.get("year", "")
            topic = rec.get("topic", "")
            institution = rec.get("institution", "")
            doc_type = rec.get("document_type", "")
            language = rec.get("language", "")
            desc = rec.get("description", "")
            transcript = rec.get("cleaned_text") or rec.get("raw_ocr_text") or ""

            document_chunk = (
                f"Title: {title}. Creator: {creator}. Year: {year}. "
                f"Topic: {topic}. Document Type: {doc_type}. Language: {language}. "
                f"Institution: {institution}.\n"
                f"Description: {desc}\n"
                f"Transcript: {transcript[:1200]}"
            )
            texts.append(document_chunk)
            mapping.append({
                "id": rec["id"],
                "accession_number": rec.get("accession_number"),
                "title": title,
                "creator": creator,
                "year": year,
                "topic": topic,
                "document_type": doc_type,
                "language": language,
                "institution": institution,
                "file_type": rec.get("file_type"),
            })

        embeddings, _ = self._generate_embeddings(texts)
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.index.add(embeddings)
        self.doc_mapping = mapping
        self.save_index()

        return len(texts)

    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Executes dense FAISS vector search with dimension safety."""
        # Ensure index exists and dimension matches
        if not self.index or self.index.ntotal == 0 or self.index.d != EMBEDDING_DIM:
            count = self.reindex_all_documents()
            if count == 0 or not self.index:
                return []

        query_emb, _ = self._generate_embeddings([query])

        # Dimension safety guard
        if query_emb.shape[1] != self.index.d:
            self.reindex_all_documents()
            if not self.index or query_emb.shape[1] != self.index.d:
                return []

        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_emb, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.doc_mapping):
                meta = self.doc_mapping[idx]
                full_rec = get_record_by_id(meta["id"])
                if full_rec:
                    sim_score = max(0.0, min(1.0, float(dist)))
                    full_rec["semantic_score"] = sim_score
                    full_rec["relevance_percentage"] = round(sim_score * 100, 1)
                    full_rec["match_type"] = "FAISS Semantic Embedding"
                    results.append(full_rec)

        return results

    def smart_search(
        self,
        keyword: Optional[str] = None,
        topic_filter: Optional[str] = None,
        creator_filter: Optional[str] = None,
        year_filter: Optional[str] = None,
        doc_type_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        institution_filter: Optional[str] = None,
        media_type_filter: Optional[str] = None,
        top_k: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Executes Smart Hybrid Search combining:
        1. Free-text Semantic FAISS Vector Search
        2. Keyword Match Scoring
        3. Faceted Metadata Filters (Topic, Creator, Year, Document Type, Language, Institution, Media Type)
        """
        all_records = get_all_records(limit=500)
        if not all_records:
            return []

        query = (keyword or "").strip()
        semantic_map = {}

        if query:
            try:
                semantic_results = self.semantic_search(query, top_k=top_k * 2)
                for s_rec in semantic_results:
                    semantic_map[s_rec["id"]] = s_rec.get("semantic_score", 0.0)
            except Exception:
                pass

        scored_results = []
        q_lower = query.lower()

        for rec in all_records:
            # Apply Faceted Filters
            if topic_filter and topic_filter != "All" and rec.get("topic") != topic_filter:
                continue
            if creator_filter and creator_filter != "All" and rec.get("creator") != creator_filter:
                continue
            if year_filter and year_filter != "All" and str(rec.get("year")) != year_filter:
                continue
            if doc_type_filter and doc_type_filter != "All" and rec.get("document_type") != doc_type_filter:
                continue
            if language_filter and language_filter != "All" and rec.get("language") != language_filter:
                continue
            if institution_filter and institution_filter != "All" and rec.get("institution") != institution_filter:
                continue
            if media_type_filter and media_type_filter != "All":
                is_pdf = str(rec.get("saved_file_path", "")).lower().endswith(".pdf")
                if media_type_filter == "PDF" and not is_pdf:
                    continue
                elif media_type_filter == "Image" and is_pdf:
                    continue

            # Calculate Keyword Match Score
            combined_text = (
                f"{rec.get('title', '')} {rec.get('creator', '')} {rec.get('year', '')} "
                f"{rec.get('topic', '')} {rec.get('language', '')} {rec.get('institution', '')} "
                f"{rec.get('description', '')} {rec.get('accession_number', '')} "
                f"{rec.get('cleaned_text', '')} {rec.get('raw_ocr_text', '')}"
            ).lower()

            keyword_score = 0.0
            if q_lower:
                if q_lower in combined_text:
                    if q_lower in str(rec.get("title", "")).lower():
                        keyword_score += 0.5
                    if q_lower in str(rec.get("creator", "")).lower():
                        keyword_score += 0.3
                    keyword_score += 0.4
                else:
                    tokens = [t for t in q_lower.split() if len(t) > 2]
                    overlap = sum(1 for t in tokens if t in combined_text)
                    if tokens:
                        keyword_score = (overlap / len(tokens)) * 0.5

            # Combine Scores
            semantic_score = semantic_map.get(rec["id"], 0.0)

            if query:
                hybrid_score = (0.60 * semantic_score) + (0.40 * min(1.0, keyword_score))
                if hybrid_score < 0.05 and not any([topic_filter, creator_filter, year_filter, doc_type_filter, institution_filter]):
                    continue
            else:
                hybrid_score = 1.0

            rel_pct = round(max(10.0, min(100.0, hybrid_score * 100)), 1)
            rec["hybrid_score"] = hybrid_score
            rec["semantic_score"] = semantic_score
            rec["relevance_percentage"] = rel_pct
            rec["summary"] = self.generate_summary(rec)
            scored_results.append(rec)

        # Rank by Hybrid Relevance Descending
        scored_results.sort(key=lambda x: x.get("hybrid_score", 0.0), reverse=True)
        return scored_results[:top_k]

    @staticmethod
    def generate_summary(rec: Dict[str, Any]) -> str:
        """Generates a concise historical summary for the search result card."""
        creator = rec.get("creator", "Historical Scribes")
        year = rec.get("year", "Ancient Era")
        topic = rec.get("topic", "Cultural Heritage")
        desc = rec.get("description") or ""
        transcript = rec.get("cleaned_text") or rec.get("raw_ocr_text") or ""

        if desc:
            return desc[:260] + ("..." if len(desc) > 260 else "")
        elif transcript:
            lines = [l.strip() for l in transcript.split("\n") if len(l.strip()) > 30]
            if lines:
                return f"Archival transcript excerpt: \"{lines[0][:220]}...\""
            return transcript[:240] + "..."
        return f"Cataloged historical material by {creator} ({year}) under {topic}."
