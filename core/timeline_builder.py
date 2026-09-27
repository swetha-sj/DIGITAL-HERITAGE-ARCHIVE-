"""
Digital Heritage Archive - Interactive Historical Heritage Timeline Builder
Builds chronological timelines mapping historical manuscripts, decrees, speeches,
and cultural records across millennia with multi-attribute category filtering:
All, Life, Writings, Speeches, Constitution, Legacy.
"""

import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from core.storage import get_all_records

TIMELINE_CATEGORIES = [
    "All",
    "Life",
    "Writings",
    "Speeches",
    "Constitution",
    "Legacy",
]

CATEGORY_ICONS = {
    "All": "🌐",
    "Life": "👑",
    "Writings": "✍️",
    "Speeches": "🎙️",
    "Constitution": "📜",
    "Legacy": "🏛️",
}

CATEGORY_COLORS = {
    "Life": "#ec4899",         # Rose / Pink
    "Writings": "#3b82f6",     # Sapphire / Blue
    "Speeches": "#f59e0b",     # Amber / Gold
    "Constitution": "#10b981", # Emerald / Green
    "Legacy": "#8b5cf6",       # Royal Purple
}


class TimelineBuilder:
    """Constructs structured timeline data and interactive Plotly visual charts."""

    @staticmethod
    def parse_chronological_year(year_str: str) -> float:
        """
        Parses historical year strings (e.g. '257 BCE', '320 BC', '1582 CE', '1949', '1942-08-08')
        into a continuous numerical timeline float (BCE = negative, CE = positive).
        """
        if not year_str or not str(year_str).strip():
            return 1000.0

        raw = str(year_str).strip().upper()
        
        # Check if BCE / BC
        is_bce = "BCE" in raw or "BC" in raw or "B.C." in raw

        # Extract digits
        digits_match = re.search(r"(\d{1,4})", raw)
        if digits_match:
            num = float(digits_match.group(1))
            return -num if is_bce else num

        return 1000.0

    @staticmethod
    def classify_category(doc: Dict[str, Any]) -> str:
        """
        Classifies an archival record into one of: Life, Writings, Speeches, Constitution, Legacy.
        """
        # 1. Direct tag check
        explicit_cat = str(doc.get("category") or "").strip()
        for cat in ["Life", "Writings", "Speeches", "Constitution", "Legacy"]:
            if cat.lower() == explicit_cat.lower():
                return cat

        combined_text = (
            f"{doc.get('title') or ''} {doc.get('topic') or ''} {doc.get('document_type') or ''} "
            f"{doc.get('description') or ''} {(doc.get('cleaned_text') or '')[:300]}"
        ).lower()

        # 2. Constitution / Legal Charters / Farmans / Edicts of Law
        if any(w in combined_text for w in [
            "constitution", "preamble", "fundamental rights", "farman", "decree",
            "treaty", "legal charter", "ordinance", "statute", "sulh-i-kul",
            "tax exemption", "law", "directive principles", "proclamation of law"
        ]):
            return "Constitution"

        # 3. Speeches / Edicts of Speech / Oral Proclamations
        if any(w in combined_text for w in [
            "speech", "address", "oral", "rock edict xii", "speech restraint",
            "gowalia tank", "tryst with destiny", "proclamation", "bulletin",
            "broadcast", "oration", "audio", "video", "interview", "testimony"
        ]):
            return "Speeches"

        # 4. Writings / Manuscripts / Treatises / Epics / Letters
        if any(w in combined_text for w in [
            "manuscript", "treatise", "arthashastra", "chronicle", "book",
            "essay", "epic", "literary", "writing", "letter", "commentary",
            "baburnama", "harshacharita", "palm-leaf", "birch bark"
        ]):
            return "Writings"

        # 5. Life / Milestones / Coronation / Reign / Biography
        if any(w in combined_text for w in [
            "coronation", "birth", "biography", "accession", "life of",
            "genealogy", "conquest", "allahabad pillar", "samudragupta",
            "harsha", "monarch", "dynasty founder", "personal"
        ]):
            return "Life"

        # 6. Legacy / Monuments / Endowments / Conservation / Temple Grants
        if any(w in combined_text for w in [
            "copper plate grant", "temple", "brihadisvara", "endowment",
            "legacy", "monument", "sanchi", "conservation", "asi",
            "heritage", "preservation", "inscription"
        ]):
            return "Legacy"

        return "Writings"

    @staticmethod
    def extract_historical_event(doc: Dict[str, Any], category: str) -> str:
        """Generates a concise Historical Event / Record headline."""
        title = doc.get("title", "")
        creator = doc.get("creator", "Historical Scribe")
        year = doc.get("year", "Historical Era")

        if "Ashoka" in title or "Ashoka" in creator:
            return "Proclamation of Moral Law & Universal Concord"
        elif "Akbar" in title or "Akbar" in creator:
            return "Imperial Decree on Universal Peace (Sulh-i-Kul)"
        elif "Chola" in title or "Rajaraja" in creator:
            return "Royal Epigraphic Temple Endowment"
        elif "Quit India" in title:
            return "National Proclamation for Civil Resistance"
        elif "Samudragupta" in title or "Harishena" in creator:
            return "Epigraphic Record of Gupta Imperial Conquests"
        elif "Harsha" in title:
            return "Royal Copper Plate Grant & Monastery Charter"
        elif "Constitution" in title:
            return "Adoption of the Sovereign Constitution of India"
        
        event_prefixes = {
            "Life": "Biographical & Reign Milestone",
            "Writings": "Scholarly Archival Treatise",
            "Speeches": "Historic Public Address & Edict",
            "Constitution": "Sovereign Charter & Decree",
            "Legacy": "Preservation & Endowed Heritage Record",
        }
        return f"{event_prefixes.get(category, 'Historical Milestone')} ({creator})"

    @classmethod
    def get_timeline_records(cls, category_filter: str = "All", search_query: str = "") -> List[Dict[str, Any]]:
        """
        Extracts, classifies, standardizes, and sorts all archival records chronologically.
        """
        raw_docs = get_all_records(limit=200)
        items = []

        for doc in raw_docs:
            category = cls.classify_category(doc)
            plot_year = cls.parse_chronological_year(doc.get("year", "1000"))
            event_name = cls.extract_historical_event(doc, category)
            description = doc.get("description") or doc.get("cleaned_text") or "Archival heritage document."
            
            # Create a clean short description (1-2 sentences)
            short_desc = description.strip()
            if len(short_desc) > 220:
                short_desc = short_desc[:215] + "..."

            item = {
                "id": doc["id"],
                "record_id": doc["id"],
                "year": doc.get("year", "Historical Era"),
                "plot_year": plot_year,
                "historical_event": event_name,
                "title": doc.get("title", "Archival Document"),
                "short_description": short_desc,
                "full_description": description,
                "category": category,
                "category_icon": CATEGORY_ICONS.get(category, "📜"),
                "category_color": CATEGORY_COLORS.get(category, "#fbbf24"),
                "creator": doc.get("creator", "Historical Scribe"),
                "institution": doc.get("institution", "National Heritage Archive"),
                "accession_number": doc.get("accession_number", f"DHA-{doc['id']:03d}"),
                "rights": doc.get("rights", "Universal Cultural Heritage"),
                "document_type": doc.get("document_type", "Manuscript"),
                "language": doc.get("language", "Classical Script"),
                "saved_file_path": doc.get("saved_file_path"),
                "processed_file_path": doc.get("processed_file_path"),
                "cleaned_text": doc.get("cleaned_text") or doc.get("raw_ocr_text") or "",
            }
            items.append(item)

        # Sort chronologically by continuous numerical year
        items.sort(key=lambda x: x["plot_year"])

        # Apply category filter
        if category_filter and category_filter != "All":
            items = [it for it in items if it["category"].lower() == category_filter.lower()]

        # Apply search query filter
        if search_query and search_query.strip():
            sq = search_query.lower().strip()
            items = [
                it for it in items
                if sq in it["title"].lower()
                or sq in it["historical_event"].lower()
                or sq in it["short_description"].lower()
                or sq in it["creator"].lower()
                or sq in it["year"].lower()
                or sq in it["accession_number"].lower()
            ]

        return items

    @classmethod
    def get_timeline_dataframe(cls, category_filter: str = "All") -> pd.DataFrame:
        """Returns a standardized pandas DataFrame for timeline visualization."""
        records = cls.get_timeline_records(category_filter=category_filter)
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    @classmethod
    def build_plotly_timeline(cls, items: List[Dict[str, Any]], selected_category: str = "All") -> Optional[go.Figure]:
        """
        Creates an interactive Plotly timeline scatter chart with rich custom hovercards.
        """
        if not items:
            return None

        df = pd.DataFrame(items)

        fig = px.scatter(
            df,
            x="plot_year",
            y="category",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
            size=[24] * len(df),
            hover_name="title",
            custom_data=["year", "historical_event", "creator", "institution", "accession_number", "short_description"],
            title=f"🏛️ Interactive Heritage Timeline ({selected_category}) — Chronological Distribution",
            template="plotly_dark",
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br><br>"
                "📅 <b>Year / Era:</b> %{customdata[0]}<br>"
                "🏛️ <b>Event / Record:</b> %{customdata[1]}<br>"
                "👑 <b>Creator:</b> %{customdata[2]}<br>"
                "🏛️ <b>Institution:</b> %{customdata[3]}<br>"
                "🆔 <b>Accession:</b> %{customdata[4]}<br>"
                "📝 <b>Summary:</b> %{customdata[5]}<extra></extra>"
            ),
            marker=dict(
                line=dict(width=2, color="#fbbf24"),
                symbol="diamond",
                opacity=0.9,
            ),
        )

        fig.update_layout(
            xaxis_title="Chronological Year (Negative = BCE, Positive = CE)",
            yaxis_title="Archival Theme",
            legend_title="Thematic Category",
            height=360,
            margin=dict(l=40, r=40, t=50, b=40),
            plot_bgcolor="rgba(15, 23, 42, 0.7)",
            paper_bgcolor="rgba(15, 23, 42, 0.0)",
            font=dict(color="#f1f5f9"),
            hoverlabel=dict(
                bgcolor="rgba(15, 23, 42, 0.95)",
                bordercolor="#fbbf24",
                font_size=12,
                font_family="Inter",
            ),
        )

        return fig
