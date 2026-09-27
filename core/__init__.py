# Core modules initialization
"""
Digital Heritage Archive - Core Engines
Contains modular subsystems for image preprocessing, OCR, metadata cataloging,
vector search, RAG, translation, TTS, and timeline generation.
"""

from .translator import HeritageTranslator, DEMO_LANGUAGES, ALL_LANGUAGES, translate_text, get_supported_languages, get_all_languages
from .tts_engine import TTSEngine, render_interactive_audio_player, get_web_speech_html, render_tts_studio, LANG_MAPPINGS

