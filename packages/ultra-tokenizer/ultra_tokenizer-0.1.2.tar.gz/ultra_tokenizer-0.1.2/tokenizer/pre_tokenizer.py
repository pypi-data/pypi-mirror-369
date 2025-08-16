"""
Pre-tokenization utilities

This module contains the PreTokenizer class that handles text normalization
and pre-processing before tokenization.
"""

from typing import List, Optional
import regex as re
import unicodedata
import logging

logger = logging.getLogger(__name__)


class PreTokenizer:
    """Pre-tokenization utilities."""

    def __init__(self):
        """Initialize pre-tokenizer."""
        # Pre-compiled regex patterns
        self.url_pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
        self.email_pattern = re.compile(r"[\w.-]+@[\w.-]+")
        self.num_pattern = re.compile(r"\d+(?:\.\d+)?")
        self.special_char_pattern = re.compile(r"[^\w\s]")

    def pre_tokenize(self, text: str) -> str:
        """Apply pre-tokenization rules to text.

        Args:
            text: Input text to pre-tokenize

        Returns:
            Pre-tokenized text
        """
        if not text:
            return ""

        # Normalize whitespace
        text = self._normalize_whitespace(text)

        # Handle special tokens
        text = self._handle_special_tokens(text)

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def _handle_special_tokens(self, text: str) -> str:
        """Handle special tokens like URLs, emails, and numbers."""
        # Replace URLs with [URL] token
        text = self.url_pattern.sub("[URL]", text)
        # Replace emails with [EMAIL] token
        text = self.email_pattern.sub("[EMAIL]", text)
        # Replace numbers with [NUM] token
        text = self.num_pattern.sub("[NUM]", text)
        return text
