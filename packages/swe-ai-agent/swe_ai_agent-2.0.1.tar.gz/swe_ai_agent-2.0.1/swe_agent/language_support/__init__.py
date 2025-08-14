"""
Language Support module for the Agentic IDE.
Provides language detection, analysis, and editing capabilities.
"""

from .detector import LanguageDetector
from .analyzers import get_language_analyzer
from .editors import get_language_editor
from .runners import get_language_runner

__all__ = ['LanguageDetector', 'get_language_analyzer', 'get_language_editor', 'get_language_runner']